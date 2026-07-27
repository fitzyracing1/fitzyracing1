"""Backfill empty/short responses in a robot journal file.

When the machine sleeps mid-run, some turns get journaled with an empty
response (the bridge scraped a suspended page). This re-asks the exact
recorded prompt for each such turn, captures a fresh response via the
bridge, and rewrites the journal in place.

Each turn's prompt already embeds its `(trace-N)` tag and (for follow-ups)
the full question text, so the prompts are effectively self-contained. We
ask each in its own fresh chat -- the answer won't carry the original
in-conversation context, but it will be a complete, on-topic reply.

Requires the bridge up and the Chrome extension connected to a logged-in
claude.ai tab (same prerequisites as agent.py).

Usage:
    python C:\\Users\\EC\\robot\\backfill.py                 # newest journal
    python C:\\Users\\EC\\robot\\backfill.py <file.jsonl>    # specific journal
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import agent  # reuse bridge transport + response-wait logic

MIN_OK = 80  # chars; matches the short-response threshold in agent.run_subject


def newest_journal():
    files = sorted(agent.JOURNAL_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_journal()
    if not path or not path.exists():
        agent.log(f"backfill: journal not found: {path}")
        return

    cfg = agent.load_json(agent.CONFIG_PATH, agent.DEFAULT_CONFIG)
    for k, v in agent.DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    token = cfg["auth_token"]

    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
               if l.strip()]
    missing = [r for r in records if len((r.get("response") or "")) < MIN_OK]
    if not missing:
        agent.log("backfill: nothing to fill; all responses look complete")
        return
    agent.log(f"backfill: {len(missing)} turn(s) to refill in {path.name}: "
              + ", ".join(str(r["turn_id"]) for r in missing))

    agent.preflight(token)
    agent.ensure_claude_tab(token)

    filled = 0
    for r in missing:
        prompt = r["prompt"]
        m = re.search(r"\(trace-[^)]+\)", prompt)
        tag = m.group(0) if m else None
        if not tag:
            agent.log(f"backfill turn {r['turn_id']}: no trace tag in prompt; skipping")
            continue
        agent.log(f"backfill turn {r['turn_id']}: opening fresh chat")
        agent.navigate_new_chat(token)
        agent.send_prompt(token, prompt)
        resp = agent.wait_for_response(token, tag, cfg)
        if len(resp) >= MIN_OK:
            r["response"] = resp
            r["backfilled"] = True
            filled += 1
            agent.log(f"backfill turn {r['turn_id']} ok ({len(resp)} chars)")
        else:
            agent.log(f"backfill turn {r['turn_id']} still short ({len(resp)} chars); leaving as-is")
        time.sleep(cfg["cadence_seconds"])

    # Atomic rewrite, preserving original order.
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, path)
    agent.log(f"backfill: rewrote {path.name}; filled {filled}/{len(missing)} turn(s)")


if __name__ == "__main__":
    agent.keep_awake()
    try:
        main()
    except Exception as e:
        agent.log(f"backfill FATAL: {e!r}")
        raise
