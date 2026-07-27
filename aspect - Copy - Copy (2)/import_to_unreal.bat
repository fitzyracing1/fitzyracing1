@echo off
REM Unreal Engine Command Line Import Script
REM Automates importing JSON data into Unreal Engine project

echo ========================================================================
echo UNREAL ENGINE JSON DATA IMPORTER
echo ========================================================================
echo.

REM Set paths - UPDATE THESE FOR YOUR PROJECT
set UE_EDITOR="C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set PROJECT_FILE="C:\Path\To\Your\Project\YourProject.uproject"
set SOURCE_DIR="C:\Users\EC\aspect\UnrealExport"
set DEST_DIR="C:\Path\To\Your\Project\Content\ImportedData"

echo Unreal Engine Path: %UE_EDITOR%
echo Project File: %PROJECT_FILE%
echo Source Directory: %SOURCE_DIR%
echo Destination: %DEST_DIR%
echo.

REM Check if Unreal Editor exists
if not exist %UE_EDITOR% (
    echo ERROR: Unreal Editor not found at %UE_EDITOR%
    echo Please update the UE_EDITOR path in this script
    pause
    exit /b 1
)

REM Create destination directory if it doesn't exist
if not exist %DEST_DIR% (
    echo Creating destination directory...
    mkdir %DEST_DIR%
)

REM Copy JSON files to Unreal project
echo.
echo ========================================================================
echo COPYING JSON FILES TO UNREAL PROJECT
echo ========================================================================
echo.

xcopy %SOURCE_DIR%\*.json %DEST_DIR%\ /Y /I
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy files
    pause
    exit /b 1
)

echo Successfully copied JSON files to project
echo.

REM Import using Unreal Editor command line
echo ========================================================================
echo IMPORTING TO UNREAL ENGINE
echo ========================================================================
echo.

REM Run Unreal Editor in import mode
%UE_EDITOR% %PROJECT_FILE% -run=ImportAssets -nosplash -unattended -nullrhi

echo.
echo ========================================================================
echo IMPORT COMPLETE
echo ========================================================================
echo.
echo JSON files have been imported to your Unreal project
echo Location: %DEST_DIR%
echo.
echo You can now access these files in Unreal Editor Content Browser
echo.
pause
