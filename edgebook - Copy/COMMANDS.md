#!/bin/bash

# Quick reference guide for common development tasks

echo "========================================="
echo "EdgeBook OS - Quick Commands Reference"
echo "========================================="
echo ""

echo "SETUP & INSTALLATION"
echo "  ./setup.sh                    Setup all dependencies"
echo "  ./setup.sh --force           Force reinstall all packages"
echo ""

echo "iOS DEVELOPMENT"
echo "  cd ios && npm run dev         Run on physical iPad"
echo "  cd ios && npm run dev:ios     Run on iOS Simulator"
echo "  cd ios && npm run build:ipa   Build for App Store"
echo ""

echo "WINDOWS BACKEND"
echo "  cd windows-backend && npm run dev      Start dev server"
echo "  cd windows-backend && npm run build    Build for production"
echo "  cd windows-backend && npm start        Run production build"
echo ""

echo "TESTING"
echo "  curl http://localhost:3000/api/health                    Check backend"
echo "  curl -X POST http://localhost:3000/api/windows/launch \\" 
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"appId\":\"vscode\",\"userId\":\"test\",\"deviceId\":\"test\"}'"
echo ""

echo "DOCUMENTATION"
echo "  README.md                     Main project documentation"
echo "  iOS_BUILD_GUIDE.md            Complete iPad setup guide"
echo "  ARCHITECTURE.md               System design and integration"
echo "  windows-backend/README.md     Windows API documentation"
echo ""

echo "USEFUL LINKS"
echo "  Expo Docs:     https://docs.expo.dev"
echo "  React Native:  https://reactnative.dev"
echo "  Express.js:    https://expressjs.com"
echo "  TypeScript:    https://www.typescriptlang.org"
echo ""
