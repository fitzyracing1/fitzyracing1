@echo off
REM Marev1 Deployment Script for Windows

echo Building Marev1 cryptocurrency...
cargo build --release

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo Creating distribution package...
if not exist dist mkdir dist

set BINARY=target\release\marev1.exe
set VERSION=0.1.0

if not exist "dist\marev1-%VERSION%" mkdir "dist\marev1-%VERSION%"

copy /Y %BINARY% "dist\marev1-%VERSION%\"
copy /Y README.md "dist\marev1-%VERSION%\"
copy /Y Cargo.toml "dist\marev1-%VERSION%\"
xcopy /E /Y src "dist\marev1-%VERSION%\src\"

echo.
echo ✓ Distribution packaged in: dist\marev1-%VERSION%\
echo ✓ Binary location: dist\marev1-%VERSION%\marev1.exe
echo.
echo Run the executable:
echo   .\dist\marev1-%VERSION%\marev1.exe
