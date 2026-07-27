# Backround Browser

A custom Chromium-based browser instance with the Pathkeeper extension pre-installed.

## What is Backround?

Backround is a standalone browser profile that automatically loads the Pathkeeper extension. It runs independently from your regular Chrome/Edge browser with its own profile and settings.

## How to Use

1. **Launch the browser:**
   - Double-click `launch-backround.ps1`
   - Or run from PowerShell: `.\launch-backround.ps1`

2. **First Launch:**
   - The browser will create a new profile in the `profile` folder
   - Pathkeeper extension will be automatically loaded
   - You can use this as your dedicated Pathkeeper browser

## Features

- ✅ Pathkeeper extension pre-loaded
- ✅ Separate profile from your main browser
- ✅ No interference with existing Chrome/Edge installations
- ✅ Clean, dedicated browsing environment

## Launch Options

- `-ExtensionPath <dir>`: Override the Pathkeeper extension directory. Use this if the extension isn't in the parent folder.
- `-OpenExtensions`: Opens `chrome://extensions` on start.
- `-OpenShortcuts`: Opens `chrome://extensions/shortcuts` to configure keybindings.

Example:

```
PowerShell -NoProfile -ExecutionPolicy Bypass -File "c:\Users\EC\backround-browser\launch-backround.ps1" -ExtensionPath "C:\Path\To\Pathkeeper" -OpenExtensions
```

## Configuration File

You can set defaults in `backround.config.json` (next to the launcher):

```
{
   "ExtensionPath": "C:\\Path\\To\\Pathkeeper",
   "OpenExtensionsOnLaunch": false,
   "OpenShortcutsOnLaunch": false
}
```

- CLI parameters override values in the config.
- If `ExtensionPath` is missing and the extension is not in the parent folder, the script warns and extension shortcuts will not work.

## Requirements

- Chrome or Edge must be installed on your system
- Windows PowerShell

## Technical Details

The launcher script finds your Chrome/Edge installation and launches it with:
- Custom user data directory
- Extension loaded in developer mode
- Isolated from your main browser profile

If the extension directory is missing or doesn't contain a `manifest.json`, the script will warn and the extension won't load (so extension shortcuts won't work). Provide `-ExtensionPath` to point to the correct folder.
