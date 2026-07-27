# muvu1 - File Path Edge Orientation System

A Windows desktop application that orients file paths to the innermost edge of the computer system and relays comprehensive path information.

## Overview

muvu1 is a Python-based Windows application that provides:
- File path normalization and orientation to absolute paths
- Path depth calculation from root
- Comprehensive file/directory metadata relay
- User-friendly GUI interface for path management

## Features

- **Path Orientation**: Resolves and normalizes file paths to their absolute form
- **Edge Calculation**: Determines path depth from the root drive
- **Path Relay**: Displays comprehensive information including:
  - Absolute path
  - Path depth (levels from root)
  - Parent directory
  - File/directory status
  - File size (for files)
  - Drive information
- **GUI Interface**: Easy-to-use Tkinter-based interface
- **Browse Functionality**: File and folder browser dialogs

## Requirements

- Windows OS
- Python 3.8 or higher
- Tkinter (included with Python standard library)

## Installation

1. Ensure Python 3.8+ is installed on your system
2. Clone or download this repository
3. No additional dependencies required (uses Python standard library)

## Usage

### Running the Application

```powershell
python main.py
```

### Using the GUI

1. **Enter a Path**: Type or paste a file/folder path in the input field
2. **Browse**: Use "Browse File" or "Browse Folder" buttons to select paths
3. **Process**: Click "Orient & Relay" to process the path
4. **View Results**: Path information displays in the output area
5. **Clear**: Use "Clear Output" to reset the display

### Path Information Displayed

- Original path as entered
- Absolute resolved path
- Depth from root (number of directory levels)
- Parent directory
- Name of file/directory
- Existence status
- Type (file or directory)
- Drive letter
- File size (for files)

## Project Structure

```
edge_defintion/
├── .github/
│   └── copilot-instructions.md
├── main.py                  # Main application file
├── requirements.txt         # Dependencies (none required)
└── README.md               # This file
```

## How It Works

The application processes file paths through two main components:

### FilePathRelay Class
- `orient_to_edge()`: Normalizes paths to absolute form
- `get_path_depth()`: Calculates directory depth from root
- `relay_path()`: Gathers and returns path metadata

### Muvu1App Class
- Provides the GUI interface
- Handles user interactions
- Displays relayed path information

## Example

Input: `C:\Users\EC\Documents\file.txt`

Output:
```
Original Path:     C:\Users\EC\Documents\file.txt
Absolute Path:     C:\Users\EC\Documents\file.txt
Path Depth:        4 levels from root
Parent Directory:  C:\Users\EC\Documents
Name:              file.txt
Exists:            Yes
Type:              File
Drive:             C:
Size:              2.45 KB (2508 bytes)
```

## Development

The application is built with:
- Python's `pathlib` for path operations
- `tkinter` for GUI
- Standard library only (no external dependencies)

## License

This project is provided as-is for educational and utility purposes.

## Author

Created as a Windows file path management utility.
