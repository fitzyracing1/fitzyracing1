@echo off
REM Marev1 Web Deployment Script

echo ========================================
echo   MAREV1 DEX - WEB DEPLOYMENT
echo ========================================
echo.

echo [1/4] Building web server...
cargo build --release --bin marev1-web

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo [2/4] Creating web distribution...
if not exist dist-web mkdir dist-web
if not exist "dist-web\marev1-web" mkdir "dist-web\marev1-web"

echo [3/4] Copying files...
copy /Y target\release\marev1-web.exe "dist-web\marev1-web\"
xcopy /E /Y web "dist-web\marev1-web\web\"
copy /Y METAMASK_GUIDE.md "dist-web\marev1-web\"
copy /Y README.md "dist-web\marev1-web\"

echo [4/4] Creating startup script...
(
echo @echo off
echo echo Starting Marev1 DEX Web Server...
echo echo.
echo echo Open your browser to: http://127.0.0.1:8080
echo echo Press Ctrl+C to stop the server
echo echo.
echo marev1-web.exe
) > "dist-web\marev1-web\start-server.bat"

echo.
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Location: dist-web\marev1-web\
echo.
echo To run:
echo   1. cd dist-web\marev1-web
echo   2. start-server.bat
echo   3. Open http://127.0.0.1:8080
echo   4. Connect MetaMask
echo.
