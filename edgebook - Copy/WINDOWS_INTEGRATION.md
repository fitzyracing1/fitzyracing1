# iOS to Windows Integration Guide

Complete guide to the Windows App launching system from iPad.

## Overview

The Windows App integration allows iPad users to launch and control Windows desktop applications through a simple, intuitive interface called the **Windows Segment**.

## How It Works

### Step 1: User Taps Windows App (iPad)
```
┌─────────────────┐
│  Windows Segment│
├─────────────────┤
│ [VS Code]       │
│ [Docker]        │
│ [Git]           │
│ [Node.js]       │
│ ...             │
└─────────────────┘
     │ User taps
     ▼
handleLaunchApp(appId)
```

### Step 2: iOS Sends Request to Windows Backend
```typescript
// iOS Code
const service = new WindowsAppLaunchService('http://192.168.1.100:3000/api');
const response = await service.launchWindowsApp({
  appId: 'vscode',
  userId: 'john-doe',
  deviceId: 'iPad-Pro-12.9'
});
```

**HTTP Request:**
```http
POST http://192.168.1.100:3000/api/windows/launch
Content-Type: application/json

{
  "appId": "vscode",
  "userId": "john-doe",
  "deviceId": "iPad-Pro-12.9"
}
```

### Step 3: Windows Backend Launches Application
```typescript
// Windows Backend Code
const executablePath = 'C:\\Users\\YourName\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe';
const child = spawn('cmd.exe', ['/c', 'start', '""', executablePath], {
  detached: true,
  stdio: 'ignore',
});
child.unref();
```

### Step 4: Application Opens on Windows
```
Windows Desktop
┌──────────────────────┐
│  [Visual Studio Code]│  ← Opens on Windows machine
│                      │
│  Ready to use!       │
└──────────────────────┘
```

### Step 5: Response Sent Back to iPad
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "vscode launched successfully",
  "appId": "vscode",
  "launchedAt": "2024-12-22T10:30:45.123Z"
}
```

### Step 6: User Notification
```
iPad Screen
┌─────────────────────┐
│ ✓ VS Code Launched  │  ← User feedback
└─────────────────────┘
```

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        iPad (iOS)                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ User Interface                                           │  │
│  │ ┌─────────────────────────────────────────────────────┐ │  │
│  │ │  Windows Segment Screen                           │ │  │
│  │ │  [VS Code] [Docker] [Git] [Node.js] ...           │ │  │
│  │ │                                                     │ │  │
│  │ │ User taps "VS Code" button                        │ │  │
│  │ └─────────────────────────────────────────────────────┘ │  │
│  │              ↓ onPress handler                        │  │
│  │ ┌─────────────────────────────────────────────────────┐ │  │
│  │ │ WindowsAppLaunchService.launchWindowsApp()        │ │  │
│  │ └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│                   HTTP POST Request                            │
│                (async axios call)                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    Network/WiFi
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Windows Machine                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Express.js Server (Port 3000)                           │  │
│  │ ┌──────────────────────────────────────────────────────┤  │
│  │ │ POST /api/windows/launch Handler                   │  │
│  │ │                                                   │  │
│  │ │ 1. Parse request body                            │  │
│  │ │    appId = "vscode"                              │  │
│  │ │    userId = "john-doe"                           │  │
│  │ │    deviceId = "iPad-Pro"                         │  │
│  │ │                                                   │  │
│  │ │ 2. Look up executable path                       │  │
│  │ │    path = appPaths["vscode"]                      │  │
│  │ │    = "C:\\...\\Microsoft VS Code\\Code.exe"      │  │
│  │ │                                                   │  │
│  │ │ 3. Spawn process                                 │  │
│  │ │    spawn('cmd.exe', ['/c', 'start', path])       │  │
│  │ │                                                   │  │
│  │ │ 4. Return success response                       │  │
│  │ │    { success: true, message: "...", ...}         │  │
│  │ └──────────────────────────────────────────────────┘  │
│  │               ↓                                         │  │
│  │ ┌──────────────────────────────────────────────────────┐  │
│  │ │ Windows Process Manager                           │  │
│  │ │ ┌────────────────────────────────────────────────┐ │  │
│  │ │ │ Spawns: Code.exe                             │ │  │
│  │ │ │ Process ID: 12345                            │ │  │
│  │ │ │ Status: Running                              │ │  │
│  │ │ └────────────────────────────────────────────────┘ │  │
│  │ └──────────────────────────────────────────────────────┘  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Desktop Applications                                     │  │
│  │ ┌──────────────────────────────────────────────────────┤  │
│  │ │  [VS Code Window]                                 │  │
│  │ │  ┌─────────────────────────────────────────────────│  │
│  │ │  │ Welcome to Visual Studio Code                 │  │
│  │ │  │                                                 │  │
│  │ │  │ Files    Edit    View    Debug    Help        │  │
│  │ │  └─────────────────────────────────────────────────│  │
│  │ │                                                   │  │
│  │ │  Ready to use!                                  │  │
│  │ │                                                   │  │
│  │ └──────────────────────────────────────────────────┘  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

### iPad Side (ios/src/components/WindowsSegment.tsx)

Define apps to display:
```typescript
const windowsAppsData: WindowsApp[] = [
  {
    id: 'vscode',
    name: 'Visual Studio Code',
    description: 'Lightweight code editor',
    icon: '💻',
    category: 'Development',
    executablePath: 'C:\\Users\\[USER]\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
    isInstalled: true,
  },
  // ... more apps
];
```

### Windows Backend Side (windows-backend/server.ts)

Define executable paths:
```typescript
const appPaths: { [key: string]: string } = {
  'vscode': 'C:\\Users\\YourName\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
  'docker': 'C:\\Program Files\\Docker\\Docker\\Docker.exe',
  'git': 'C:\\Program Files\\Git\\bin\\git.exe',
  // ... more apps
};
```

**Important**: The `id` must match on both sides!

## Adding New Applications

### 1. Add to Windows Backend
Edit `windows-backend/server.ts`:
```typescript
const appPaths: { [key: string]: string } = {
  // ... existing apps
  'my-app': 'C:\\Path\\To\\MyApp.exe',
};
```

### 2. Add to iOS App Catalog
Edit `ios/src/components/WindowsSegment.tsx`:
```typescript
const windowsAppsData: WindowsApp[] = [
  // ... existing apps
  {
    id: 'my-app',
    name: 'My Application',
    description: 'What it does',
    icon: '🚀',
    category: 'Development',
    executablePath: 'C:\\Path\\To\\MyApp.exe',
    isInstalled: true,
  },
];
```

### 3. Test
1. Restart Windows Backend: `npm run dev`
2. Reload iOS app in Expo
3. Tap the app in Windows Segment
4. Verify it launches on Windows

## Network Configuration

### Local Network (Same WiFi)

**Recommended for development:**

1. Find Windows machine IP address:
   ```powershell
   ipconfig
   # Look for IPv4 Address: 192.168.x.x
   ```

2. Update iOS service configuration:
   ```typescript
   const service = new WindowsAppLaunchService('http://192.168.1.100:3000/api');
   ```

3. Verify connectivity:
   ```bash
   # From iPad terminal (or use Expo CLI)
   curl http://192.168.1.100:3000/api/health
   ```

### VPN/Remote Network

**For production or remote access:**

1. Set up VPN tunnel between iPad and Windows network
2. Use VPN IP address or hostname:
   ```typescript
   const service = new WindowsAppLaunchService('https://vpn.yourdomain.com:3000/api');
   ```

3. Enable HTTPS and firewall rules

## Troubleshooting

### App Won't Launch

**Symptom**: Tap app button, nothing happens

**Solutions**:
1. Check Windows Backend is running:
   ```bash
   curl http://192.168.1.100:3000/api/health
   ```

2. Verify executable path is correct:
   ```powershell
   # On Windows, test if path exists
   Test-Path "C:\Path\To\App.exe"
   ```

3. Check app ID matches on both sides

4. Look at Windows Backend logs for errors

### Network Connection Failed

**Symptom**: "Cannot reach Windows backend" error on iPad

**Solutions**:
1. Verify Windows IP address
2. Check firewall allows port 3000:
   ```powershell
   netsh advfirewall firewall add rule name="EdgeBook Port 3000" `
     dir=in action=allow protocol=tcp localport=3000
   ```

3. Test from iPad:
   ```bash
   ping 192.168.1.100
   curl http://192.168.1.100:3000/api/health
   ```

4. Check both devices on same network

### App Shows "Not Installed"

**Symptom**: Installation indicator shows red "Not Installed"

**Solutions**:
1. Install the application on Windows
2. Update `isInstalled: true` in app definition
3. Or update backend to check actual installation:
   ```typescript
   // Query Windows registry
   const installed = checkWindowsRegistry(appId);
   ```

## Security Considerations

### Current Implementation
- HTTP (unencrypted)
- No authentication
- All users can launch apps
- App whitelist prevents arbitrary execution

### For Production, Add:

1. **HTTPS/TLS**
   ```typescript
   import https from 'https';
   const server = https.createServer(httpsOptions, app);
   ```

2. **Authentication**
   ```typescript
   app.post('/api/windows/launch', authenticate, (req, res) => {
     // Only authenticated users can launch apps
   });
   ```

3. **Rate Limiting**
   ```typescript
   import rateLimit from 'express-rate-limit';
   const limiter = rateLimit({
     windowMs: 60 * 1000,
     max: 10 // 10 requests per minute
   });
   ```

4. **Request Signing**
   ```typescript
   // Sign requests with HMAC-SHA256
   const signature = crypto
     .createHmac('sha256', secret)
     .update(payload)
     .digest('hex');
   ```

5. **Audit Logging**
   ```typescript
   logger.info(`App launch: ${appId} by ${userId} from ${deviceId}`);
   ```

## Performance Optimization

### iPad Side
- Use `FlatList` for app list (already implemented)
- Memoize filtered results
- Lazy load app metadata
- Debounce search input

### Windows Backend
- Use worker threads for heavy operations
- Cache app registry queries
- Implement connection pooling
- Monitor memory usage

### Network
- Enable HTTP compression
- Implement request batching
- Use WebSocket for real-time updates
- Add request caching headers

## Testing the Integration

### Manual Testing

1. **Backend Health Check**
   ```bash
   curl http://192.168.1.100:3000/api/health
   
   # Expected: { status: 'ok', timestamp: '...', activeSessions: 0 }
   ```

2. **Launch App**
   ```bash
   curl -X POST http://192.168.1.100:3000/api/windows/launch \
     -H "Content-Type: application/json" \
     -d '{
       "appId": "vscode",
       "userId": "test-user",
       "deviceId": "test-device"
     }'
   
   # Expected: { success: true, message: "...", appId: "vscode", ... }
   ```

3. **Check Installation**
   ```bash
   curl http://192.168.1.100:3000/api/windows/apps/vscode/installed
   
   # Expected: { appId: 'vscode', installed: true }
   ```

4. **List Installed Apps**
   ```bash
   curl http://192.168.1.100:3000/api/windows/apps/installed
   
   # Expected: { apps: [...] }
   ```

### Automated Testing

Create test file `windows-backend/test.ts`:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',
  timeout: 5000,
});

async function test() {
  try {
    // Test health
    const health = await api.get('/health');
    console.log('✓ Health check passed');

    // Test app launch
    const launch = await api.post('/windows/launch', {
      appId: 'vscode',
      userId: 'test',
      deviceId: 'test',
    });
    console.log('✓ App launch request succeeded');

  } catch (error) {
    console.error('✗ Test failed:', error);
  }
}

test();
```

## Advanced Features

### Remote Desktop Integration (Future)

```typescript
// Start RDP session
const session = await service.startRemoteSession({
  userId: 'john',
  deviceId: 'iPad-Pro',
  sessionType: 'rdp',
});

// Opens RDP client to Windows desktop
Linking.openURL(`rdp://${session.url}`);
```

### App Process Monitoring (Future)

```typescript
// Track running apps
const status = await api.get('/windows/apps/vscode/status');
// { isRunning: true, pid: 12345, memory: 256, cpu: 5 }
```

### File Transfer (Future)

```typescript
// Send files from iPad to Windows app
await api.post('/windows/apps/vscode/files', {
  sourceFile: 'file:///path/on/ipad',
  destinationPath: 'C:\\Users\\Desktop\\',
});
```

## Monitoring & Logging

### iPad Side
```typescript
// Log all app launches
window.addEventListener('applaunch', (event) => {
  console.log(`Launched: ${event.appId} at ${event.timestamp}`);
});
```

### Windows Backend
```typescript
// Log to file
import fs from 'fs';
const logStream = fs.createWriteStream('launches.log', { flags: 'a' });
logStream.write(`${timestamp}: Launched ${appId} for ${userId}\n`);
```

### Monitoring Dashboard (Future)
```
┌──────────────────────────────────────┐
│  EdgeBook Windows App Monitor        │
├──────────────────────────────────────┤
│ Status: Online                       │
│ Active Sessions: 2                   │
│ Apps Launched (today): 15            │
│ Performance: Good                    │
│                                      │
│ Recent Launches:                     │
│  - VS Code (2 min ago)              │
│  - Docker (5 min ago)               │
│  - Git (1 hour ago)                 │
└──────────────────────────────────────┘
```

---

**Version**: 1.0.0
**Last Updated**: December 2025
**Support**: See iOS_BUILD_GUIDE.md and ARCHITECTURE.md
