import React, { useState } from 'react';
import AppStore from './AppStore';

declare global {
  interface Window {
    edgebook?: { 
      ping: () => string;
      launchApp: (appId: string) => Promise<{ success: boolean; error?: string }>;
    };
  }
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'home' | 'appstore'>('appstore');

  return (
    <div style={{ height: '100vh', overflow: 'hidden' }}>
      {currentScreen === 'home' && (
        <div style={{ fontFamily: 'system-ui', padding: 24 }}>
          <h1>EdgeBook OS</h1>
          <p>Electron + React + Vite is running.</p>
          <p>Preload says: {window.edgebook?.ping?.()}</p>
          <button onClick={() => setCurrentScreen('appstore')}>
            Open App Store
          </button>
        </div>
      )}
      
      {currentScreen === 'appstore' && (
        <div>
          <AppStore />
        </div>
      )}
    </div>
  );
}
