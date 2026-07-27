# Marev1 Deployment Guide

## Quick Start

### Windows
```powershell
# Run the deployment script
.\deploy.bat

# Execute the binary
.\dist\marev1-0.1.0\marev1.exe
```

### Linux/macOS
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Execute the binary
./dist/marev1-0.1.0/marev1
```

## Deployment Options

### Option 1: Standalone Binary (Recommended)
The `deploy.bat` (Windows) or `deploy.sh` (Linux/macOS) scripts create a self-contained distribution package.

**Advantages:**
- No dependencies needed
- Single executable file
- Easy to distribute

**Output:** `dist/marev1-0.1.0/marev1.exe` (or `marev1` on Linux/macOS)

### Option 2: Docker Container
Deploy using Docker for consistent environments.

```bash
# Build Docker image
docker build -t marev1:0.1.0 .

# Run container
docker run -it marev1:0.1.0
```

Or with Docker Compose:
```bash
docker-compose up
```

### Option 3: GitHub Actions (CI/CD)
Automatic builds for multiple platforms on push to `main` branch.

**Platforms:**
- Linux (x86_64)
- Windows (x86_64)  
- macOS (x86_64)

**Setup:**
1. Push code to GitHub
2. GitHub Actions automatically builds and tests
3. Artifacts are available for download

## Package Contents

```
dist/marev1-0.1.0/
├── marev1.exe          # Executable binary
├── README.md           # Documentation
├── Cargo.toml          # Project manifest
└── src/                # Source code
    ├── main.rs
    ├── lib.rs
    ├── blockchain.rs
    ├── block.rs
    ├── transaction.rs
    ├── wallet.rs
    └── error.rs
```

## Requirements

### Standalone Binary
- Windows 10+, Linux, or macOS
- No additional software needed

### Building from Source
- Rust 1.56+ ([Install](https://www.rust-lang.org/tools/install))
- Cargo (included with Rust)

### Docker Deployment
- Docker 20.10+
- Docker Compose 1.29+ (optional)

## Verification

Test the deployment:

```powershell
# Windows
.\dist\marev1-0.1.0\marev1.exe

# Linux/macOS
./dist/marev1-0.1.0/marev1
```

Expected output:
```
Welcome to Marev1 Cryptocurrency!
Wallet 1 - Alice: 0x3bc51062973c458d5a6f2d8d64a023246354ad7e
Wallet 2 - Bob: 0xcd9fb1e148ccd8442e5aa74904cc73bf6fb54d1d
...
Chain is valid: true
```

## Distribution

### Create Release Archive
**Windows:**
```powershell
Compress-Archive -Path dist\marev1-0.1.0 -DestinationPath marev1-0.1.0.zip
```

**Linux/macOS:**
```bash
tar -czf marev1-0.1.0.tar.gz dist/marev1-0.1.0/
```

### Publish to Package Registries
To publish to crates.io:
```bash
cargo publish
```

Update `Cargo.toml` with your repository URL and license information first.

## Troubleshooting

### Binary not found
- Ensure you're in the project directory: `cd c:\Users\EC\marev1`
- Run `cargo build --release` manually if deployment script fails

### Permission denied (Linux/macOS)
```bash
chmod +x ./dist/marev1-0.1.0/marev1
```

### Docker build fails
- Ensure Docker is running
- Check internet connection for dependency downloads
- Try: `docker system prune` to free space

## Security Considerations

- Store binaries in secure locations
- Verify checksums before distribution
- Don't commit sensitive data to version control
- Use signed releases for production

## Version Management

Current version: **0.1.0**

To update version:
1. Edit `Cargo.toml` version field
2. Update `deploy.bat` or `deploy.sh` version reference
3. Rebuild: `cargo build --release`
4. Redeploy: `.\deploy.bat`

## Support

For issues or questions:
1. Check README.md for feature documentation
2. Review source code comments in `src/`
3. Run tests: `cargo test --lib`
