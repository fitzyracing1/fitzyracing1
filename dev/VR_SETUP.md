# VR Setup Instructions for Meta Quest

## Converting Your Unity Project to Quest VR

### 1. Install XR Plugin Management
In Unity Editor:
1. Go to **Edit > Project Settings > XR Plugin Management**
2. Click **Install XR Plugin Management**
3. Switch to **Android** tab
4. Check **Oculus** (or **Meta Quest**)

### 2. Configure Android Build Settings
1. Go to **File > Build Settings**
2. Select **Android** platform
3. Click **Switch Platform**
4. Click **Player Settings**
5. Set the following:
   - **Company Name**: Your company name
   - **Product Name**: UnityApartmentsVR
   - **Minimum API Level**: Android 10.0 (API Level 29)
   - **Target API Level**: Automatic (highest installed)

### 3. Configure XR Settings
In **Project Settings > XR Plugin Management > Oculus**:
- **Stereo Rendering Mode**: Multiview
- **Target Devices**: Check **Quest** and **Quest 2/3**

### 4. Update Scene
- The **VRSceneSetup** script is already configured in MainScene
- It will automatically create VR player, hands, and interactions
- Set `enableVRMode = true` in the Inspector (already set)

### 5. Build for Quest
1. Connect your Quest via USB
2. Enable **Developer Mode** on your Quest
3. In Unity: **File > Build Settings**
4. Click **Build And Run**
5. Choose a location and filename
6. Unity will build and install to your Quest

## VR Controls

### Quest Controllers:
- **Left Thumbstick**: Move forward/backward/strafe
- **Right Thumbstick**: Snap turn left/right
- **Trigger (either hand)**: Interact with doors and books
- **Point laser at objects**: Highlights interactable items

## Testing in Unity Editor

You can test VR functionality in Unity Editor with:
1. Install **Oculus Desktop App**
2. Connect Quest via Link cable or Air Link
3. Press Play in Unity Editor
4. Put on headset

## Project Features in VR

- **Apartment Building**: Walk through multiple floors and rooms
- **Interactive Doors**: Point and trigger to open/close
- **Coding Project Books**: Point at books and trigger to view details
- **Smooth Locomotion**: Natural walking with thumbstick
- **Snap Turning**: Comfortable rotation to prevent motion sickness

## Scripts Created:
- `VRPlayerController.cs` - VR movement and input
- `VRInteractor.cs` - Hand tracking and ray-based interaction
- `VRSceneSetup.cs` - Automatic VR scene configuration
- All existing scripts updated for VR compatibility

## Troubleshooting

### Black screen in Quest:
- Check XR Plugin Management is installed
- Verify Oculus/Meta Quest is checked in Android tab
- Ensure Stereo Rendering Mode is set

### Controllers not working:
- Make sure Target Devices includes Quest
- Verify Input System is not conflicting
- Check VR hands are created in hierarchy

### Build fails:
- Install Android Build Support in Unity Hub
- Update Android SDK/NDK via Unity Hub
- Check USB debugging is enabled on Quest

## Next Steps

1. Install XR Plugin Management packages
2. Switch to Android platform
3. Build and deploy to Quest
4. Enjoy your VR apartment portfolio!
