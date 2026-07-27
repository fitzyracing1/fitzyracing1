# EdgeBook OS - Visual Guide

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        EDGEBOOK OS v0.2.0                        │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐     ┌──────────────────────────┐
│     WINDOWS DESKTOP             │     │      IPAD (iOS)          │
│   (Electron + React)            │     │  (React Native + Expo)   │
│                                 │     │                          │
│ ┌──────────────────────────────┐│     │ ┌────────────────────────│
│ │    App Store                 ││     │ │ App Store              │
│ │ - Microsoft Edge             ││     │ │ - Teams   - Outlook    │
│ │ - Teams                      ││     │ │ - OneDrive - Figma    │
│ │ - OneDrive                   ││     │ │ - Netflix - Spotify   │
│ │ - etc.                       ││     │ │ - and more...          │
│ └──────────────────────────────┘│     │ └────────────────────────│
│                                 │     │ ┌────────────────────────│
│                                 │     │ │ Windows Segment [NEW]  │
│                                 │     │ │ - VS Code              │
│                                 │     │ │ - Docker               │
│                                 │     │ │ - Node.js              │
│                                 │     │ │ - Git                  │
│                                 │     │ │ - PowerShell           │
│                                 │     │ │ - and more...          │
│                                 │     │ └────────────────────────│
│                                 │     │                          │
└─────────────────────────────────┘     └──────────────────────────┘
          ▲                                        ▲
          │                                        │
          └────────────────────────────────────────┘
          │         Network (WiFi/VPN)             │
          └────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│         Windows Backend Service (Node.js/Express)                │
│                 Runs on Windows Machine                          │
│                                                                  │
│  GET /health                    ← Health checks                 │
│  POST /windows/launch           ← Launch apps                   │
│  GET /windows/apps/installed    ← Check installations           │
│  POST /windows/remote-session   ← RDP/VNC sessions            │
│  POST /windows/apps/:id/close   ← Close apps                   │
└──────────────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│             Windows Desktop Applications                         │
│                                                                  │
│  [VS Code]  [Docker]  [Git]  [Node.js]  [PowerShell]  [etc.]  │
└──────────────────────────────────────────────────────────────────┘
```

## iOS User Interface Flow

```
┌─────────────────────────────────────────────┐
│   EdgeBook OS (iPad Landscape)              │
├─────────────────────────────────────────────┤
│                                             │
│  [Back] ← Home / App Store                │
│                                             │
│  Search: [________________]                 │
│                                             │
│  Categories: [All] [Productivity]         │
│             [Communication] [Design]      │
│             [Development]   [Windows...] │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Teams    │  │ Outlook  │  │ OneDrive ││
│  │   👥    │  │    📧    │  │    ☁️    ││
│  │ Communic│  │ Productiv│  │ Storage  ││
│  └──────────┘  └──────────┘  └──────────┘│
│  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ VS Code  │  │ Docker   │  │ Git      ││
│  │   💻    │  │    🐳    │  │   📦    ││
│  │ Development          │  │Development
│  └──────────┘  └──────────┘  └──────────┘│
│  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Node.js  │  │PowerShell│  │ Blender  ││
│  │   ⚙️    │  │   🖥️    │  │   🎬    ││
│  │ Development  System   Design          │
│  └──────────┘  └──────────┘  └──────────┘│
│                                             │
└─────────────────────────────────────────────┘
```

## Windows App Launching Sequence

```
┌────────────────┐
│  iPad Screen   │
│  [VS Code]     │  ← User taps VS Code app
└────────────────┘
        │
        │ onPress()
        ▼
┌─────────────────────────────────────────────┐
│ handleLaunchApp(appId: 'vscode')           │
└─────────────────────────────────────────────┘
        │
        │ Check if installed
        ▼
        │
        ├─ YES → Show loading indicator
        │        Prepare launch request
        │
        └─ NO  → Show installation warning
                 Offer documentation link

        │
        │ (YES path)
        ▼
┌─────────────────────────────────────────────┐
│ HTTP POST /api/windows/launch               │
│ {                                           │
│   "appId": "vscode",                       │
│   "userId": "john-doe",                    │
│   "deviceId": "iPad-Pro"                   │
│ }                                          │
└─────────────────────────────────────────────┘
        │ Network transmission
        ▼
┌─────────────────────────────────────────────┐
│ Windows Backend Receives Request            │
│                                             │
│ 1. Validate appId exists                   │
│ 2. Look up executable path                 │
│ 3. Spawn process: Code.exe                 │
│ 4. Return success response                 │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ Response: HTTP 200 OK                       │
│ {                                           │
│   "success": true,                         │
│   "message": "vscode launched...",         │
│   "appId": "vscode",                       │
│   "launchedAt": "2024-12-22T10:30:45Z"    │
│ }                                          │
└─────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│ iPad Shows Success Indicator    │
│ ✓ VS Code Launched             │
│ (Auto-dismiss after 2 seconds)  │
└────────────────────────────────┘

┌────────────────────────────────┐
│ Windows Desktop                │
│ [VS Code Window Opens]         │
│                                │
│ Welcome to Visual Studio Code  │
│                                │
│ File  Edit  View  Debug  Help  │
│                                │
│ Ready to use!                  │
└────────────────────────────────┘
```

## Component Hierarchy

```
EdgeBook iOS App
│
├─ App.tsx (Main Router)
│  │
│  ├─ Screen: "appstore"
│  │  └─ AppStoreScreen.tsx
│  │     ├─ SearchInput
│  │     ├─ CategoryFilter
│  │     │  ├─ [All]
│  │     │  ├─ [Productivity]
│  │     │  ├─ [Communication]
│  │     │  └─ [Windows Apps] ← NEW
│  │     └─ AppGrid
│  │        ├─ [AppCard]
│  │        ├─ [AppCard]
│  │        └─ [AppCard]
│  │           │
│  │           ├─ icon
│  │           ├─ name
│  │           ├─ description
│  │           └─ category
│  │
│  └─ Screen: "windows-segment"
│     └─ WindowsSegment.tsx ← NEW
│        ├─ Header with Back Button
│        ├─ SearchInput
│        ├─ CategoryFilter
│        │  ├─ [All]
│        │  ├─ [Development]
│        │  ├─ [System]
│        │  ├─ [Design]
│        │  └─ [Media]
│        └─ AppsList (FlatList)
│           ├─ [AppCard]
│           │  ├─ icon
│           │  ├─ name
│           │  ├─ description
│           │  ├─ installed status ← NEW
│           │  └─ category
│           └─ [AppCard]
│
└─ Services
   └─ WindowsAppLaunchService.ts ← NEW
      ├─ launchWindowsApp()
      ├─ checkAppInstalled()
      ├─ getInstalledApps()
      ├─ startRemoteSession()
      └─ closeWindowsApp()
```

## File Organization Chart

```
edgebook/
│
├── iOS Platform
│   └── ios/
│       ├── app.json ..................... Expo configuration
│       ├── App.tsx ....................... Main app component (41 lines)
│       ├── eas.json ..................... EAS Build config
│       ├── package.json ................. iOS dependencies
│       ├── tsconfig.json ................ TypeScript config
│       │
│       └── src/
│           ├── screens/
│           │   └── AppStoreScreen.tsx ... Web apps UI (289 lines)
│           │
│           ├── components/
│           │   └── WindowsSegment.tsx .. Windows apps UI (372 lines) ⭐ NEW
│           │
│           ├── services/
│           │   └── WindowsAppLaunchService.ts . API bridge (74 lines) ⭐ NEW
│           │
│           └── index.tsx
│
├── Windows Backend
│   └── windows-backend/
│       ├── server.ts .................... Express API (187 lines) ⭐ NEW
│       ├── package.json ................. Node dependencies ⭐ NEW
│       ├── tsconfig.json ................ TypeScript config ⭐ NEW
│       └── README.md .................... API docs ⭐ NEW
│
├── Desktop (Existing)
│   ├── electron/ ....................... Electron main
│   └── renderer/ ....................... React UI
│
├── Documentation
│   ├── README.md ....................... Main guide (UPDATED)
│   ├── iOS_BUILD_GUIDE.md ............. Setup guide (400+ lines) ⭐ NEW
│   ├── ARCHITECTURE.md ................ Technical design (500+ lines) ⭐ NEW
│   ├── WINDOWS_INTEGRATION.md ......... Integration guide (600+ lines) ⭐ NEW
│   ├── IMPLEMENTATION_SUMMARY.md ...... This summary ⭐ NEW
│   └── COMMANDS.md .................... Quick reference ⭐ NEW
│
└── Setup Scripts
    ├── setup.bat ...................... Windows setup ⭐ NEW
    ├── setup.sh ....................... macOS/Linux setup ⭐ NEW
    └── dev-servers.sh ................. Dev starter ⭐ NEW
```

## Data Flow: App Launch

```
┌──────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                 │
└──────────────────────────────────────────────────────────────────┘

Step 1: USER ACTION
───────────────────
    iPad User
         │
         ▼
    Taps "VS Code" Button
         │
         └──→ Sets appId = 'vscode'


Step 2: SERVICE CALL
─────────────────────
    handleLaunchApp(appId)
         │
         ▼
    WindowsAppLaunchService.launchWindowsApp({
      appId: 'vscode',
      userId: 'john-doe',
      deviceId: 'iPad-Pro-12.9'
    })
         │
         ▼
    axios.post(
      'http://192.168.1.100:3000/api/windows/launch',
      {...}
    )


Step 3: NETWORK TRANSMISSION
──────────────────────────────
    iOS ──(HTTPS POST)──> Windows Backend
              {
                "appId": "vscode",
                "userId": "john-doe",
                "deviceId": "iPad-Pro-12.9"
              }


Step 4: BACKEND PROCESSING
────────────────────────────
    POST /api/windows/launch
         │
         ├──→ Parse request body
         ├──→ Validate appId in whitelist
         ├──→ Look up executable path
         │    appPaths['vscode'] = 'C:\...\Code.exe'
         ├──→ Check path exists
         └──→ Spawn process
              spawn('cmd.exe', [
                '/c',
                'start',
                '""',
                'C:\...\Code.exe'
              ])


Step 5: RESPONSE
─────────────────
    Windows Backend
         │
         ▼
    Success Response:
    {
      "success": true,
      "message": "vscode launched successfully",
      "appId": "vscode",
      "launchedAt": "2024-12-22T10:30:45.123Z"
    }
         │
         └──(HTTP 200)──> iOS


Step 6: UI FEEDBACK
────────────────────
    iOS Receives Response
         │
         ├──→ success === true?
         │    YES: Show success notification
         │        ✓ VS Code Launched
         │    NO:  Show error alert
         │        Error: {message}
         │
         └──→ Auto-dismiss or wait for user


Step 7: WINDOWS DESKTOP
────────────────────────
    Process Spawns
         │
         ▼
    VS Code Executable Launches
         │
         ▼
    Window Appears on Desktop
         │
         ▼
    Ready to Use!
```

## Windows Segment App Categories

```
┌─────────────────────────────────────────────────────────────────┐
│              Windows Segment - App Categories                   │
└─────────────────────────────────────────────────────────────────┘

DEVELOPMENT (6 apps)
├─ 💻 Visual Studio Code        [Installed] ✓
├─ 🔧 Visual Studio 2022        [Not Installed] ○
├─ ⚙️  Node.js                  [Installed] ✓
├─ 📦 Git                       [Installed] ✓
├─ 🐳 Docker Desktop            [Not Installed] ○
└─ ☁️  Azure CLI                [Not Installed] ○

SYSTEM (4 apps)
├─ 🖥️  PowerShell 7             [Installed] ✓
├─ ⌨️  Windows Terminal          [Installed] ✓
├─ 🐧 Windows Subsystem Linux   [Not Installed] ○
└─ 🖨️  Hyper-V                  [Not Installed] ○

DESIGN (3 apps)
├─ 🎨 Adobe Photoshop           [Not Installed] ○
├─ ✏️  Adobe Illustrator         [Not Installed] ○
└─ 🎬 Blender                   [Not Installed] ○

MEDIA (3 apps)
├─ 📹 OBS Studio                [Not Installed] ○
├─ 🎥 FFmpeg                    [Not Installed] ○
└─ ▶️  VLC Media Player          [Installed] ✓

LEGEND:
✓ = Installed (tap to launch)
○ = Not Installed (shows installation info)
```

## Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

Local Network (WiFi) - Development
───────────────────────────────────
    iPad (192.168.1.50)
           │
           │ HTTP (port 8081)
           │
        WiFi Router
           │
           │ HTTP (port 3000)
           │
    Windows PC (192.168.1.100)
           │
           ├─ Express Backend
           │  └─ Windows Apps


Cloud Network (VPN) - Production
──────────────────────────────────
    iPad (Mobile Network)
           │
           │ HTTPS (port 443)
           │
        VPN Tunnel
           │
        VPN Gateway
           │
           │ HTTPS (port 443)
           │
    Corporate Network
           │
           ├─ Express Backend (Secured)
           │  └─ Windows Apps (Firewalled)


Connection Details
──────────────────
Protocol:      HTTP or HTTPS
Port:          3000 (HTTP) or 443 (HTTPS)
Timeout:       5 seconds
Retry:         Yes, with exponential backoff
Compression:   GZIP (future)
```

## Deployment Environments

```
DEVELOPMENT
────────────
iPad (Simulator)
    ↓
Expo Go (localhost:8081)
    ↓
Windows Backend (localhost:3000)
    ↓
Local Windows Apps

STAGING
────────
iPad (Build Preview)
    ↓
Expo Preview Build
    ↓
Windows Backend (staging.yourcompany.com)
    ↓
Staging Windows Apps

PRODUCTION
───────────
iPad (App Store)
    ↓
App Store Version
    ↓
Windows Backend (windows.yourcompany.com)
    ↓
Production Windows Apps
```

## Feature Timeline

```
Version 0.1.0 (Original)
├─ Electron Desktop App
└─ Windows App Store

Version 0.2.0 (Current)
├─ iOS React Native App
├─ Expo Framework
├─ App Store UI (iPad)
├─ Windows Segment ⭐ NEW
├─ iOS↔Windows Bridge ⭐ NEW
├─ Windows Backend Service ⭐ NEW
├─ 15+ Windows Apps ⭐ NEW
└─ Comprehensive Documentation ⭐ NEW

Version 0.3.0 (Planned)
├─ Remote Desktop (RDP/VNC)
├─ App Installation Management
├─ Real-time App Monitoring
└─ Multi-user Authentication

Version 1.0.0 (Planned)
├─ App Store Submission
├─ Production Deployment
├─ Analytics & Monitoring
└─ Enterprise Features
```

---

**Visual Guide Complete** ✓  
Use these diagrams as reference for understanding the system architecture!
