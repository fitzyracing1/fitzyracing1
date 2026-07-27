# MAREV - Meme Token + Custom DEX Stack

**Status:** 🟢 Live on Base Mainnet  
**Sale:** ✅ Available for Purchase  
**Package:** Deployed Token + DEX + Source Code

---

## 🚀 What Is This?

A complete cryptocurrency ecosystem combining:
- **ERC-20 Token (MAREV)** deployed on Base mainnet
- **Custom DEX Contract** for decentralized swaps
- **Web Trading Interface** (Vercel-ready)
- **Rust Blockchain Demo** with proof-of-work

Perfect for buyers looking for a ready-to-launch token + DEX stack.

---

## 📊 Live Deployments

### Base Mainnet (Chain ID: 8453)
- **Token:** `0xbb73AC0044F8798924474d66E5c81937BDcdEccF`
- **DEX:** `0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039`
- **USDC:** `0x833589fcd6edb6e08f4c7c32d4f71b1566469c3d`

[View Token on BaseScan](https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF) | [View DEX on BaseScan](https://basescan.org/address/0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039)

---

## 💰 For Sale

📄 **See [SALE_PACKAGE.md](./SALE_PACKAGE.md)** for complete details.

**What's Included:**
- ✅ All source code (Solidity + Rust + Frontend)
- ✅ Deployed Base mainnet contracts
- ✅ Contract ownership transfer
- ✅ Full documentation + guides
- ✅ 14-30 days technical support

**Pricing:** Contact for packages (Code-Only / Full Stack / Premium)

---

## 🏗️ Repository Structure

```
marev1/rust/
├── dex/              # Solidity smart contracts (Hardhat)
│   ├── contracts/    # Token + DEX contracts
│   ├── scripts/      # Deployment scripts
│   ├── test/         # Test suite
│   └── deployments-*.json  # Live addresses
├── src/              # Rust blockchain demo
│   ├── block.rs      # Block structure + mining
│   ├── blockchain.rs # Chain management
│   ├── transaction.rs# Transactions + fees
│   ├── wallet.rs     # Wallet generation
│   └── main.rs       # Demo runner
├── vercel/           # Web trading interface
│   ├── dex.html      # Trading UI
│   ├── dex.js        # Web3 integration
│   └── vercel.json   # Deployment config
├── SALE_PACKAGE.md   # 📦 Complete sale details
└── BUYER_HANDOVER_CHECKLIST.md  # Handover process
```

---

## 🧪 Quick Start (Testing Locally)

### Rust Blockchain Demo

```powershell
# Run the demo
cargo run

# Run tests (6 tests)
cargo test
```

**Expected Output:**
```
Marev1 - Minimal Blockchain Demo
Alice: 0x3bc51062973c458d5a6f2d8d64a023246354ad7e
Bob:   0xcd9fb1e148ccd8442e5aa74904cc73bf6fb54d1d
Blocks: 2
Chain valid: true
```

### Solidity Contracts

```powershell
cd dex
npm install
npx hardhat test
npx hardhat compile
```

### Web Interface

```powershell
cd vercel
npx serve .
# Open http://localhost:3000
```

---

## 📚 Documentation

- **[SALE_PACKAGE.md](./SALE_PACKAGE.md)** - Complete sale package details
- **[BUYER_HANDOVER_CHECKLIST.md](./BUYER_HANDOVER_CHECKLIST.md)** - Handover process
- **[dex/README.md](./dex/README.md)** - Smart contract deployment guide
- **[dex/DEPLOYMENT_GUIDE.md](./dex/DEPLOYMENT_GUIDE.md)** - Network deployment steps
- **[vercel/README.md](./vercel/README.md)** - Frontend deployment guide

---

## 🔐 Security & Legal

⚠️ **Software sale only - not financial advice.**

- Contracts use OpenZeppelin libraries
- Standard ERC-20 implementation
- No external audit completed
- Buyer responsible for compliance
- See [SALE_PACKAGE.md](./SALE_PACKAGE.md) for full disclaimer

---

## 📞 Contact (Buyers Only)

**Serious inquiries:** [Your Contact Info]  
**Package details:** See [SALE_PACKAGE.md](./SALE_PACKAGE.md)

---

## ⚙️ Technical Details

### Rust Components
- `src/block.rs` - Block structure + mining
- `src/blockchain.rs` - Chain management + validation
- `src/transaction.rs` - Transaction handling + fees
- `src/wallet.rs` - Address generation (Keccak256)
- `src/main.rs` - Demo runner

### Solidity Contracts
- `MAREVToken.sol` - ERC-20 token
- `MAREVDex.sol` - Custom DEX with liquidity pools
- OpenZeppelin security standards

### Tech Stack
- **Rust:** 1.93.0
- **Solidity:** ^0.8.20
- **Hardhat:** Latest
- **Web3:** Ethers.js / Web3.js

---

**Last Updated:** March 4, 2026  
**Status:** Live & For Sale
