# Unity Setup Guide for Meta Quest Virtual Office

## Prerequisites Installation

### 1. Install Unity Hub
- Download from: https://unity.com/download
- Install Unity Hub on your system

### 2. Install Unity Editor (2021.3 LTS or later)
1. Open Unity Hub
2. Go to Installs → Install Editor
3. Select Unity 2021.3 LTS (or newer)
4. Add Android Build Support:
   - ☑ Android Build Support
   - ☑ Android SDK & NDK Tools
   - ☑ OpenJDK

### 3. Set up Meta Quest Developer Mode
1. Create a Meta Developer account at: https://developer.oculus.com
2. Create an organization (required for development)
3. On your Meta Quest device:
   - Go to Settings → System → Developer Mode
   - Enable Developer Mode

### 4. Install Meta Quest Developer Hub (Optional but recommended)
- Download from: https://developer.oculus.com/downloads/

## Creating the Unity Project

### Step 1: Create New Project
1. Open Unity Hub
2. Click "New Project"
3. Select "3D Core" template
4. Name: "MetaQuestVirtualOffice"
5. Click "Create Project"

### Step 2: Import Scripts
1. Copy all files from this repository into your Unity project
2. The scripts should be in `Assets/Scripts/` folder

### Step 3: Install Required Packages

#### A. Install Oculus Integration (from Asset Store)
1. Open Unity Asset Store window (Window → Asset Store)
2. Search for "Oculus Integration"
3. Download and Import
4. When prompted, accept Oculus XR plugin setup
5. Restart Unity if prompted

#### B. Install Netcode for GameObjects
1. Window → Package Manager
2. Click "+" → Add package by name
3. Enter: `com.unity.netcode.gameobjects`
4. Click "Add"

#### C. Install TextMeshPro (if not already installed)
1. Window → Package Manager
2. Search for "TextMesh Pro"
3. Click "Install"
4. Import TMP Essential Resources when prompted

### Step 4: Configure Project Settings

#### Build Settings
1. File → Build Settings
2. Select "Android"
3. Click "Switch Platform"
4. Set Texture Compression to ASTC

#### XR Plugin Management
1. Edit → Project Settings → XR Plug-in Management
2. Click "Install XR Plugin Management"
3. Under Android tab:
   - ☑ Oculus
4. Click on Oculus settings:
   - Set Target Devices to Quest 2
   - Set Stereo Rendering Mode to Multiview

#### Player Settings
1. Edit → Project Settings → Player
2. Under Android tab:

**Other Settings:**
- Package Name: com.yourcompany.virtualoffice
- Minimum API Level: Android 10.0 (API level 29)
- Target API Level: Automatic (highest installed)
- Scripting Backend: IL2CPP
- Target Architectures: ☑ ARM64

**Publishing Settings:**
- Build:
  - Compression Method: LZ4
- Configuration:
  - Scripting Define Symbols: (leave default)
  - Allow 'unsafe' Code: ☐

**XR Settings:**
- ☑ Virtual Reality Supported (this might be under Deprecated)

#### Quality Settings
1. Edit → Project Settings → Quality
2. Set Default quality level to Medium or High
3. Adjust for VR performance:
   - V Sync Count: Don't Sync
   - Antialiasing: 2x Multi Sampling

#### Graphics Settings
1. Edit → Project Settings → Graphics
2. Check that the Scriptable Render Pipeline is set to None (Built-in)

### Step 5: Create Scene

1. Create new scene: File → New Scene → Basic (Built-in)
2. Save as "VirtualOffice"

#### Add Network Manager
1. Create empty GameObject: GameObject → Create Empty
2. Rename to "NetworkManager"
3. Add component: `NetworkManager` (Unity.Netcode)
4. Add your custom `NetworkManager.cs` script

#### Add Office Manager
1. Create empty GameObject
2. Rename to "OfficeManager"
3. Add your custom `OfficeManager.cs` script

#### Add VR Rig
1. Right-click in Hierarchy → XR → XR Origin (Action-based)
2. This creates the VR camera and controllers
3. Add your VR scripts to the controllers

#### Add Environment
1. Create floor: GameObject → 3D Object → Plane
2. Scale to appropriate office size (e.g., 20, 1, 20)
3. Create walls (cubes) around the perimeter

#### Create Desk Prefab
1. GameObject → 3D Object → Cube (for desk surface)
2. Add child objects for desk legs
3. Add your `DeskController.cs` script
4. Drag to Prefabs folder to create prefab
5. Place multiple desk instances in scene

### Step 6: Build for Meta Quest

#### Connect Device
1. Connect Meta Quest to PC via USB-C
2. Put on headset and allow USB debugging when prompted
3. Verify connection in Command Prompt: `adb devices`

#### Build Settings
1. File → Build Settings
2. Add current scene to "Scenes In Build"
3. Select Android platform
4. Click "Player Settings" and verify all settings
5. Close Player Settings

#### Build and Run
1. Click "Build And Run"
2. Choose location to save APK
3. Wait for build to complete
4. App will automatically install and launch on Quest

### Step 7: Testing

#### In Editor Testing (with Oculus Link)
1. Connect Quest to PC
2. Enable Oculus Link on Quest
3. In Unity, click Play
4. Test with Quest controllers

#### On Device Testing
1. Put on Meta Quest headset
2. Go to Apps → Unknown Sources
3. Find "MetaQuestVirtualOffice"
4. Launch the app

## Troubleshooting

### Build Errors
- **"Unable to find Android SDK"**: Install Android SDK through Unity Hub or set path in Preferences
- **"Java exception"**: Ensure minimum API level is 29 or higher
- **Missing packages**: Reinstall required packages through Package Manager

### Runtime Issues
- **Black screen**: Check XR Plugin Management settings
- **Controllers not working**: Verify Oculus Integration is properly imported
- **Network not connecting**: Check NetworkManager configuration

### Performance Issues
- Lower quality settings
- Reduce shadow quality
- Optimize mesh complexity
- Use texture compression

## Next Steps

1. Implement user authentication backend
2. Set up dedicated server for multiplayer
3. Add 3D models for office furniture
4. Implement voice chat
5. Add more file types support
6. Create avatar system

## Useful Resources

- [Unity XR Documentation](https://docs.unity3d.com/Manual/XR.html)
- [Meta Quest Developer Center](https://developer.oculus.com/documentation/)
- [Unity Netcode Documentation](https://docs-multiplayer.unity3d.com/)
- [Oculus Integration Guide](https://developer.oculus.com/documentation/unity/)
