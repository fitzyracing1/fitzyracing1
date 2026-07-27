@echo off
REM EdgeBook OS - Windows Setup Script
REM This script sets up the iOS and Windows Backend environments

echo =========================================
echo EdgeBook OS - Setup Script
echo =========================================
echo.

REM Check prerequisites
echo Checking prerequisites...

where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo Error: npm is not installed
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i

echo Node.js %NODE_VERSION%
echo npm %NPM_VERSION%
echo.

REM Setup iOS
echo =========================================
echo Setting up iOS ^(Expo/React Native^)...
echo =========================================

if not exist "ios\node_modules\" (
    cd ios
    echo Installing dependencies...
    call npm install
    cd ..
    echo iOS dependencies installed
) else (
    echo iOS dependencies already installed
)

echo.

REM Setup Windows Backend
echo =========================================
echo Setting up Windows Backend ^(Express^)...
echo =========================================

if not exist "windows-backend\node_modules\" (
    cd windows-backend
    echo Installing dependencies...
    call npm install
    cd ..
    echo Windows Backend dependencies installed
) else (
    echo Windows Backend dependencies already installed
)

echo.

REM Summary
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo Next steps:
echo.
echo For iOS Development:
echo   cd ios
echo   npm run dev              # Run on device
echo.
echo For Windows Backend:
echo   cd windows-backend
echo   npm run dev              # Start development server
echo.
echo See iOS_BUILD_GUIDE.md for detailed instructions
echo.

pause
