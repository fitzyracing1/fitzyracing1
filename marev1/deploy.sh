#!/bin/bash
# Marev1 Deployment Script for Linux/macOS

set -e

echo "Building Marev1 cryptocurrency..."
cargo build --release

BINARY="./target/release/marev1"
VERSION=$($BINARY --version 2>/dev/null || echo "0.1.0")

echo "Creating distribution package..."
mkdir -p dist/marev1-$VERSION

cp target/release/marev1 dist/marev1-$VERSION/
cp README.md dist/marev1-$VERSION/
cp Cargo.toml dist/marev1-$VERSION/
cp -r src dist/marev1-$VERSION/

echo "Packaging..."
cd dist
tar -czf marev1-$VERSION-linux-x86_64.tar.gz marev1-$VERSION/
echo "✓ Created: marev1-$VERSION-linux-x86_64.tar.gz"

cd ..
echo "Deployment ready in ./dist/"
