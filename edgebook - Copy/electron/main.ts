import { app, BrowserWindow, ipcMain, shell } from 'electron';
import path from 'path';

let mainWindow: BrowserWindow | null = null;

const launchApp = async (appId: string) => {
  const appPaths: { [key: string]: string } = {
    'edge': 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'edge-alt': 'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'teams': 'https://www.microsoft.com/teams/download',
    'outlook': 'https://outlook.live.com',
    'onenote': 'https://www.onenote.com',
    'onedrive': 'https://onedrive.live.com',
    'copilot': 'https://copilot.microsoft.com',
    'netflix': 'https://www.netflix.com',
    'spotify': 'https://www.spotify.com',
    'discord': 'https://discord.com/download',
    'slack': 'https://slack.com/download',
    'notion': 'https://www.notion.so',
    'figma': 'https://www.figma.com'
  };

  const appPath = appPaths[appId];
  
  if (!appPath) {
    console.error(`Unknown app: ${appId}`);
    return { success: false, error: 'App not found' };
  }

  try {
    // All apps open via URL - either to web app or download page
    await shell.openExternal(appPath);
    return { success: true };
  } catch (err) {
    console.error(`Failed to launch ${appId}:`, err);
    return { success: false, error: String(err) };
  }
};

ipcMain.handle('launch-app', async (event, appId: string) => {
  return await launchApp(appId);
});

const createWindow = () => {
  const iconPath = path.join(__dirname, '..', 'build', 'icon.ico');
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 640,
    icon: iconPath,
    webPreferences: {
      preload: path.join(app.getAppPath(), 'dist', 'main', 'preload.js'),
      sandbox: false,
      contextIsolation: true
    }
  });

  const isDev = !app.isPackaged;
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173/');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(app.getAppPath(), 'dist', 'renderer', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
