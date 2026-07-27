/**
 * Backend service for handling iOS to Windows communication
 * This Node.js/Express service runs on the Windows machine
 */

import express, { Request, Response } from 'express';
import { spawn } from 'child_process';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

// Store for active sessions
const activeSessions: Map<string, any> = new Map();

/**
 * Launch a Windows application
 */
app.post('/api/windows/launch', (req: Request, res: Response) => {
  const { appId, userId, deviceId } = req.body;

  if (!appId) {
    return res.status(400).json({
      success: false,
      message: 'appId is required',
      error: 'Missing appId parameter',
    });
  }

  const appPaths: { [key: string]: string } = {
    'vscode': 'C:\\Users\\[USER]\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
    'vs': 'C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe',
    'node': 'C:\\Program Files\\nodejs\\node.exe',
    'git': 'C:\\Program Files\\Git\\bin\\git.exe',
    'powershell': 'C:\\Program Files\\PowerShell\\7\\pwsh.exe',
    'docker': 'C:\\Program Files\\Docker\\Docker\\Docker.exe',
    'vlc': 'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',
    'photoshop': 'C:\\Program Files\\Adobe\\Adobe Photoshop [Version]\\Photoshop.exe',
    'blender': 'C:\\Program Files\\Blender Foundation\\Blender [Version]\\blender.exe',
  };

  const executablePath = appPaths[appId];

  if (!executablePath) {
    return res.status(404).json({
      success: false,
      message: `Application '${appId}' not found`,
      appId,
      launchedAt: new Date().toISOString(),
      error: 'Unknown application ID',
    });
  }

  try {
    // Spawn the application
    const child = spawn('cmd.exe', ['/c', 'start', '""', executablePath], {
      detached: true,
      stdio: 'ignore',
    });

    child.unref();

    res.json({
      success: true,
      message: `${appId} launched successfully`,
      appId,
      launchedAt: new Date().toISOString(),
    });

    console.log(`[${new Date().toISOString()}] Launched app: ${appId} for user: ${userId}`);
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to launch application',
      appId,
      launchedAt: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * Check if an application is installed
 */
app.get('/api/windows/apps/:appId/installed', (req: Request, res: Response) => {
  const { appId } = req.params;

  // In a real implementation, this would check the Windows registry or file system
  const installedApps = [
    'vscode',
    'node',
    'git',
    'powershell',
    'vlc',
  ];

  const isInstalled = installedApps.includes(appId);

  res.json({
    appId,
    installed: isInstalled,
  });
});

/**
 * Get list of installed applications
 */
app.get('/api/windows/apps/installed', (req: Request, res: Response) => {
  // In a real implementation, this would query Windows registry
  const installedApps = [
    {
      id: 'vscode',
      name: 'Visual Studio Code',
      executablePath: 'C:\\Users\\[USER]\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
      isRunning: false,
    },
    {
      id: 'node',
      name: 'Node.js',
      executablePath: 'C:\\Program Files\\nodejs\\node.exe',
      isRunning: false,
    },
    {
      id: 'git',
      name: 'Git',
      executablePath: 'C:\\Program Files\\Git\\bin\\git.exe',
      isRunning: false,
    },
  ];

  res.json({
    apps: installedApps,
  });
});

/**
 * Start a remote session
 */
app.post('/api/windows/remote-session', (req: Request, res: Response) => {
  const { userId, deviceId, sessionType } = req.body;

  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Store session info
  activeSessions.set(sessionId, {
    userId,
    deviceId,
    sessionType,
    createdAt: new Date(),
  });

  res.json({
    sessionId,
    url: `rdp://localhost:3389?sessionId=${sessionId}`,
  });

  console.log(`[${new Date().toISOString()}] Started remote session: ${sessionId}`);
});

/**
 * Close an application
 */
app.post('/api/windows/apps/:appId/close', (req: Request, res: Response) => {
  const { appId } = req.params;

  try {
    spawn('taskkill', ['/IM', `${appId}.exe`, '/F'], {
      stdio: 'ignore',
    });

    res.json({
      success: true,
      message: `${appId} closed successfully`,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to close application',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * Health check endpoint
 */
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    activeSessions: activeSessions.size,
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`EdgeBook Windows App Service running on http://localhost:${PORT}`);
  console.log('Ready to receive requests from iOS devices');
});
