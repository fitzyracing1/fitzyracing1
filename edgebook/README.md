# EdgeBook OS

A Windows-friendly Electron + React + TypeScript app with Microsoft Edge WebView2 engine and an integrated App Store, scaffolded with Vite.

## Quick Start

```powershell
# From the project root
npm install
npm run dev
```

This opens the Electron window with Microsoft Edge WebView2 and serves the React UI via Vite.

## Build & Package

### Development
```powershell
npm run dev           # Start dev server with hot reload
```

### Production Build
```powershell
npm run build         # Build renderer + main process
npm run start         # Run the built app
npm run dist:win      # Create Windows installer (.exe)
```

The Windows installer will be in `release/` directory.

## Features

- **Electron + React** — Modern desktop app framework
- **Microsoft Edge WebView2** — Powered by Edge engine
- **App Store** — Launch web and desktop apps from integrated UI
- **Vite** — Lightning-fast dev server & hot reload
- **TypeScript** — Type-safe development
- **Context Isolation** — Secure preload bridge
- **Windows Packaging** — Build standalone .exe installer

## App Store

The integrated app store includes:
- **Browser**: Microsoft Edge
- **Productivity**: Outlook, OneNote, OneDrive
- **Communication**: Teams, Discord, Slack
- **AI**: Copilot
- **Entertainment**: Netflix, Spotify
- **Design**: Figma, Notion

All apps open in the default browser or launch their web versions if not installed locally.

## Project Structure

- `electron/` — Electron main + preload (TypeScript)
- `renderer/` — React UI via Vite
- `build/` — App resources (icon.ico)
- `dist/` — Compiled output
- `.vscode/tasks.json` — VS Code tasks
- `package.json` — Dependencies and scripts
