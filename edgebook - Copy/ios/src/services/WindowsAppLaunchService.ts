import axios, { AxiosInstance } from 'axios';

export interface LaunchAppRequest {
  appId: string;
  userId: string;
  deviceId: string;
}

export interface LaunchAppResponse {
  success: boolean;
  message: string;
  appId: string;
  launchedAt: string;
  error?: string;
}

export interface WindowsAppInfo {
  id: string;
  name: string;
  executablePath: string;
  isRunning: boolean;
  lastLaunchTime?: string;
}

class WindowsAppLaunchService {
  private apiClient: AxiosInstance;
  private apiBaseUrl: string;

  constructor(baseUrl: string = 'http://localhost:3000/api') {
    this.apiBaseUrl = baseUrl;
    this.apiClient = axios.create({
      baseURL: this.apiBaseUrl,
      timeout: 5000,
    });
  }

  /**
   * Launch a Windows application from iOS device
   * This communicates with your Windows backend service
   */
  async launchWindowsApp(request: LaunchAppRequest): Promise<LaunchAppResponse> {
    try {
      const response = await this.apiClient.post('/windows/launch', request);
      return response.data;
    } catch (error) {
      return {
        success: false,
        message: 'Failed to launch app',
        appId: request.appId,
        launchedAt: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Check if a Windows application is installed
   */
  async checkAppInstalled(appId: string): Promise<boolean> {
    try {
      const response = await this.apiClient.get(`/windows/apps/${appId}/installed`);
      return response.data.installed;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get list of installed Windows applications
   */
  async getInstalledApps(): Promise<WindowsAppInfo[]> {
    try {
      const response = await this.apiClient.get('/windows/apps/installed');
      return response.data.apps;
    } catch (error) {
      return [];
    }
  }

  /**
   * Start a remote session to control Windows desktop
   */
  async startRemoteSession(sessionConfig: {
    userId: string;
    deviceId: string;
    sessionType: 'rdp' | 'vnc' | 'custom';
  }): Promise<{ sessionId: string; url: string }> {
    try {
      const response = await this.apiClient.post('/windows/remote-session', sessionConfig);
      return response.data;
    } catch (error) {
      throw new Error('Failed to start remote session');
    }
  }

  /**
   * Close a running Windows application
   */
  async closeWindowsApp(appId: string): Promise<boolean> {
    try {
      const response = await this.apiClient.post(`/windows/apps/${appId}/close`);
      return response.data.success;
    } catch (error) {
      return false;
    }
  }
}

export default WindowsAppLaunchService;
