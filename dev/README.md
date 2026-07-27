# Unity Project

A Unity game development project with C# scripts and VS Code integration.

## Project Structure

```
├── Assets/
│   ├── Scripts/          # C# game scripts
│   │   ├── PlayerController.cs
│   │   ├── GameManager.cs
│   │   └── CameraFollow.cs
│   ├── Scenes/           # Unity scenes
│   │   └── MainScene.unity
│   ├── Prefabs/          # Reusable game objects
│   ├── Materials/        # Material assets
│   └── ...
├── ProjectSettings/      # Unity project settings
└── .github/
    └── copilot-instructions.md
```

## Scripts Overview

### PlayerController.cs
- Handles player movement and jumping
- Uses Rigidbody for physics-based movement
- Includes ground detection
- Configurable movement speed and jump force

### GameManager.cs
- Singleton pattern for global game state
- Score tracking system
- Lives management
- Game restart functionality

### CameraFollow.cs
- Smooth camera following system
- Configurable offset and smoothing
- Optional target look-at functionality

## Getting Started

### Prerequisites
- Unity Hub and Unity Editor (2021.3 LTS or later recommended)
- Visual Studio Code with Unity extensions

### Setup Instructions

1. **Open in Unity Hub**
   - Open Unity Hub
   - Click "Add" or "Open"
   - Select this project folder (`c:\Users\EC\dev`)

2. **Generate VS Code Solution Files**
   - Open the project in Unity Editor
   - Go to `Edit > Preferences > External Tools`
   - Set "External Script Editor" to Visual Studio Code
   - Click "Regenerate project files"

3. **Open in VS Code**
   - The project should now be properly configured
   - Open the workspace in VS Code to edit scripts

### Usage

1. **Creating a Scene**
   - Use MainScene.unity as a starting point
   - Add a player GameObject with Rigidbody component
   - Attach PlayerController.cs to the player
   - Add a camera with CameraFollow.cs and assign the player as target
   - Add GameManager GameObject with GameManager.cs

2. **Testing**
   - Press Play in Unity Editor to test the game
   - Use WASD/Arrow keys for movement
   - Press Space to jump

## Development

### Adding New Scripts
1. Create C# scripts in `Assets/Scripts/` folder
2. Unity will automatically compile them
3. Attach scripts to GameObjects in the Inspector

### Debugging
- Use `Debug.Log()` for console output
- Set breakpoints in VS Code (requires Unity Debugger extension)
- Check Unity Console for runtime errors

## Building the Project

### Command-Line Build

Three build scripts are provided for automated builds:

#### PowerShell Script (Build.ps1)
```powershell
# Basic build
.\Build.ps1

# With custom Unity path
.\Build.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\2022.3.10f1\Editor\Unity.exe"

# Development build
.\Build.ps1 -Development

# Custom build location
.\Build.ps1 -BuildPath "C:\MyBuilds\Windows"
```

#### Batch Script (Build.bat)
```cmd
Build.bat
```

#### From Unity Editor
The `BuildScript.cs` editor script provides menu options:
- **Build > Build Windows** - Build for Windows
- **Build > Build Linux** - Build for Linux
- **Build > Build macOS** - Build for macOS

### Requirements
- Update the Unity path in the build scripts to match your Unity installation
- Add scenes to Build Settings in Unity Editor (File > Build Settings)
- Builds will be output to the `Builds/` folder

## Extensions Installed
- Unity (Visual Studio Tools for Unity)
- Unity Code Snippets

## Notes

- This is a basic Unity project structure
- Unity-specific files (.meta files) will be generated automatically when you open the project in Unity Editor
- Make sure to commit .meta files to version control if using Git
- The project uses Unity's default settings and configurations

## License

This project is a template and can be used freely for any purpose.
