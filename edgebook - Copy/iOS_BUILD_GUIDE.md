# EdgeBook iOS Build Guide

This guide covers building EdgeBook OS for iPad with Windows app integration.

## Overview

EdgeBook now supports iOS builds using React Native and Expo. The iOS version includes:

- **App Store** with web and cloud applications
- **Windows Segment** - Access and launch Windows desktop applications from iPad
- **iPad Optimization** - Full landscape mode support with responsive layouts
- **Cross-platform Architecture** - Shared app catalogs and configurations

## Project Structure

```
edgebook/
├── ios/                          # iOS/React Native project
│   ├── app.json                 # Expo configuration
│   ├── eas.json                 # EAS Build configuration
│   ├── App.tsx                  # Main app component
│   ├── package.json             # iOS dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── src/
│   │   ├── screens/
│   │   │   └── AppStoreScreen.tsx    # App Store UI
│   │   ├── components/
│   │   │   └── WindowsSegment.tsx    # Windows apps interface
│   │   ├── services/
│   │   │   └── WindowsAppLaunchService.ts  # iOS↔Windows bridge
│   │   └── index.tsx            # Entry point
│   └── assets/                  # App icons and images
├── windows-backend/             # Node.js backend for Windows
│   ├── server.ts               # Express API server
│   ├── package.json            # Node dependencies
│   └── tsconfig.json           # TypeScript config
├── electron/                    # Electron main process (Windows Desktop)
├── renderer/                    # React UI (shared)
└── package.json                # Root configuration
```

## Prerequisites

### For iOS Development

1. **macOS** - iOS development requires a Mac
2. **Xcode** - Install from App Store or [developer.apple.com](https://developer.apple.com)
3. **Node.js** - v18 or higher
4. **Expo CLI** - `npm install -g expo-cli`
5. **EAS CLI** - `npm install -g eas-cli` (for building)

### For Windows Backend

1. **Node.js** - v18 or higher
2. **npm** - v8 or higher

## Installation

### iOS Setup

```bash
cd ios
npm install
```

### Windows Backend Setup

```bash
cd windows-backend
npm install
```

## Development

### Running on iOS Simulator

```bash
cd ios
npm run dev:ios
```

This will:
- Start the Expo development server
- Open the app in the iOS simulator
- Enable hot reloading

### Running on Physical iPad

1. Install the Expo Go app from App Store
2. From the `ios/` directory:
   ```bash
   npm run dev
   ```
3. Scan the QR code with your iPad camera
4. The app will open in Expo Go

### Running Windows Backend

```bash
cd windows-backend
npm run dev
```

The backend server will start on `http://localhost:3000`

## Windows App Integration

### How It Works

1. **iOS App** → Sends app launch request to Windows Backend
2. **Windows Backend** → Receives request, validates app, launches executable
3. **Windows App** → Opens on Windows machine and can be controlled

### Windows Apps Catalog

The Windows Segment includes:

**Development Tools:**
- Visual Studio Code
- Visual Studio 2022
- Node.js
- Git
- Docker Desktop
- Azure CLI

**System Tools:**
- PowerShell 7
- Windows Terminal
- Windows Subsystem for Linux
- Hyper-V

**Design Software:**
- Adobe Photoshop
- Adobe Illustrator
- Blender

**Media Tools:**
- OBS Studio
- FFmpeg
- VLC Media Player

### Adding New Windows Apps

Edit `ios/src/components/WindowsSegment.tsx` and add to the `windowsAppsData` array:

```typescript
{
  id: 'my-app',
  name: 'My Application',
  description: 'Description of the app',
  icon: '🚀',
  category: 'Development',
  executablePath: 'C:\\Path\\To\\App.exe',
  isInstalled: false,
}
```

Then update `windows-backend/server.ts` to include the executable path:

```typescript
const appPaths: { [key: string]: string } = {
  'my-app': 'C:\\Path\\To\\App.exe',
  // ... other apps
};
```

## Building for Production

### iOS App Store Build

#### Step 1: Configure App Information

Edit `ios/app.json`:

```json
{
  "expo": {
    "name": "EdgeBook OS",
    "slug": "edgebook-os",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.yourcompany.edgebook",
      "buildNumber": "1"
    }
  }
}
```

#### Step 2: Create EAS Build Project

```bash
cd ios
eas build:configure
```

#### Step 3: Build for iOS

```bash
# Development build
npm run build:ipa

# Or submit directly to App Store
npm run submit
```

#### Step 4: Upload to App Store Connect

1. Download the `.ipa` file from EAS Build
2. Use Xcode's Organizer or Transporter to upload to App Store Connect
3. Submit for review

### Windows Backend Production Build

```bash
cd windows-backend
npm run build
npm start
```

For deployment, consider:
- Running as a Windows Service using `nssm` or `pm2`
- Using Docker for containerization
- Setting up reverse proxy (nginx/Apache)

## Configuration

### iOS Configuration (app.json)

Key settings for iPad optimization:

```json
{
  "expo": {
    "orientation": "landscape",
    "ios": {
      "supportsTabletMode": true,
      "buildNumber": "1"
    }
  }
}
```

### Windows Backend Configuration (.env)

```env
PORT=3000
NODE_ENV=production
CORS_ORIGIN=http://your-ios-device-ip:port
LOG_LEVEL=info
```

## Testing

### iOS Testing

```bash
cd ios
# Run on simulator
npm run dev:ios

# Test specific component
npm run dev:ios -- --app-id com.edgebook.os
```

### Windows Backend Testing

```bash
cd windows-backend

# Test health endpoint
curl http://localhost:3000/api/health

# Test app launch
curl -X POST http://localhost:3000/api/windows/launch \
  -H "Content-Type: application/json" \
  -d '{
    "appId": "vscode",
    "userId": "test-user",
    "deviceId": "test-device"
  }'
```

## Troubleshooting

### iOS Issues

**App won't build:**
```bash
# Clear cache and rebuild
cd ios
rm -rf node_modules package-lock.json
npm install
npm run dev:ios
```

**Device connection issues:**
- Ensure device and development machine are on same network
- Check firewall settings
- Verify port 8081 is available

### Windows Backend Issues

**Port already in use:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

**App launch fails:**
- Check executable paths are correct
- Verify Windows user permissions
- Check Windows Firewall settings

## Performance Optimization

### iOS Performance

- Images optimized for iPad resolution (2732x2048)
- FlatList used for efficient app listing
- Memoized category filtering
- Code splitting with Expo bundling

### Windows Backend Performance

- Connection pooling for multiple requests
- Async/await pattern prevents blocking
- Process spawning with detached mode
- Activity logging for monitoring

## Security Considerations

### iOS Security

- HTTPS only communication with backend
- Certificate pinning recommended
- API authentication tokens
- Secure storage of user credentials (Keychain)

### Windows Backend Security

- Input validation on all endpoints
- Rate limiting on app launch endpoint
- Whitelist of allowed applications
- User authentication required
- Audit logging of all launches

## Deployment Checklist

- [ ] Update version numbers (iOS and backend)
- [ ] Update app.json with correct bundle ID
- [ ] Configure eas.json with ASC App ID
- [ ] Run all tests
- [ ] Build production iOS app
- [ ] Deploy Windows backend
- [ ] Test end-to-end on device
- [ ] Submit to App Store
- [ ] Release notes prepared
- [ ] Support documentation updated

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                 iPad (iOS)                          │
│  ┌──────────────────────────────────────────────┐  │
│  │    EdgeBook App (React Native)              │  │
│  │  ┌──────────────┐  ┌──────────────────────┐ │  │
│  │  │  App Store   │  │  Windows Segment     │ │  │
│  │  │  UI          │  │  (App Launcher)      │ │  │
│  │  └──────────────┘  └──────────────────────┘ │  │
│  │           │                   │              │  │
│  │  WindowsAppLaunchService      │              │  │
│  │           │                   │              │  │
│  └───────────┼───────────────────┼──────────────┘  │
│              │                   │                  │
└──────────────┼───────────────────┼──────────────────┘
               │                   │
        HTTPS  │   HTTP/REST       │
               │                   │
┌──────────────┼───────────────────┼──────────────────┐
│              ▼                   ▼                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Windows Backend (Node.js/Express)          │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │  Windows App Launch Service            │ │  │
│  │  │  - App validation                      │ │  │
│  │  │  - Process spawning                    │ │  │
│  │  │  - Session management                  │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  │           │                                  │  │
│  └───────────┼──────────────────────────────────┘  │
│              │                                     │
└──────────────┼─────────────────────────────────────┘
               │
        taskkill/Process Spawn
               │
┌──────────────▼──────────────────────────────────────┐
│        Windows Desktop Applications                │
│  (VS Code, Node.js, Docker, etc.)                 │
└────────────────────────────────────────────────────┘
```

## Next Steps

1. **Configure Apple Developer Account** - Required for App Store submission
2. **Set Up CI/CD** - Automate builds with GitHub Actions or EAS
3. **Implement Authentication** - Add user accounts and permissions
4. **Add Remote Desktop** - Integrate RDP or VNC for full desktop control
5. **Expand App Catalog** - Add more supported applications
6. **Analytics** - Track app usage and user behavior

## Support

For issues or questions:
- Check troubleshooting section above
- Review Expo documentation: https://docs.expo.dev
- Check React Native docs: https://reactnative.dev
- Review Express.js docs: https://expressjs.com

## License

EdgeBook OS - All Rights Reserved
