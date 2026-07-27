# Meta Quest Virtual Office

A virtual reality office application for Meta Quest where users can log into virtual desks and share files with each other in a collaborative workspace.

## Features

- **Virtual Desks**: Each user has their own virtual desk workspace
- **Multiplayer Support**: Multiple users can join the same office space
- **File Sharing**: Share and view files with other users in real-time
- **VR Interactions**: Natural hand-based interactions for object manipulation
- **User Authentication**: Login system to identify users

## Prerequisites

- Unity 2021.3 LTS or later
- Meta Quest SDK (Oculus Integration package)
- Meta Quest 2 or Quest Pro headset
- Unity Hub installed

## Setup Instructions

### 1. Create Unity Project

1. Open Unity Hub
2. Create a new 3D project (Core)
3. Name it "MetaQuestVirtualOffice"
4. Copy the contents of this repository into your Unity project's `Assets/Scripts` folder

### 2. Install Required Packages

Via Unity Package Manager:
- Oculus Integration (from Asset Store)
- Netcode for GameObjects (Unity Package Manager)
- TextMeshPro (if not already installed)

### 3. Configure Project Settings

1. **Build Settings**
   - File → Build Settings → Android
   - Switch Platform to Android

2. **XR Settings**
   - Edit → Project Settings → XR Plug-in Management
   - Enable Oculus
   - Set Texture Quality to High

3. **Player Settings**
   - Set Minimum API Level to Android 10.0 (API level 29)
   - Set Install Location to Automatic
   - Set Write Permission to External (SDCard)
   - Enable Internet Access

### 4. Scene Setup

1. Create a new scene called "VirtualOffice"
2. Add the `NetworkManager` script to an empty GameObject
3. Add the `OfficeManager` script to an empty GameObject
4. Create a floor plane and walls for the office space
5. Place desk prefabs in the scene

## Project Structure

```
Assets/
├── Scripts/
│   ├── Networking/
│   │   ├── NetworkManager.cs
│   │   └── PlayerNetwork.cs
│   ├── VR/
│   │   ├── VRController.cs
│   │   ├── VRGrabber.cs
│   │   └── VRTeleport.cs
│   ├── Office/
│   │   ├── OfficeManager.cs
│   │   ├── DeskController.cs
│   │   └── UserLogin.cs
│   └── FileSharing/
│       ├── FileManager.cs
│       ├── FileDisplay.cs
│       └── FileSync.cs
└── Prefabs/
    ├── Player.prefab
    ├── Desk.prefab
    └── FileViewer.prefab
```

## Building for Meta Quest

1. Connect your Meta Quest headset via USB
2. Enable Developer Mode on your Quest
3. File → Build Settings → Build and Run
4. Install the APK on your device

## Usage

1. Put on your Meta Quest headset
2. Launch the Virtual Office app
3. Enter your username to log in
4. Use hand controllers to:
   - Teleport around the office
   - Grab and manipulate objects
   - Share files with other users
   - Access your virtual desk

## Technologies Used

- Unity 3D
- Meta Quest SDK (Oculus Integration)
- Unity Netcode for GameObjects (Multiplayer)
- C# Programming

## Notes

- This is a starting framework. You'll need to set up a multiplayer backend (Unity Relay, Photon, or custom server)
- File sharing requires implementing actual file transfer protocol
- 3D models for desks and office furniture need to be created or imported
- Consider implementing voice chat for better collaboration

## Development Tips

- Test VR interactions in the Unity Editor using Oculus Link
- Use the XR Interaction Toolkit for more advanced interactions
- Implement proper error handling for network disconnections
- Add user presence indicators (avatars, nameplates)

## License

MIT License
