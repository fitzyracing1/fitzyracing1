# JARVIS - Autonomous Mechanical Parts Generation Bot

JARVIS is an intelligent technical bot that autonomously generates mechanical parts and continuously creates files from its own prediction cycles. Inspired by the AI assistant from Iron Man, this system leverages Natural Language Processing and Machine Learning to design and optimize mechanical components.

## Features

- **Autonomous Part Generation**: JARVIS continuously generates mechanical parts based on ML predictions
- **Self-Generating Files**: Automatically creates JSON files for each generated part
- **Machine Learning Predictions**: Uses intelligent algorithms to predict part properties
- **NLP Integration**: Natural Language Processing for text analysis and keyword extraction
- **File Management**: Organized storage of parts, metadata, and session logs
- **Interactive & Autonomous Modes**: Choose between user-directed or fully autonomous operation
- **Batch Generation**: Generate multiple parts in a single operation
- **Statistics & Reporting**: Comprehensive tracking of generation statistics

## Project Structure

```
jarvis_bot/
├── main.py                 # Main JARVIS orchestrator
├── requirements.txt        # Python dependencies
├── bot_parts/
│   ├── nlp.py             # NLP module for text processing
│   ├── ml.py              # Machine Learning module for predictions
│   └── file_manager.py    # File I/O and persistence
├── data/
│   ├── parts/             # Generated part files (JSON)
│   ├── logs/              # Session logs
│   └── metadata/          # Generation metadata
└── README.md              # This file
```

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode (Default)

Run JARVIS in interactive mode where you control part generation:

```bash
python main.py
```

**Available Commands:**
- `generate [n]` - Generate n mechanical parts
- `status` - Show generation statistics
- `list` - List all generated parts
- `auto [n]` - Start autonomous cycles with n second delay
- `stop` - Stop autonomous generation
- `exit` - Exit JARVIS

Example:
```
JARVIS> generate 5
JARVIS> status
JARVIS> auto 3
```

### Autonomous Mode

Run JARVIS in fully autonomous mode:

```bash
# Run 10 cycles with 2 second delay between cycles
python main.py --mode autonomous --cycles 10 --delay 2

# Run 5 cycles with 1 second delay (faster)
python main.py --mode autonomous --cycles 5 --delay 1
```

**Command Line Options:**
- `--mode {interactive|autonomous}` - Operation mode (default: interactive)
- `--cycles N` - Number of cycles to run in autonomous mode (default: 5)
- `--delay N` - Delay between cycles in seconds (default: 2)

## Generated Output

### Part Files
Each generated part is saved as a JSON file with the following structure:

```json
{
  "id": 1,
  "name": "Motor_mechanical_1",
  "category": "Motor",
  "type": "Mechanical",
  "material": "Metal",
  "version": "1.0",
  "dimensions": {
    "diameter": 75,
    "width": 45,
    "height": 38,
    "weight": 2.5
  },
  "specifications": {
    "max_rpm": 3500,
    "torque_capacity": 250.5,
    "temperature_range": "-30 to 150 C",
    "efficiency": 0.92
  },
  "keywords": [],
  "confidence_score": 0.87
}
```

### Data Organization

- **Parts Directory**: `data/parts/` - Contains all generated part definitions
- **Metadata**: `data/metadata/` - Contains generation statistics and metadata
- **Logs**: `data/logs/` - Contains session execution logs

## Generated Part Categories

JARVIS can generate the following part types:
- Motors, Gears, Bearings, Shafts
- Couplings, Valves, Pumps, Cylinders
- Joints, Springs, Brackets, Pulleys
- Belts, Pistons, Actuators

Part types include:
- Mechanical, Electrical, Hydraulic, Pneumatic

Available materials:
- Metal, Plastic, Composite, Titanium, Aluminum, Steel

## Architecture

### NLP Module (`nlp.py`)
- Text tokenization and analysis
- Stopword removal
- Keyword extraction
- Sentiment analysis using VADER

### ML Module (`ml.py`)
- Autonomous part property prediction
- Batch generation capabilities
- Statistical analysis of generated parts
- Confidence scoring

### File Manager (`file_manager.py`)
- JSON serialization and storage
- Directory management
- Session logging
- Metadata tracking

## Example Workflow

1. **Start JARVIS**:
   ```bash
   python main.py
   ```

2. **Generate initial batch**:
   ```
   JARVIS> generate 10
   ```

3. **Check statistics**:
   ```
   JARVIS> status
   ```

4. **Switch to autonomous mode**:
   ```
   JARVIS> auto 5
   ```

5. **View generated parts**:
   ```
   JARVIS> list
   ```

6. **Exit JARVIS**:
   ```
   JARVIS> exit
   ```

## System Requirements

- Python 3.7+
- 100+ MB free disk space for part files
- NLTK data files (downloaded automatically on first run)

## Performance Notes

- Generation speed: ~5-10 parts per cycle
- File I/O: One file per part (~2-3KB per file)
- Memory usage: Minimal (~50-100MB)

## Future Enhancements

- CAD file generation (STEP/IGES format)
- Advanced ML models for part optimization
- Real-time 3D visualization
- Database backend for part storage
- REST API for remote access
- Multi-threading for faster generation

## License

JARVIS Mechanical Parts Generation Bot - 2025

## Disclaimer

This is an educational demonstration of autonomous part generation. Generated parts are simulated and should not be used for actual manufacturing without proper engineering validation.
