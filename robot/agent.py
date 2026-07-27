"""Autonomous research robot driving Claude.ai via the AI Browser Bridge.

Loop:
  for each subject in goals.txt:
    1. open a fresh Claude.ai chat
    2. seed with subject, ask for an answer + NEXT: follow-up line
    3. for N turns: parse NEXT: from response, send it back, wait, journal
    4. ask for a synthesis brief, save to syntheses/<subject>.md
    5. once goals queue is low, ask Claude itself to propose more subjects
  Stop conditions: STOP file appears, max_total_turns reached, fatal error.

Run:    python C:\\Users\\EC\\robot\\agent.py
Stop:   create C:\\Users\\EC\\robot\\STOP (e.g. `New-Item STOP`); the robot
        finishes the current turn and exits cleanly.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\EC\robot")
BRIDGE = "http://127.0.0.1:17777"
CONFIG_PATH = ROOT / "config.json"
STATE_PATH = ROOT / "state.json"
GOALS_PATH = ROOT / "goals.txt"
LOG_PATH = ROOT / "agent.log"
STOP_PATH = ROOT / "STOP"
JOURNAL_DIR = ROOT / "journal"
SYNTH_DIR = ROOT / "syntheses"

DEFAULT_CONFIG = {
    "auth_token": "138c03e372fe620c6ed6fb3589dede86",
    "cadence_seconds": 30,
    "turns_per_subject": 8,
    "response_initial_wait_seconds": 20,
    "max_response_wait_seconds": 90,
    "stable_text_polls": 3,
    "poll_interval_seconds": 3,
    "max_total_turns": 5000,
    "min_goals_remaining": 3,
    "extend_goals_by": 5,
    "error_backoff_seconds": 60,
}

DEFAULT_GOALS = [
    "Diversity regularizers for small mixture-of-experts ensembles (5-10 experts)",
    "Calibration of softmax outputs and how to measure expected calibration error",
    "Distillation from large to small models: which signals transfer best",
    "RAG retrieval ranking: BM25 vs dense vs hybrid trade-offs in 2025",
    "Loss landscape geometry as a predictor of generalization",
    "Inductive biases in small transformers vs convnets at sub-1B scale",
    "Low-resource translation strategies for Irish (Gaeilge)",
    "Base L2 blockchain consensus and finality models",
    "Mechanistic interpretability: what we actually know about attention heads",
    "Speculative decoding and self-speculation: when it helps vs hurts latency",
]

TAG_FMT = "(trace-{id})"
NEXT_MARKER = "NEXT:"


def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def keep_awake():
    """Block system/display sleep for the life of this process (Windows).

    Uses SetThreadExecutionState with ES_CONTINUOUS, so the request persists
    until the process exits (or clears it), at which point Windows restores
    normal power behaviour automatically. This prevents the overnight-run
    failure where the box sleeps mid-turn and the bridge scrapes an empty /
    suspended page.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        res = ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        if res == 0:
            log("keep-awake: SetThreadExecutionState returned 0 (not applied)")
        else:
            log("keep-awake enabled (system + display sleep blocked for this run)")
    except Exception as e:
        log(f"keep-awake unavailable: {e!r}")


def bridge_post(action, args, token, timeout=40):
    body = json.dumps({"action": action, "args": args}).encode("utf-8")
    req = urllib.request.Request(
        f"{BRIDGE}/command",
        data=body,
        headers={"Content-Type": "application/json", "X-Auth-Token": token},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError(f"bridge error ({action}): {payload.get('error')}")
    return payload.get("result", {})


def bridge_get(path, timeout=10):
    with urllib.request.urlopen(f"{BRIDGE}{path}", timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def preflight(token):
    if not bridge_get("/health").get("ok"):
        raise RuntimeError("bridge /health not ok")
    status = bridge_get("/status")
    poll = status.get("extension_last_poll_seconds_ago")
    if poll is None or poll > 30:
        raise RuntimeError(f"extension not connected (last poll: {poll})")
    log(f"preflight ok (extension poll {poll:.1f}s ago)")


def ensure_claude_tab(token):
    tabs = bridge_post("list_tabs", {}, token).get("tabs", [])
    claude = [t for t in tabs if "claude.ai" in (t.get("url") or "")]
    if claude:
        active = next((t for t in claude if t.get("active")), None)
        if active:
            return
        bridge_post("switch_tab", {"tab_id": claude[0]["id"]}, token)
        time.sleep(2)
        return
    bridge_post("navigate", {"url": "https://claude.ai/new"}, token)
    time.sleep(5)


def navigate_new_chat(token):
    bridge_post("navigate", {"url": "https://claude.ai/new"}, token)
    time.sleep(4)
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            bridge_post("wait_for",
                        {"selector": "div.ProseMirror", "timeout_ms": 5000},
                        token)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("new chat input never appeared")


def send_prompt(token, text):
    bridge_post("click", {"selector": "div.ProseMirror"}, token)
    bridge_post("type",
                {"selector": "div.ProseMirror", "text": text, "submit": False},
                token)
    bridge_post("press",
                {"selector": "div.ProseMirror", "key": "Enter"},
                token)


def clean_response_tail(tail):
    m = re.search(r"Claude responded:.*?\n\s*\n", tail, re.DOTALL)
    if m:
        tail = tail[m.end():]
    for footer in (
        "Claude is AI and can make mistakes",
        "Claude works directly with your codebase",
        "Claude Fable",
        "\nShare\n",
        "Sonnet 4.6 Low",
        "Sonnet 4.6",
    ):
        j = tail.find(footer)
        if j > 0:
            tail = tail[:j]
    return tail.strip()


def wait_for_response(token, prompt_tag, cfg):
    time.sleep(cfg["response_initial_wait_seconds"])
    deadline = time.time() + cfg["max_response_wait_seconds"]
    last = ""
    stable = 0
    while time.time() < deadline:
        try:
            body = bridge_post("get_text", {"selector": "body"}, token).get("text", "")
        except Exception as e:
            log(f"get_text error: {e!r}")
            time.sleep(cfg["poll_interval_seconds"])
            continue
        idx = body.rfind(prompt_tag)
        if idx >= 0:
            cleaned = clean_response_tail(body[idx + len(prompt_tag):])
            if cleaned and cleaned == last and len(cleaned) > 80:
                stable += 1
                if stable >= cfg["stable_text_polls"]:
                    return cleaned
            else:
                stable = 0
                last = cleaned
        time.sleep(cfg["poll_interval_seconds"])
    return last


def extract_next(response_text):
    if not response_text:
        return None
    m = re.search(rf"{re.escape(NEXT_MARKER)}\s*(.+?)\s*$", response_text,
                  re.MULTILINE)
    if m:
        q = m.group(1).strip().strip("'\"`")
        if 8 < len(q) < 500:
            return q
    return None


SEED_TEMPLATE = (
    "Topic: {subject}\n\n"
    "We are about to explore this across several turns. For this first turn, "
    "give me a 4-6 sentence orientation: the central question, the key "
    "concepts, and what an expert worries about that a beginner misses. "
    "Be concrete and avoid platitudes.\n\n"
    "At the very end, on its own line starting with 'NEXT:', write the single "
    "sharpest follow-up question a teacher would ask next. Do not mention or "
    "quote the trace token. {tag}"
)
FOLLOWUP_TEMPLATE = (
    "{question}\n\n"
    "Answer in 4-7 sentences. Be concrete; cite specific systems, papers, or "
    "numbers where useful. At the very end, on its own line starting with "
    "'NEXT:', write your single sharpest non-obvious follow-up question, "
    "different from any we have asked before. Do not mention the trace token. "
    "{tag}"
)
SYNTH_TEMPLATE = (
    "Synthesize everything we have covered about '{subject}' as a self-"
    "contained 400-700 word markdown brief. Structure: a top-line thesis "
    "sentence, 3-5 key insights with one-paragraph explanations each, a "
    "'Common pitfalls' subsection, and one 'Open question for deeper work' "
    "subsection. Start the document with '# {subject}'. Do not include the "
    "trace token in the brief. {tag}"
)
EXTEND_GOALS_TEMPLATE = (
    "Propose {n} sharp, well-scoped research subjects worth a multi-turn "
    "deep dive, in machine learning systems, applied AI, or adjacent "
    "engineering. Each on its own line, no numbering, no commentary, just "
    "the subject phrase. Different from these recent ones: {recent}. {tag}"
)


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_goals():
    if not GOALS_PATH.exists():
        GOALS_PATH.write_text("\n".join(DEFAULT_GOALS) + "\n", encoding="utf-8")
    lines = [l.strip() for l in GOALS_PATH.read_text(encoding="utf-8").splitlines()]
    return [l for l in lines if l and not l.startswith("#")]


def append_goals(new_goals):
    with open(GOALS_PATH, "a", encoding="utf-8") as f:
        for g in new_goals:
            f.write(g + "\n")


def safe_filename(s):
    s = re.sub(r"[^\w\- ]+", "", s)
    return s.strip().replace(" ", "_")[:80] or "subject"


def run_subject(token, cfg, state, subject):
    log(f"subject [{state['subject_index']}] '{subject}' starting")
    chat_file = JOURNAL_DIR / (
        datetime.now().strftime("%Y%m%d_%H%M%S") + "_" +
        safe_filename(subject) + ".jsonl"
    )
    navigate_new_chat(token)
    try:
        state["chat_url"] = bridge_post("get_url", {}, token).get("url")
    except Exception:
        state["chat_url"] = None
    save_json(STATE_PATH, state)

    next_q = None
    for turn in range(cfg["turns_per_subject"]):
        if STOP_PATH.exists():
            return
        turn_id = state["total_turns"] + 1
        tag = TAG_FMT.format(id=turn_id)
        if turn == 0:
            prompt = SEED_TEMPLATE.format(subject=subject, tag=tag)
        else:
            q = next_q or f"Tell me one specific, non-obvious fact about {subject}."
            prompt = FOLLOWUP_TEMPLATE.format(question=q, tag=tag)
        send_prompt(token, prompt)
        response = wait_for_response(token, tag, cfg)
        if len(response) < 80:
            log(f"turn {turn_id} short/empty response ({len(response)} chars); skipping")
        record = {
            "turn_id": turn_id,
            "subject_index": state["subject_index"],
            "subject": subject,
            "turn_in_subject": turn,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "response": response,
        }
        with open(chat_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        next_q = extract_next(response)
        state["total_turns"] = turn_id
        state["turn_in_subject"] = turn + 1
        save_json(STATE_PATH, state)
        log(f"turn {turn_id} ok ({len(response)} chars) next={(next_q or '<none>')[:70]}")
        time.sleep(cfg["cadence_seconds"])

    # Synthesis turn
    turn_id = state["total_turns"] + 1
    tag = TAG_FMT.format(id=turn_id)
    send_prompt(token, SYNTH_TEMPLATE.format(subject=subject, tag=tag))
    synth = wait_for_response(token, tag, cfg)
    if synth and len(synth) > 100:
        path = SYNTH_DIR / (safe_filename(subject) + ".md")
        path.write_text(synth, encoding="utf-8")
        log(f"synthesis written: {path.name} ({len(synth)} chars)")
    else:
        log(f"synthesis too short ({len(synth)} chars); skipping write")
    state["total_turns"] = turn_id
    state["subject_index"] += 1
    state["turn_in_subject"] = 0
    save_json(STATE_PATH, state)
    time.sleep(cfg["cadence_seconds"])


def extend_goals_via_claude(token, cfg, recent):
    tag = TAG_FMT.format(id=f"ext-{int(time.time())}")
    navigate_new_chat(token)
    prompt = EXTEND_GOALS_TEMPLATE.format(
        n=cfg["extend_goals_by"],
        recent="; ".join(recent),
        tag=tag,
    )
    send_prompt(token, prompt)
    resp = wait_for_response(token, tag, cfg)
    lines = []
    for raw in resp.splitlines():
        l = raw.strip().lstrip("-*•").strip()
        l = re.sub(r"^\d+[\.\)]\s*", "", l)
        if 12 <= len(l) <= 200 and not l.lower().startswith(("here", "sure", "of course", "below")):
            lines.append(l)
    new = lines[:cfg["extend_goals_by"]]
    if new:
        append_goals(new)
        log(f"appended {len(new)} new goals; first: {new[0][:70]}")
    else:
        log("extend_goals returned no usable lines")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    JOURNAL_DIR.mkdir(exist_ok=True)
    SYNTH_DIR.mkdir(exist_ok=True)
    if not CONFIG_PATH.exists():
        save_json(CONFIG_PATH, DEFAULT_CONFIG)
    cfg = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    if STOP_PATH.exists():
        log("STOP file present at startup; remove it to run")
        return
    state = load_json(STATE_PATH, {
        "total_turns": 0,
        "subject_index": 0,
        "turn_in_subject": 0,
        "chat_url": None,
        "started_at": datetime.now(timezone.utc).isoformat(),
    })
    if state.get("turn_in_subject", 0) > 0:
        log(f"resuming mid-subject; restarting current subject from turn 0")
        state["turn_in_subject"] = 0
        save_json(STATE_PATH, state)
    token = cfg["auth_token"]
    keep_awake()
    preflight(token)
    ensure_claude_tab(token)
    log(f"robot starting; total_turns={state['total_turns']} subject_index={state['subject_index']}")
    while True:
        if STOP_PATH.exists():
            log("STOP file detected; exiting cleanly")
            break
        if state["total_turns"] >= cfg["max_total_turns"]:
            log(f"hit max_total_turns={cfg['max_total_turns']}; exiting")
            break
        goals = load_goals()
        if state["subject_index"] >= len(goals):
            log("goals queue exhausted; asking Claude for more")
            try:
                extend_goals_via_claude(token, cfg, goals[-5:])
            except Exception as e:
                log(f"extend_goals error: {e!r}")
                time.sleep(cfg["error_backoff_seconds"])
                continue
            goals = load_goals()
            if state["subject_index"] >= len(goals):
                log("still no goals; sleeping then retrying")
                time.sleep(cfg["error_backoff_seconds"])
                continue
        subject = goals[state["subject_index"]]
        try:
            run_subject(token, cfg, state, subject)
        except Exception as e:
            log(f"ERROR in subject '{subject}': {e!r}; backoff {cfg['error_backoff_seconds']}s")
            time.sleep(cfg["error_backoff_seconds"])
            continue
        remaining = len(load_goals()) - state["subject_index"]
        if remaining < cfg["min_goals_remaining"]:
            try:
                extend_goals_via_claude(token, cfg, load_goals()[-5:])
            except Exception as e:
                log(f"auto-extend goals failed: {e!r}")
    log(f"robot stopped at total_turns={state['total_turns']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("interrupted by user (KeyboardInterrupt)")
    except Exception as e:
        log(f"FATAL: {e!r}")
        raise
