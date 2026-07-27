# Crawl Bot

A standalone autonomous crawl bot that operates independently without external control.

## Features

- **Autonomous Operation**: Runs 20 crawl cycles automatically
- **No External Dependencies**: Bot answers to no one, purely self-directed
- **Cycle-Based Execution**: Each cycle simulates a crawl operation
- **Data Collection**: Tracks items found during each crawl cycle

## Project Structure

```
.
├── src/
│   └── crawl_bot.py       # Main bot implementation
├── README.md              # This file
└── .github/
    └── copilot-instructions.md
```

## Getting Started

### Prerequisites
- Python 3.7+

### Running the Bot

```bash
python src/crawl_bot.py
```

The bot will automatically execute 20 crawl cycles and print progress for each cycle.

## Output Example

```
🤖 Crawl Bot Starting - 20 cycles ahead
============================================================
[Cycle 1] Crawled at 2026-01-01T10:30:45.123456 - Found 45 items
[Cycle 2] Crawled at 2026-01-01T10:30:45.234567 - Found 72 items
...
[Cycle 20] Crawled at 2026-01-01T10:30:47.345678 - Found 38 items
============================================================
✓ Bot completed 20 cycles
✓ Total items collected: 1243
```

## Architecture

### CrawlBot Class

- **`__init__(cycles=20)`**: Initialize bot with desired number of cycles
- **`crawl()`**: Execute a single crawl cycle and collect data
- **`run()`**: Run all cycles and return collected data

## Usage

The bot is designed to be completely autonomous:

```python
from src.crawl_bot import CrawlBot

# Create bot with custom cycle count
bot = CrawlBot(cycles=20)

# Run it
results = bot.run()
```

## Notes

- Each cycle has a 0.1 second delay for stable operation
- Data collection happens automatically during crawling
- No configuration or external control needed

---

**Status**: Ready for deployment | **Version**: 1.0.0
