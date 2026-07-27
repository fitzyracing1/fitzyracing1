# PathKeeper Browser Extension

This workspace contains the PathKeeper browser extension - a tool for managing and tracking file paths.

## Project Type
Browser Extension (Manifest V3)

## Features
- Save and manage file paths
- Copy paths to clipboard
- Local storage for all data
- Clean, intuitive UI

## Structure
- `manifest.json` - Extension manifest
- `popup.html/css/js` - Extension popup interface
- `background.js` - Background service worker
- `src/` - TypeScript source files (optional)
- `icons/` - Extension icons (need to be added)

## Setup
1. Add icon images (16x16, 48x48, 128x128) to `icons/` folder or remove icon references from manifest
2. Load extension in browser developer mode
3. See README.md for detailed installation instructions

## Development
- Written in vanilla JavaScript (TypeScript sources available in `src/`)
- No build process required for basic usage
- Can compile TypeScript with `npm run build` if Node.js is installed
