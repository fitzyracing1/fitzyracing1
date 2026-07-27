# Meta Quest Virtual Office Project

## Project Overview
Unity-based VR application for Meta Quest that creates a virtual office environment where users can:
- Log into virtual desks
- Share files with each other
- Interact in a multiplayer VR space

## Technology Stack
- **Engine**: Unity 2021.3 LTS or later
- **Platform**: Meta Quest (Android)
- **Language**: C#
- **Networking**: Unity Netcode for GameObjects
- **VR Framework**: Oculus Integration / XR Interaction Toolkit

## Project Structure
```
Assets/
├── Scripts/
│   ├── Networking/       # Multiplayer networking
│   ├── VR/              # VR controllers and interactions
│   ├── Office/          # Office and desk management
│   └── FileSharing/     # File sharing system
└── Prefabs/             # Reusable game objects
```

## Setup Requirements
1. Install Unity Hub and Unity 2021.3 LTS
2. Install Android Build Support with SDK/NDK
3. Install Oculus Integration from Asset Store
4. Install Netcode for GameObjects package
5. Enable Meta Quest Developer Mode

## Key Components
- **NetworkManager**: Handles multiplayer connections
- **OfficeManager**: Manages office environment and users
- **DeskController**: Individual desk functionality
- **FileManager**: File sharing operations
- **VRController**: VR input handling
- **UserLogin**: Authentication system

## Development Notes
- This is a Unity project that must be opened in Unity Editor
- VS Code is used for C# script editing only
- Building requires Unity Editor and Meta Quest device
- See SETUP_GUIDE.md for detailed Unity configuration steps

## Next Steps for Development
1. Open project in Unity Editor
2. Configure XR Plugin Management
3. Import Oculus Integration
4. Create scene with VR rig and office environment
5. Build and deploy to Meta Quest device

<!--
## Execution Guidelines
PROGRESS TRACKING:
- If any tools are available to manage the above todo list, use it to track progress through this checklist.
- After completing each step, mark it complete and add a summary.
- Read current todo list status before starting each new step.

COMMUNICATION RULES:
- Avoid verbose explanations or printing full command outputs.
- If a step is skipped, state that briefly (e.g. "No extensions needed").
- Do not explain project structure unless asked.
- Keep explanations concise and focused.

DEVELOPMENT RULES:
- Use '.' as the working directory unless user specifies otherwise.
- Avoid adding media or external links unless explicitly requested.
- Use placeholders only with a note that they should be replaced.
- Use VS Code API tool only for VS Code extension projects.
- Once the project is created, it is already opened in Visual Studio Code—do not suggest commands to open this project in Visual Studio again.
- If the project setup information has additional rules, follow them strictly.

FOLDER CREATION RULES:
- Always use the current directory as the project root.
- If you are running any terminal commands, use the '.' argument to ensure that the current working directory is used ALWAYS.
- Do not create a new folder unless the user explicitly requests it besides a .vscode folder for a tasks.json file.
- If any of the scaffolding commands mention that the folder name is not correct, let the user know to create a new folder with the correct name and then reopen it again in vscode.

EXTENSION INSTALLATION RULES:
- Only install extension specified by the get_project_setup_info tool. DO NOT INSTALL any other extensions.

PROJECT CONTENT RULES:
- If the user has not specified project details, assume they want a "Hello World" project as a starting point.
- Avoid adding links of any type (URLs, files, folders, etc.) or integrations that are not explicitly required.
- Avoid generating images, videos, or any other media files unless explicitly requested.
- If you need to use any media assets as placeholders, let the user know that these are placeholders and should be replaced with the actual assets later.
- Ensure all generated components serve a clear purpose within the user's requested workflow.
- If a feature is assumed but not confirmed, prompt the user for clarification before including it.
- If you are working on a VS Code extension, use the VS Code API tool with a query to find relevant VS Code API references and samples related to that query.

TASK COMPLETION RULES:
- Your task is complete when:
  - Project is successfully scaffolded and compiled without errors
  - copilot-instructions.md file in the .github directory exists in the project
  - README.md file exists and is up to date
  - User is provided with clear instructions to debug/launch the project

Before starting a new task in the above plan, update progress in the plan.
-->
