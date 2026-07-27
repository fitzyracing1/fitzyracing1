# MAREV Token + DEX Stack - Sale Package

**Product:** Deployed Meme Token + Custom DEX on Base Mainnet  
**Status:** Live & Operational  
**Sale Date:** March 2026

---

## 🎯 What You're Buying

A complete, deployed cryptocurrency ecosystem consisting of:

1. **ERC-20 Token (MAREV)** - Deployed & tradeable on Base mainnet
2. **Custom DEX Contract** - Your own decentralized exchange for swapping
3. **Web Interface** - Frontend for users to interact with your DEX
4. **Rust Blockchain Demo** - Educational blockchain implementation
5. **Full Source Code** - All contracts, scripts, and deployment tooling
6. **Deployment Documentation** - Step-by-step guides for future deployments

---

## 📊 Deployed Contracts (Base Mainnet)

| Contract | Address | Chain ID |
|----------|---------|----------|
| **MAREV Token** | `0xbb73AC0044F8798924474d66E5c81937BDcdEccF` | 8453 |
| **DEX Contract** | `0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039` | 8453 |
| **USDC (Base)** | `0x833589fcd6edb6e08f4c7c32d4f71b1566469c3d` | 8453 |
| **Deployer** | `0x4253AaCA78419dd5d82A74708c29c6Bdfe325565` | 8453 |
| **Deployed** | February 9, 2026 | Live |

### Contract Verification Status
- [ ] MAREV Token verified on BaseScan
- [ ] DEX Contract verified on BaseScan

**View on BaseScan:**
- Token: https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF
- DEX: https://basescan.org/address/0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039

---

## 🏗️ What's Included

### 1. Smart Contracts (`dex/`)
- ✅ `MAREVToken.sol` - ERC-20 token with minting capabilities
- ✅ `MAREVDex.sol` - Custom DEX with liquidity pools
- ✅ `ERC20Mock.sol` - Testing utilities
- ✅ Deployment scripts (`scripts/deploy.js`)
- ✅ Hardhat test suite (`test/dex.test.js`)
- ✅ Multi-network config (localhost, Base Sepolia, Base mainnet)

### 2. Web Interface (`vercel/`)
- ✅ Trading interface (`dex.html`, `dex.js`)
- ✅ Landing page (`index.html`)
- ✅ Responsive styling (`styles.css`)
- ✅ Vercel deployment config (`vercel.json`)
- ✅ Web3 integration with MetaMask

### 3. Rust Blockchain (`src/`)
- ✅ Complete blockchain implementation
- ✅ Wallet system with address generation
- ✅ Transaction handling with fees
- ✅ Block mining with proof-of-work
- ✅ Chain validation
- ✅ 6 passing unit tests

### 4. Documentation
- ✅ Main README
- ✅ DEX README with deployment guide
- ✅ Vercel README for frontend
- ✅ Contract deployment history (JSON files)

---

## 💰 Token Economics

**Token Name:** MAREV  
**Symbol:** MAREV  
**Decimals:** 18  
**Initial Supply:** Set at deployment  
**Contract Type:** ERC-20 Standard

**Features:**
- Standard ERC-20 transfers
- Minting capability (owner-controlled)
- Pausable functionality
- OpenZeppelin security standards

---

## 🔧 Technical Stack

### Smart Contracts
- **Language:** Solidity ^0.8.20
- **Framework:** Hardhat
- **Libraries:** OpenZeppelin Contracts
- **Networks:** Base (mainnet), Base Sepolia (testnet), Localhost

### Frontend
- **Framework:** Vanilla JavaScript + Web3.js/Ethers.js
- **Hosting:** Vercel-ready
- **Wallet:** MetaMask integration
- **UI:** Responsive HTML/CSS

### Blockchain Demo
- **Language:** Rust 1.93.0
- **Dependencies:** sha2, hex
- **Features:** Full blockchain simulation

---

## 🚀 Quick Start for Buyer

### 1. Verify Ownership Transfer
```bash
# Check current contract owner
cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "owner()" --rpc-url https://mainnet.base.org
```

### 2. Clone Repository
```bash
git clone <your-repo-url>
cd marev1
```

### 3. Install Dependencies
```bash
# Solidity contracts
cd dex
npm install

# Rust blockchain
cd ../
cargo build
```

### 4. Test Locally
```bash
# Run Rust tests
cargo test

# Run Solidity tests
cd dex
npx hardhat test
```

### 5. Deploy Frontend
```bash
cd vercel
# Deploy to your Vercel account
vercel deploy --prod
```

---

## 📋 What Buyer Receives

### Code & Contracts
- ✅ Complete GitHub repository access
- ✅ All contract source code
- ✅ Deployment scripts for new chains
- ✅ Test suites (Rust + Solidity)

### Deployed Assets (Base Mainnet)
- ✅ Live ERC-20 token contract
- ✅ Live DEX contract
- ✅ Contract ABIs (in `dex/artifacts/`)
- ✅ Deployment transaction records

### Ownership Transfer
- ✅ Contract ownership transfer instructions
- ✅ Admin wallet handover (secure process)
- ✅ Private key transfer (if applicable)

### Documentation
- ✅ Full setup guides
- ✅ Deployment checklists
- ✅ Uniswap integration guide
- ✅ Troubleshooting tips

### Support
- ✅ 14-day technical support window
- ✅ Deployment assistance
- ✅ Bug fixes for existing code
- ❌ No ongoing maintenance after support period

---

## 🔐 Security & Legal

### Security Considerations
- Contracts use OpenZeppelin battle-tested libraries
- Standard ERC-20 implementation
- Owner-controlled minting (requires secure key management)
- No external audit completed (recommend before mainnet if critical)

### Legal Disclaimer
⚠️ **IMPORTANT:** This is a software product sale only.

- **NOT financial advice** - Buyer responsible for all regulatory compliance
- **No guarantees** - Software provided "as-is"
- **Token value** - No promises about future token value or market performance
- **Compliance** - Buyer must ensure legal compliance in their jurisdiction
- **Tax obligations** - Buyer responsible for all tax implications
- **Smart contract risks** - Blockchain transactions are irreversible

**Seller assumes NO liability for:**
- Market performance of token
- Regulatory compliance issues
- Loss of funds due to misuse
- Smart contract exploits (though none known)
- Frontend or infrastructure downtime

---

## 💵 Pricing Options

### Option 1: Code-Only Package - $XXX
- Complete source code repository
- Contract ABIs and deployment configs
- Documentation and guides
- **NO** ownership transfer of deployed contracts
- **NO** technical support

### Option 2: Full Stack Package - $XXX
- Everything in Code-Only Package
- Ownership transfer of deployed Base mainnet contracts
- Private key handover (secure process)
- 14 days of technical support
- Deployment assistance

### Option 3: Premium Package - $XXX
- Everything in Full Stack Package
- 30 days of technical support
- Uniswap pool creation assistance
- Contract verification on BaseScan
- Custom branding updates
- Video walkthrough session

---

## 📞 Handover Process

### Step 1: Payment & Agreement
1. Buyer sends payment
2. Seller provides sale agreement (digital signature)
3. Both parties agree to terms

### Step 2: Repository Transfer
1. Buyer provides GitHub username
2. Seller transfers repository access
3. Buyer confirms code receipt

### Step 3: Contract Ownership Transfer (Full Stack only)
1. Seller initiates `transferOwnership()` call
2. Buyer confirms new owner address
3. Transaction executes on-chain
4. Buyer verifies ownership

### Step 4: Private Key Transfer (Full Stack only)
1. Secure key exchange (encrypted channel)
2. Buyer imports key to secure wallet
3. Buyer confirms control
4. Seller wipes key from all devices

### Step 5: Support Period Begins
- Buyer has 14-30 days (depending on package)
- Communication via email/Discord/Telegram
- Response time: 24-48 hours

---

## ✅ Pre-Sale Checklist (Seller)

- [ ] Verify all contracts on BaseScan
- [ ] Test ownership transfer process
- [ ] Backup all private keys securely
- [ ] Update documentation with latest addresses
- [ ] Run full test suite and confirm passing
- [ ] Deploy demo frontend (if showing to buyers)
- [ ] Prepare secure key transfer method
- [ ] Draft sale agreement
- [ ] Set pricing for each package tier

---

## 📧 Contact

**Seller:** [Your Name/Handle]  
**Email:** [Your Email]  
**Discord/Telegram:** [Your Handle]

**Serious inquiries only.**  
Proof of funds may be required for Full Stack packages.

---

**Last Updated:** March 4, 2026  
**Repository:** marev (fitzyracing1)  
**Current Status:** Live on Base Mainnet
