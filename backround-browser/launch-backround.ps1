# Backround Browser Launcher
# Custom Chromium browser with Pathkeeper extension pre-loaded

param(
    [string] $ExtensionPath,
    [switch] $OpenExtensions,
    [switch] $OpenShortcuts
)

# Optional config file to set defaults
$configFile = Join-Path $PSScriptRoot "backround.config.json"
$config = $null
if (Test-Path $configFile) {
    try {
        $config = Get-Content -Raw $configFile | ConvertFrom-Json
        Write-Host "Config loaded: $configFile" -ForegroundColor Gray
    } catch {
        Write-Host "WARNING: Failed to parse $configFile" -ForegroundColor Yellow
    }
}

if (-not $ExtensionPath -and $config -and $config.ExtensionPath) {
    $ExtensionPath = $config.ExtensionPath
}
if (-not $OpenExtensions -and $config -and $config.OpenExtensionsOnLaunch) {
    $OpenExtensions = $true
}
if (-not $OpenShortcuts -and $config -and $config.OpenShortcutsOnLaunch) {
    $OpenShortcuts = $true
}

if (-not $ExtensionPath) {
    $ExtensionPath = Join-Path $PSScriptRoot ".."
}

# Resolve relative extension path to absolute
try {
    $isRooted = [System.IO.Path]::IsPathRooted($ExtensionPath)
    if (-not $isRooted) {
        $ExtensionPath = Join-Path $PSScriptRoot $ExtensionPath
    }
} catch {}

$extensionPath = $ExtensionPath
$profilePath = Join-Path $PSScriptRoot "profile"

# Validate extension path so we know if shortcuts could exist
$extensionManifest = Join-Path $extensionPath "manifest.json"
if (-not (Test-Path $extensionPath)) {
    Write-Host "WARNING: Extension folder not found at $extensionPath" -ForegroundColor Yellow
    Write-Host "Shortcuts from the extension won't work unless it's loaded." -ForegroundColor Yellow
} elseif (-not (Test-Path $extensionManifest)) {
    Write-Host "WARNING: No manifest.json in $extensionPath. Extension may not load." -ForegroundColor Yellow
    Write-Host "Ensure the Pathkeeper extension folder is correct." -ForegroundColor Yellow
} else {
    Write-Host "Extension detected: $extensionPath" -ForegroundColor Green
}

# Try bundled Chromium first, then fall back to system installations
$bundledChromium = Join-Path $PSScriptRoot "chrome-win\chrome.exe"
$chromePaths = @(
    $bundledChromium,
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)

$chromiumExe = $null
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $chromiumExe = $path
        break
    }
}

if (-not $chromiumExe) {
    Write-Host "ERROR: No Chromium-based browser found!" -ForegroundColor Red
    Write-Host "Please install Chrome or Edge first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Launching Backround Browser..." -ForegroundColor Cyan
Write-Host "Using: $chromiumExe" -ForegroundColor Gray
Write-Host "Profile dir: $profilePath" -ForegroundColor Gray
Write-Host "Extension dir: $extensionPath" -ForegroundColor Gray

# Launch browser with extension loaded in developer mode
& $chromiumExe `
    "--user-data-dir=$profilePath" `
    "--load-extension=$extensionPath" `
    "--disable-extensions-except=$extensionPath" `
    "--no-first-run" `
    "--no-default-browser-check" `
    $(if ($OpenExtensions) { "chrome://extensions" }) `
    $(if ($OpenShortcuts) { "chrome://extensions/shortcuts" })
