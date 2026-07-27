# PathKeeper Browser Extension

A lightweight browser extension to manage and track file paths efficiently. Save, organize, and quickly copy file paths to your clipboard.

## Features

- **Save Paths**: Quickly store file paths for easy access
- **Copy to Clipboard**: One-click copying of saved paths
- **Path History**: View all your saved paths with timestamps
- **Clean UI**: Simple and intuitive interface
- **Local Storage**: All data stored locally in your browser

## Installation

### For Development (Chrome/Edge)

1. Open your browser and navigate to the extensions page:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`

2. Enable "Developer mode" (toggle in the top right)

3. Click "Load unpacked"

4. Select the `faster_pathkeeper` folder

5. The PathKeeper extension should now appear in your extensions list

### For Development (Firefox)

1. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`

2. Click "Load Temporary Add-on"

3. Navigate to the `faster_pathkeeper` folder and select the `manifest.json` file

4. The extension will be loaded temporarily

## Building from Source

If you have Node.js installed and want to compile TypeScript:

```bash
npm install
npm run build
```

This will compile the TypeScript files in `src/` to JavaScript in `dist/`.

## Usage

1. Click the PathKeeper icon in your browser toolbar

2. Enter or paste a file path in the input field

3. Click "Add Path" or press Enter

4. Your path is now saved and appears in the list below

5. Click "Copy" to copy any saved path to your clipboard

6. Click "Delete" to remove a specific path

7. Click "Clear All" to remove all saved paths

## Project Structure

```
faster_pathkeeper/
├── manifest.json          # Extension manifest
├── popup.html            # Popup UI
├── popup.css             # Popup styles
├── popup.js              # Compiled popup script
├── background.js         # Compiled background service worker
├── src/
│   ├── popup.ts         # TypeScript source for popup
│   └── background.ts    # TypeScript source for background
├── icons/               # Extension icons (add your own)
├── package.json         # Node.js dependencies
└── tsconfig.json        # TypeScript configuration
```

## Notes

- **Icons**: The manifest references icon files in the `icons/` folder. You'll need to add your own icon images (16x16, 48x48, 128x128 PNG files) or remove the icon references from `manifest.json`.

- **Permissions**: The extension requires:
  - `storage`: To save paths locally
  - `clipboardWrite`: To copy paths to clipboard

- **Browser Compatibility**: This extension uses Manifest V3 and is compatible with modern Chrome, Edge, and Firefox browsers.

## License

MIT License - Feel free to modify and use as needed.
