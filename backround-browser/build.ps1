# Backround Browser build script
param(
  [string] $OutputDir = "dist",
  [switch] $Zip
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$out = Join-Path $root $OutputDir
$bundle = Join-Path $out "backround-browser"

Write-Host "Building Backround Browser distribution..." -ForegroundColor Cyan

# Clean output
if (Test-Path $bundle) { Remove-Item -Recurse -Force $bundle }
New-Item -ItemType Directory -Path $bundle | Out-Null

# Copy Chromium bundle
$chromeSrc = Join-Path $root "chrome-win"
if (-not (Test-Path $chromeSrc)) { throw "chrome-win not found at $chromeSrc" }
Copy-Item -Path $chromeSrc -Destination $bundle -Recurse -Force

# Copy launcher and docs
Copy-Item (Join-Path $root "launch-backround.ps1") -Destination $bundle -Force
Copy-Item (Join-Path $root "Backround.bat") -Destination $bundle -Force
Copy-Item (Join-Path $root "README.md") -Destination $bundle -Force

# Copy extension
$extSrc = Join-Path $root "pathkeeper"
if (-not (Test-Path $extSrc)) { throw "pathkeeper extension not found at $extSrc" }
Copy-Item -Path $extSrc -Destination (Join-Path $bundle "pathkeeper") -Recurse -Force

# Remove any nested archives from extension folder to avoid zip conflicts
Get-ChildItem -Path (Join-Path $bundle "pathkeeper") -Filter *.zip -Recurse -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item $_.FullName -Force }

# Create empty profile folder (created/used on first launch)
New-Item -ItemType Directory -Path (Join-Path $bundle "profile") | Out-Null

# Write config to load extension from local folder and open pages on first run
$cfg = @{ ExtensionPath = "pathkeeper"; OpenExtensionsOnLaunch = $true; OpenShortcutsOnLaunch = $true } | ConvertTo-Json -Depth 3
$cfgPath = Join-Path $bundle "backround.config.json"
Set-Content -Path $cfgPath -Value $cfg -Encoding UTF8

Write-Host "Distribution ready at: $bundle" -ForegroundColor Green

if ($Zip) {
  $zipPath = Join-Path $out "backround-browser.zip"
  if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
  Compress-Archive -Path $bundle -DestinationPath $zipPath
  Write-Host "Zip created: $zipPath" -ForegroundColor Green
}
