# EdgeBook OS

A cross-platform application ecosystem for Windows (Desktop) and iPad, featuring integrated app stores and Windows app launching from iOS.

## 🎯 Platforms

### Windows Desktop
Electron + React + TypeScript with Microsoft Edge WebView2 and standalone .exe packaging.

### iPad
React Native + Expo with native iOS optimization, App Store integration, and **Windows App Segment** for launching desktop applications.

## Quick Start

### Windows Desktop Development
```powershell
# From the project root
npm install
npm run dev
```

This opens the Electron window with the React UI and hot reload via Vite.

### iPad Development

Prerequisites: macOS, Xcode, Node.js 18+, Expo CLI

```bash
cd ios
npm install
npm run dev:ios
```

Opens the app in iOS Simulator with live reloading.

## 📱 iPad Features

### App Store
Launch web and cloud applications:
- **Browser**: Microsoft Edge
- **Productivity**: Outlook, OneNote, OneDrive, Notion
- **Communication**: Teams, Discord, Slack
- **AI**: Copilot
- **Entertainment**: Netflix, Spotify
- **Design**: Figma, Adobe Suite

### Windows Segment
**New!** Launch Windows desktop applications directly from iPad:
- **Development**: VS Code, Visual Studio, Node.js, Git, Docker
- **System Tools**: PowerShell, Windows Terminal, WSL, Hyper-V
- **Design**: Photoshop, Illustrator, Blender
- **Media**: OBS Studio, FFmpeg, VLC

See [iOS_BUILD_GUIDE.md](./iOS_BUILD_GUIDE.md) for complete iPad setup and deployment.

## 🏗️ Build & Package

### Windows Desktop
```powershell
npm run dev              # Start dev server
npm run build            # Build renderer + main process
npm run start            # Run the built app
npm run dist:win         # Create Windows installer (.exe)
```

### iPad
```bash
cd ios
npm run dev:ios          # Run on iOS Simulator
npm run build:ipa        # Build for App Store
npm run submit           # Submit to App Store
```

## ✨ Core Features

### Windows Desktop
- **Electron + React** — Native desktop framework
- **Microsoft Edge WebView2** — Modern rendering engine
- **App Store** — Web and desktop app launcher
- **Vite** — Lightning-fast dev server
- **TypeScript** — Type-safe development
- **Windows Packaging** — Standalone .exe installer

### iPad
- **React Native + Expo** — Cross-platform UI framework
- **iPad Optimization** — Landscape mode, full-screen support
- **Windows Integration** — Launch desktop apps from iPad
- **Category Filtering** — Search and organize apps
- **Installation Status** — View app availability
- **Hot Reload** — Instant development feedback

## 📚 Documentation

- **[iOS Build Guide](./iOS_BUILD_GUIDE.md)** — Complete iPad setup, development, and deployment
- **[Architecture](./ARCHITECTURE.md)** — System design, data flow, and integration points
- **[Windows Backend](./windows-backend/README.md)** — API documentation and setup

## 🔗 Windows Integration Architecture

```
iPad (iOS App)
      ↓ (HTTP REST API)
Windows Backend Service (Node.js/Express)
      ↓ (Process spawn)
Windows Desktop Applications
```

The Windows Backend runs on your Windows machine and:
1. Receives app launch requests from iOS
2. Validates application paths
3. Spawns the executable
4. Returns status to iPad device

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed technical documentation.

## 📦 Project Structure

```
edgebook/
├── ios/                    # iOS/React Native project
│   ├── app.json           # Expo configuration
│   ├── src/               # TypeScript components
│   ├── App.tsx            # Main app component
│   └── package.json       # iOS dependencies
├── windows-backend/        # Windows app launcher service
│   ├── server.ts          # Express.js API
│   └── package.json       # Node dependencies
├── electron/              # Electron main process
├── renderer/              # React UI (shared)
├── iOS_BUILD_GUIDE.md     # iPad setup guide
├── ARCHITECTURE.md        # System design
└── README.md             # This file
```

## 🚀 Getting Started

### For Windows Desktop Users
1. Clone the repository
2. Run `npm install` and `npm run dev`
3. Open apps from the App Store

### For iPad Users
1. On macOS with Xcode installed
2. Navigate to `ios/` directory
3. Run `npm install && npm run dev:ios`
4. Use iOS Simulator or physical device
5. Launch Windows apps via Windows Segment

### To Deploy Windows Backend
1. Navigate to `windows-backend/`
2. Run `npm install && npm run build`
3. Run on your Windows machine with `npm start`
4. Configure firewall to allow port 3000

## 🔒 Security Notes

Current implementation includes:
- Whitelist of supported applications
- Input validation on app IDs
- Audit logging of launches
- Process isolation

For production, add:
- HTTPS/TLS encryption
- JWT authentication
- Rate limiting
- Network segmentation

## 📋 System Requirements

### Windows Desktop
- Windows 10 or 11
- .NET Framework 4.6+
- ~200MB disk space

### iPad
- iOS 14 or later (iPad native app)
- or Expo Go (development)
- WiFi/LAN connectivity to Windows machine

### Windows Backend
- Windows 10 or 11
- Node.js 18+
- Administrator privileges for app launching

## 🛠️ Development

See detailed guides:
- **Windows**: Edit `electron/` and `renderer/`
- **iPad**: Edit `ios/src/`
- **Backend**: Edit `windows-backend/server.ts`

## 📄 License

All Rights Reserved - EdgeBook OS

---

**Latest Update**: December 2025
**Version**: 0.2.0 (iOS Preview)

## Project Structure

- `electron/` — Electron main + preload (TypeScript)
- `renderer/` — React UI via Vite
- `build/` — App resources (icon.ico)
- `dist/` — Compiled output
- `.vscode/tasks.json` — VS Code tasks
- `package.json` — Dependencies and scripts
