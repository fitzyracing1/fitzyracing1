# PowerShell Script to Import JSON Data to Unreal Engine
# Provides more control and feedback than batch script

param(
    [string]$UnrealVersion = "UE_5.7",
    [string]$ProjectPath = "",
    [switch]$CopyOnly
)

Write-Host "========================================================================"
Write-Host "UNREAL ENGINE JSON DATA IMPORTER (PowerShell)"
Write-Host "========================================================================"
Write-Host ""

# Configuration
$SourceDir = "C:\Users\EC\aspect\UnrealExport"
$UEBasePath = "C:\Program Files\Epic Games"
$UEEditorPath = Join-Path $UEBasePath "$UnrealVersion\Engine\Binaries\Win64\UnrealEditor.exe"
$UECmdPath = Join-Path $UEBasePath "$UnrealVersion\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

Write-Host "Configuration:"
Write-Host "  Unreal Version: $UnrealVersion"
Write-Host "  Editor Path: $UEEditorPath"
Write-Host "  Source Directory: $SourceDir"
Write-Host ""

# Check if Unreal Engine exists
if (-not (Test-Path $UEEditorPath)) {
    Write-Host "ERROR: Unreal Editor not found at: $UEEditorPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available Unreal Engine versions:" -ForegroundColor Yellow
    Get-ChildItem -Path $UEBasePath -Directory | Where-Object { $_.Name -like "UE_*" } | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "Usage: .\import_to_unreal.ps1 -UnrealVersion UE_5.7 -ProjectPath 'C:\Path\To\Project.uproject'"
    exit 1
}

# Check source directory
if (-not (Test-Path $SourceDir)) {
    Write-Host "ERROR: Source directory not found: $SourceDir" -ForegroundColor Red
    exit 1
}

# Get JSON files
$JsonFiles = Get-ChildItem -Path $SourceDir -Filter "*.json"
Write-Host "Found $($JsonFiles.Count) JSON files to import:"
foreach ($file in $JsonFiles) {
    Write-Host "  ✓ $($file.Name)" -ForegroundColor Green
}
Write-Host ""

# If project path is provided, copy files to project
if ($ProjectPath -ne "") {
    if (-not (Test-Path $ProjectPath)) {
        Write-Host "ERROR: Project file not found: $ProjectPath" -ForegroundColor Red
        exit 1
    }

    $ProjectDir = Split-Path $ProjectPath -Parent
    $ContentDir = Join-Path $ProjectDir "Content\ImportedData"
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $ContentDir)) {
        Write-Host "Creating directory: $ContentDir"
        New-Item -ItemType Directory -Path $ContentDir -Force | Out-Null
    }

    Write-Host "========================================================================"
    Write-Host "COPYING FILES TO PROJECT"
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "Destination: $ContentDir"
    Write-Host ""

    foreach ($file in $JsonFiles) {
        $destPath = Join-Path $ContentDir $file.Name
        Copy-Item -Path $file.FullName -Destination $destPath -Force
        Write-Host "  Copied: $($file.Name)" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "✓ All files copied successfully!" -ForegroundColor Green
    Write-Host ""

    if (-not $CopyOnly) {
        Write-Host "========================================================================"
        Write-Host "LAUNCHING UNREAL EDITOR"
        Write-Host "========================================================================"
        Write-Host ""
        Write-Host "Opening project: $ProjectPath"
        Write-Host "Files available in: Content/ImportedData"
        Write-Host ""
        
        # Launch Unreal Editor
        Start-Process -FilePath $UEEditorPath -ArgumentList "`"$ProjectPath`""
        
        Write-Host "Unreal Editor is starting..."
        Write-Host "Access imported files in Content Browser > ImportedData folder"
    }
} else {
    Write-Host "========================================================================"
    Write-Host "PROJECT PATH REQUIRED"
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "Please provide the path to your Unreal project file (.uproject)"
    Write-Host ""
    Write-Host "Usage examples:"
    Write-Host "  .\import_to_unreal.ps1 -ProjectPath 'C:\MyProject\MyGame.uproject'"
    Write-Host "  .\import_to_unreal.ps1 -UnrealVersion UE_5.7 -ProjectPath 'C:\MyProject\MyGame.uproject'"
    Write-Host "  .\import_to_unreal.ps1 -ProjectPath 'C:\MyProject\MyGame.uproject' -CopyOnly"
    Write-Host ""
    Write-Host "Available JSON files ready to import:"
    foreach ($file in $JsonFiles) {
        Write-Host "  - $($file.Name): $([math]::Round($file.Length / 1KB, 2)) KB"
    }
}

Write-Host ""
Write-Host "========================================================================"
Write-Host "SCRIPT COMPLETE"
Write-Host "========================================================================"
