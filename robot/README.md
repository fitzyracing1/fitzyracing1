# Research Robot

Autonomous agent that drives Claude.ai through the AI Browser Bridge, running thousands of turns unattended. Picks subjects from `goals.txt`, drills 8 turns deep on each via self-extracted follow-ups (Claude proposes its own next question with a `NEXT:` line), writes a synthesis markdown file per subject, then advances. When the goals queue runs low, asks Claude itself for new subjects.

## Run

```powershell
C:\Users\EC\robot\run.ps1
```

This boots the bridge (if not running), clears any old STOP file, and starts `agent.py` hidden. The robot expects the user's Chrome to be open with the AI Browser Bridge extension connected.

## Stop

```powershell
New-Item C:\Users\EC\robot\STOP
```

The robot checks for this file each turn and exits cleanly after the current turn completes.

## Tail logs

```powershell
Get-Content C:\Users\EC\robot\agent.log -Wait -Tail 20
```

## Files

- `agent.py` — main loop (single-file, stdlib only)
- `config.json` — cadence, turns-per-subject, caps (created on first run from defaults)
- `goals.txt` — editable queue of subjects; one per line; edit any time
- `state.json` — persistent counters; resumes after restart
- `journal/<timestamp>_<subject>.jsonl` — every turn (prompt + response)
- `syntheses/<subject>.md` — per-subject final brief

## Tuning

Edit `config.json`. Key knobs:

- `cadence_seconds`: pause between turns (default 30)
- `turns_per_subject`: depth per subject before synthesis (default 8)
- `max_total_turns`: hard cap (default 5000)
- `max_response_wait_seconds`: how long to wait for Claude to finish (default 90)
