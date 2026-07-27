@echo off
REM Unity Command-Line Build Script (Batch version)
REM Usage: Build.bat [UnityPath] [BuildTarget]

setlocal

set UNITY_PATH="C:\Program Files\Unity\Hub\Editor\2022.3.10f1\Editor\Unity.exe"
set PROJECT_PATH=%~dp0
set BUILD_TARGET=Win64
set BUILD_PATH=%~dp0Builds\Windows

if not "%~1"=="" set UNITY_PATH=%~1
if not "%~2"=="" set BUILD_TARGET=%~2

if not exist %UNITY_PATH% (
    echo Unity not found at: %UNITY_PATH%
    echo Please update the UNITY_PATH variable or pass the path as first argument
    exit /b 1
)

echo Building Unity Project...
echo Unity Path: %UNITY_PATH%
echo Project Path: %PROJECT_PATH%
echo Build Target: %BUILD_TARGET%
echo Build Path: %BUILD_PATH%

if not exist "%BUILD_PATH%" mkdir "%BUILD_PATH%"

%UNITY_PATH% -quit -batchmode -nographics -projectPath "%PROJECT_PATH%" -buildTarget %BUILD_TARGET% -buildWindows64Player "%BUILD_PATH%\Game.exe"

if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    echo Build location: %BUILD_PATH%\Game.exe
) else (
    echo Build failed with error code: %ERRORLEVEL%
    echo Check Unity log at: %LOCALAPPDATA%\Unity\Editor\Editor.log
    exit /b %ERRORLEVEL%
)

endlocal
