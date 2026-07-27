# Quick Demo Commands

Fast commands to show your MAREV stack is working — perfect for buyer demos.

---

## 🦀 Rust Blockchain Demo

### Run the Demo
```powershell
Set-Location "C:\Users\EC\marev1\rust"
cargo run
```

**Expected Output:**
```
Marev1 - Minimal Blockchain Demo
Alice: 0x3bc51062973c458d5a6f2d8d64a023246354ad7e
Bob:   0xcd9fb1e148ccd8442e5aa74904cc73bf6fb54d1d
Blocks: 2
Chain valid: true
```

### Run Tests
```powershell
cargo test
```

**Expected:**
```
test result: ok. 6 passed; 0 failed; 0 ignored
```

### Run Release Build
```powershell
cargo run --release
```

---

## 🔗 Smart Contract Tests

### Run Full Test Suite
```powershell
Set-Location "C:\Users\EC\marev1\rust\dex"
npm install
npx hardhat test
```

### Deploy to Local Hardhat Network
```powershell
npx hardhat node
# In new terminal:
npx hardhat run scripts/deploy.js --network localhost
```

### Compile Contracts
```powershell
npx hardhat compile
```

---

## 🌐 Check Live Contracts (Base Mainnet)

### View Token on BaseScan
```powershell
Start-Process "https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF"
```

### View DEX on BaseScan
```powershell
Start-Process "https://basescan.org/address/0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039"
```

### Check Token Balance (using cast)
```bash
cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "totalSupply()" --rpc-url https://mainnet.base.org
```

### Check Token Owner
```bash
cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "owner()" --rpc-url https://mainnet.base.org
```

### Check DEX Liquidity
```bash
cast call 0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039 "getLiquidity(address)" <token_address> --rpc-url https://mainnet.base.org
```

---

## 💻 Web Interface Demo

### Run Locally
```powershell
Set-Location "C:\Users\EC\marev1\rust\vercel"
npx serve .
```

Then open: http://localhost:3000

### Test with MetaMask
1. Open `dex.html` in browser
2. Connect MetaMask (Base network)
3. Try sample swap or liquidity check

---

## 📊 Quick Stats

### Get Deployment Info
```powershell
Set-Location "C:\Users\EC\marev1\rust\dex"
Get-Content .\deployments-base.json | ConvertFrom-Json | Format-List
```

**Output:**
```
network        : base
chainId        : 8453
marevToken     : 0xbb73AC0044F8798924474d66E5c81937BDcdEccF
dex            : 0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039
usdc           : 0x833589fcd6edb6e08f4c7c32d4f71b1566469c3d
deployer       : 0x4253AaCA78419dd5d82A74708c29c6Bdfe325565
deploymentTime : 2026-02-09T21:34:24.608Z
isTestnet      : False
```

---

## 🧪 One-Line Full Validation

### Validate Everything
```powershell
# Rust tests
Set-Location "C:\Users\EC\marev1\rust"; cargo test

# Solidity tests  
Set-Location "C:\Users\EC\marev1\rust\dex"; npx hardhat test

# Check live contracts
Start-Process "https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF"
```

---

## 🎬 Buyer Demo Script (5 Minutes)

### Step 1: Show Local Tests (1 min)
```powershell
cd C:\Users\EC\marev1\rust
cargo test
```
*"All 6 tests pass — blockchain logic is solid."*

### Step 2: Show Live Contracts (1 min)
```powershell
Start-Process "https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF"
```
*"Token is live on Base mainnet, fully deployed."*

### Step 3: Show Deployment History (1 min)
```powershell
cd dex
Get-Content .\deployments-base.json
```
*"Here's proof of deployment with exact addresses and timestamp."*

### Step 4: Show Smart Contract Tests (1 min)
```powershell
npx hardhat test
```
*"All Solidity tests pass — DEX logic is verified."*

### Step 5: Show Web Interface (1 min)
```powershell
cd ..\vercel
npx serve .
```
Open browser to `http://localhost:3000`  
*"Here's the trading interface, ready to deploy on Vercel."*

---

## 🔍 Verify Contract Interaction

### Read Token Name
```bash
cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "name()" --rpc-url https://mainnet.base.org | cast --to-ascii
```

### Read Token Symbol
```bash
cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "symbol()" --rpc-url https://mainnet.base.org | cast --to-ascii
```

### Read Token Decimals
```bash
cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "decimals()" --rpc-url https://mainnet.base.org
```

---

## 📸 Screenshots for Buyers

### Must-Have Screenshots
1. `cargo test` output showing all pass
2. BaseScan verified contract page
3. Web interface running locally
4. `deployments-base.json` content
5. Hardhat test results

### Take Screenshots
```powershell
# Run tests
cargo test

# Then use Win+Shift+S to capture output
```

---

## 🎯 Quick Checks Before Sale

```powershell
# 1. Tests pass
cd C:\Users\EC\marev1\rust
cargo test

# 2. Contracts verified
Start-Process "https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF"

# 3. Code compiles
cd dex
npx hardhat compile

# 4. Deployment records exist
Get-Content .\deployments-base.json

# 5. Frontend works
cd ..\vercel
npx serve .
```

All green? ✅ Ready to sell!

---

**Last Updated:** March 4, 2026  
**Project:** MAREV Token + DEX Stack
