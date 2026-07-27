import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('edgebook', {
  ping: () => 'pong',
  launchApp: (appId: string) => ipcRenderer.invoke('launch-app', appId)
});
