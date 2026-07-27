#!/bin/bash

# EdgeBook OS - Development Server Starter
# Runs iOS and Windows Backend development servers simultaneously

echo "========================================="
echo "EdgeBook OS - Development Servers"
echo "========================================="
echo ""
echo "Starting iOS and Windows Backend development servers..."
echo ""
echo "Make sure you have:"
echo "  1. Installed all dependencies (run setup.sh first)"
echo "  2. Node.js and npm installed"
echo "  3. Xcode command line tools (for macOS)"
echo ""

# Function to start servers
start_servers() {
    # Start Windows Backend in background
    echo "Starting Windows Backend on http://localhost:3000"
    cd windows-backend
    npm run dev &
    BACKEND_PID=$!
    cd ..
    
    # Give backend time to start
    sleep 2
    
    # Start iOS dev server
    echo "Starting iOS dev server"
    cd ios
    npm run dev
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    echo "Servers stopped"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Start the servers
start_servers
