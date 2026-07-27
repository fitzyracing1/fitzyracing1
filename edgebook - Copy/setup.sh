#!/bin/bash

# EdgeBook OS - iOS & Windows Backend Setup Script
# This script sets up the complete iOS + Windows backend environment

echo "========================================="
echo "EdgeBook OS - Setup Script"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi

echo "✓ Node.js $(node --version)"
echo "✓ npm $(npm --version)"
echo ""

# Setup iOS
echo "========================================="
echo "Setting up iOS (Expo/React Native)..."
echo "========================================="

if [ ! -d "ios/node_modules" ]; then
    cd ios
    echo "Installing dependencies..."
    npm install
    cd ..
    echo "✓ iOS dependencies installed"
else
    echo "✓ iOS dependencies already installed"
fi

echo ""

# Setup Windows Backend
echo "========================================="
echo "Setting up Windows Backend (Express)..."
echo "========================================="

if [ ! -d "windows-backend/node_modules" ]; then
    cd windows-backend
    echo "Installing dependencies..."
    npm install
    cd ..
    echo "✓ Windows Backend dependencies installed"
else
    echo "✓ Windows Backend dependencies already installed"
fi

echo ""

# Summary
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "For iOS Development:"
echo "  cd ios"
echo "  npm run dev:ios          # Run on iOS Simulator"
echo "  npm run dev              # Run on physical device"
echo ""
echo "For Windows Backend:"
echo "  cd windows-backend"
echo "  npm run dev              # Start development server"
echo ""
echo "See iOS_BUILD_GUIDE.md for detailed instructions"
echo ""
