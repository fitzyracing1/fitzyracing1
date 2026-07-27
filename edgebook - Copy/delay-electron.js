const { spawn } = require('child_process');

// Wait 3 seconds for Vite to start, then launch Electron
setTimeout(() => {
  const electron = spawn('electron', ['.'], {
    stdio: 'inherit',
    shell: true
  });
  
  electron.on('error', (err) => {
    console.error('Electron error:', err);
    process.exit(1);
  });
  
  electron.on('exit', (code) => {
    process.exit(code);
  });
}, 3000);
