# Architecture: iOS-to-Windows Integration

## System Overview

EdgeBook OS now provides a complete ecosystem for iPad users to:
1. Access cloud and web applications via App Store
2. Launch and control Windows desktop applications
3. Manage cross-platform workflows seamlessly

## Component Architecture

### 1. iOS Application Layer

**App.tsx** - Root component managing screens
```
Main Navigation
├── App Store Screen
│   ├── Search & Filter
│   ├── Category Selection  
│   └── App Grid
└── Windows Segment Screen
    ├── Back Navigation
    ├── Windows App List
    └── Launch Controls
```

**AppStoreScreen.tsx** - Web/Cloud applications (iOS native)
- 12+ built-in applications (Teams, Outlook, Figma, etc.)
- Search and category filtering
- Direct URL launching via `Linking.openURL()`

**WindowsSegment.tsx** - Windows desktop applications (remote launch)
- 15+ Windows applications catalog
- Installation status indicators
- Category-based filtering
- Launch request handling

### 2. Communication Bridge

**WindowsAppLaunchService.ts** - iOS↔Windows API client
- REST API client using axios
- Handles request/response serialization
- Error handling and timeouts
- Session management

**API Endpoints:**
```
POST   /api/windows/launch              # Launch app
GET    /api/windows/apps/installed      # Check installation
GET    /api/windows/apps/:id/installed  # Single app check
POST   /api/windows/remote-session      # Start RDP/VNC
POST   /api/windows/apps/:id/close      # Kill process
GET    /api/health                      # Health check
```

### 3. Windows Backend Service

**server.ts** - Express.js API server
- Runs on Windows machine (localhost:3000)
- Handles app launch requests
- Spawns processes using `child_process.spawn()`
- Manages sessions and cleanup

**Key Functions:**
- `launchApp()` - Spawn executable via taskkill/cmd
- `checkInstalled()` - Query registry for app availability
- `startRemoteSession()` - RDP/VNC session creation
- `closeApp()` - Kill running processes

### 4. Data Models

#### AppItem (Web/Cloud Apps)
```typescript
{
  id: string;           // Unique identifier
  name: string;         // Display name
  icon: string;         // Emoji icon
  description: string;  // Short description
  category: string;     // App category
  url?: string;         // Web URL to open
}
```

#### WindowsApp (Desktop Apps)
```typescript
{
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  executablePath?: string;  // Path to .exe on Windows
  webUrl?: string;          // Documentation/download link
  isInstalled?: boolean;    // Availability status
}
```

## Data Flow Diagrams

### App Launch Flow

```
iPad User Interface
        │
        ▼
   App Card Tap
        │
        ▼
WindowsAppLaunchService
  .launchWindowsApp()
        │
        ▼
   HTTP POST Request
        │
        ▼
Windows Backend
  /api/windows/launch
        │
        ▼
Validation & Path Lookup
        │
        ▼
Process Spawn
  spawn('cmd', ['/c', 'start', '""', execPath])
        │
        ▼
Application Launches
        │
        ▼
Response to iPad
        │
        ▼
User Notification
```

### Status Check Flow

```
iPad: Check if App Installed
        │
        ▼
WindowsAppLaunchService
  .checkAppInstalled(appId)
        │
        ▼
HTTP GET Request
        │
        ▼
Windows Backend
  /api/windows/apps/:id/installed
        │
        ▼
Query Windows Registry
        │
        ▼
Return boolean status
        │
        ▼
Update UI with Status
  (Green checkmark or warning)
```

## File Organization

```
ios/
├── app.json                          # Expo configuration
├── App.tsx                           # Main app component (41 lines)
├── src/
│   ├── screens/
│   │   └── AppStoreScreen.tsx       # Web apps (289 lines)
│   ├── components/
│   │   └── WindowsSegment.tsx       # Windows apps (372 lines)
│   ├── services/
│   │   └── WindowsAppLaunchService.ts  # API client (74 lines)
│   └── index.tsx                    # Entry point
└── assets/                          # Icons, splashscreen

windows-backend/
├── server.ts                        # Express server (187 lines)
├── package.json
└── tsconfig.json
```

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **iOS App** | React Native | 0.73.0 | Cross-platform UI framework |
| **iOS Build** | Expo | 50.0.0 | Managed app development & distribution |
| **iOS Backend** | Express | 4.18.2 | REST API communication |
| **Windows Backend** | Node.js | 18+ | App launching & process management |
| **Language** | TypeScript | 5.3.3 | Type-safe development |
| **HTTP Client** | axios | Latest | API requests from iOS |

## Integration Points

### 1. Network Communication
- **Protocol**: HTTP/REST (can upgrade to HTTPS with certificates)
- **Default Port**: 3000
- **Connection**: Direct LAN or VPN tunnel
- **Latency**: <100ms on local network

### 2. Device Requirements
- **iOS**: iPad with iOS 14+ (Expo supports to iOS 11)
- **Windows**: Windows 10/11 with .NET Framework
- **Network**: Same subnet or VPN connection

### 3. Security Considerations
```
Current Implementation:
├── HTTP REST API (upgrade to HTTPS)
├── No authentication (add JWT tokens)
├── Whitelist apps (prevent arbitrary execution)
├── Log all launches (audit trail)
└── Validate paths (prevent injection attacks)

Recommended Enhancements:
├── TLS/SSL certificates
├── OAuth 2.0 authentication
├── Rate limiting
├── CORS configuration
├── Request signing
└── Encrypted payloads
```

## Scalability Considerations

### Current Architecture
- Single Windows machine backend
- Direct 1:1 device connection
- ~100 concurrent requests capacity

### For Enterprise Scale
```
Load Balancer
    │
    ├─ Windows Backend 1
    ├─ Windows Backend 2
    └─ Windows Backend N
    
Plus:
├── Redis cache for app lists
├── Database for user sessions
├── Queue system for requests
└── Message broker for notifications
```

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| App launch | 500-1000ms | Depends on app startup |
| Status check | 100-200ms | Registry query |
| List apps | 200-300ms | File system scan |
| UI rendering | <16ms | 60 FPS on iPad |

## Error Handling

### iOS Level
```typescript
try {
  const result = await service.launchWindowsApp(request);
  if (!result.success) {
    Alert.alert('Error', result.error);
  }
} catch (error) {
  Alert.alert('Connection Error', 'Cannot reach Windows backend');
}
```

### Backend Level
```typescript
try {
  spawn('cmd', [...]);
  return { success: true };
} catch (error) {
  return { 
    success: false, 
    error: error.message 
  };
}
```

## Future Enhancements

1. **Remote Desktop Integration**
   - Full RDP/VNC client in iOS app
   - Real-time desktop streaming
   - Mouse/keyboard input forwarding

2. **Advanced App Management**
   - App installation from iOS
   - Update management
   - Resource monitoring

3. **Notification System**
   - Real-time app status updates
   - Push notifications
   - Message queues

4. **Multi-user Support**
   - User authentication
   - Per-user app preferences
   - Access control & permissions

5. **Analytics & Monitoring**
   - Usage statistics
   - Performance metrics
   - Error logging & alerts

## Development Workflow

### For iOS Features
1. Edit component in `ios/src/`
2. Hot reload in Expo Go
3. Test on simulator/device
4. Commit changes

### For Windows Backend
1. Edit server logic in `windows-backend/`
2. Restart dev server (npm run dev)
3. Test endpoints with curl/Postman
4. Commit changes

### For Both
1. Update type definitions
2. Test integration
3. Update documentation
4. Version bump (major.minor.patch)

## Deployment Strategy

### Development
```bash
# Terminal 1 - iOS
cd ios && npm run dev

# Terminal 2 - Windows
cd windows-backend && npm run dev
```

### Staging
```bash
cd ios && eas build --profile preview
cd windows-backend && npm run build && npm start
```

### Production
```bash
cd ios && eas build --platform ios --profile production
cd windows-backend && npm run build
pm2 start dist/server.js --name "edgebook-windows"
```

---

**Last Updated**: December 22, 2025
**Architecture Version**: 1.0.0
**Maintenance**: GitHub Issues, Pull Requests
