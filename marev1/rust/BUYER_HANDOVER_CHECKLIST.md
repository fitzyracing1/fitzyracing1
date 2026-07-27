# Buyer Handover Checklist

**Project:** MAREV Token + DEX Stack  
**Sale Date:** _______________  
**Buyer:** _______________  
**Package:** [ ] Code-Only  [ ] Full Stack  [ ] Premium

---

## 📋 Pre-Handover (Seller Tasks)

### Contract Verification
- [ ] MAREV Token verified on BaseScan
  - URL: https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF
- [ ] DEX Contract verified on BaseScan
  - URL: https://basescan.org/address/0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039
- [ ] Contract ABIs exported and organized
- [ ] Source code matches deployed bytecode

### Repository Preparation
- [ ] All code committed and pushed to main branch
- [ ] `.env` files removed or sanitized (no private keys)
- [ ] README files updated with current addresses
- [ ] Test suites passing (Rust + Solidity)
- [ ] Dependencies documented in package.json and Cargo.toml

### Documentation Review
- [ ] SALE_PACKAGE.md complete and accurate
- [ ] Deployment guides tested and working
- [ ] Contract addresses verified in all docs
- [ ] Troubleshooting section added to READMEs

### Security Audit
- [ ] No private keys in repository
- [ ] No API keys or secrets committed
- [ ] Ownership transfer process tested on testnet
- [ ] Backup of all deployment data secured

---

## 🤝 Handover Process

### Phase 1: Payment & Agreement (Day 0)
- [ ] Buyer payment received and confirmed
- [ ] Sale agreement signed by both parties
- [ ] Buyer GitHub username collected
- [ ] Buyer wallet address confirmed (for ownership transfer)

### Phase 2: Code Transfer (Day 0-1)
- [ ] Repository access granted to buyer
  - Buyer GitHub: _______________
- [ ] Buyer confirms repository access
- [ ] Buyer successfully clones repository locally
- [ ] Buyer confirms all files present

### Phase 3: Documentation Walkthrough (Day 1-2)
- [ ] Buyer reads SALE_PACKAGE.md
- [ ] Buyer reads all READMEs (main, dex/, vercel/)
- [ ] Buyer understands contract addresses and networks
- [ ] Buyer reviews deployment history JSON files
- [ ] Questions answered

### Phase 4: Local Setup Verification (Day 2-3)
- [ ] Buyer installs Node.js dependencies (`npm install`)
- [ ] Buyer installs Rust toolchain
- [ ] Buyer runs `cargo test` successfully (6 tests pass)
- [ ] Buyer runs `npx hardhat test` successfully
- [ ] Buyer compiles contracts without errors

### Phase 5: Contract Ownership Transfer (Full Stack/Premium only) (Day 3-5)
- [ ] Buyer provides new owner address: `0x_______________`
- [ ] Buyer confirms control of new owner address
- [ ] Seller initiates `transferOwnership()` on MAREV Token
  - Tx Hash: _______________
- [ ] Seller initiates ownership transfer on DEX Contract
  - Tx Hash: _______________
- [ ] Buyer calls `acceptOwnership()` or confirms transfer
- [ ] Buyer verifies ownership on-chain:
  ```bash
  cast call 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "owner()" --rpc-url https://mainnet.base.org
  ```
- [ ] Ownership transfer complete and verified

### Phase 6: Deployer Key Transfer (Full Stack/Premium only) (Day 5)
**⚠️ CRITICAL SECURITY STEP**

- [ ] Secure communication channel established (Signal/encrypted email)
- [ ] Buyer confirms understanding of key security responsibilities
- [ ] Seller sends encrypted deployer private key
- [ ] Buyer imports key to secure hardware wallet (recommended)
- [ ] Buyer confirms control by signing test message
- [ ] Seller receives confirmation of buyer control
- [ ] **Seller deletes private key from all devices**
- [ ] **Seller confirms key deletion**
- [ ] Buyer transfers remaining Base ETH from deployer wallet (if desired)

### Phase 7: Frontend Handover (Day 5-7)
- [ ] Buyer reviews `vercel/` directory
- [ ] Buyer updates contract addresses in `dex.js` (if needed)
- [ ] Buyer tests frontend locally:
  ```bash
  cd vercel
  npx serve .
  ```
- [ ] Buyer connects MetaMask to local frontend
- [ ] Buyer deploys to their own Vercel/hosting account
  - URL: _______________
- [ ] Frontend live and functional

### Phase 8: Uniswap Integration (Premium only) (Day 7-14)
- [ ] Check if Uniswap pool exists for MAREV/USDC
- [ ] If no pool: guide buyer through pool creation
- [ ] Buyer adds initial liquidity
  - Amount MAREV: _______________
  - Amount USDC: _______________
  - Fee tier: _______________
  - Tx Hash: _______________
- [ ] Pool visible on Uniswap interface
- [ ] Test swap executed successfully
- [ ] Buyer understands liquidity management

---

## 🎓 Knowledge Transfer

### Smart Contract Operations
- [ ] Explain minting function (if owner-controlled)
- [ ] Explain pause/unpause functionality
- [ ] Explain DEX liquidity management
- [ ] Walk through contract upgrade process (if applicable)
- [ ] Demonstrate reading contract state with cast/Etherscan

### Deployment to New Networks
- [ ] Show how to add network to `hardhat.config.js`
- [ ] Demonstrate testnet deployment
- [ ] Explain gas estimation and funding requirements
- [ ] Walk through deployment script modifications

### Maintenance & Operations
- [ ] How to monitor contract events
- [ ] How to handle user support requests
- [ ] Where to find transaction history
- [ ] How to update frontend contract addresses
- [ ] Backup and recovery procedures

---

## 🐛 Testing & Validation

### Buyer Self-Testing Checklist
- [ ] Can build Rust project without errors
- [ ] All Rust tests pass locally
- [ ] Can compile Solidity contracts
- [ ] All Solidity tests pass locally
- [ ] Can read deployed contract state on BaseScan
- [ ] Can connect to contracts via Hardhat console
- [ ] Frontend loads without errors
- [ ] Can interact with contracts via frontend

### Live Contract Validation
- [ ] Token balance readable on BaseScan
- [ ] Token transfers work (test with small amount)
- [ ] DEX contract responsive to queries
- [ ] Ownership correctly transferred to buyer
- [ ] No unexpected errors in contract calls

---

## 📞 Support Period

### Support Details
- **Duration:** _____ days (14 or 30 depending on package)
- **Start Date:** _______________
- **End Date:** _______________
- **Contact Method:** [Email/Discord/Telegram]
- **Response Time:** 24-48 hours

### Covered Issues
- [ ] Bug fixes in existing code
- [ ] Deployment assistance
- [ ] Configuration help
- [ ] Documentation clarifications
- [ ] Contract interaction guidance

### NOT Covered
- [ ] New feature development
- [ ] Smart contract modifications
- [ ] Ongoing infrastructure hosting
- [ ] Marketing or token promotion
- [ ] Legal or regulatory advice
- [ ] Issues caused by buyer modifications

---

## ✅ Final Handover Confirmation

### Seller Confirmation
I confirm that I have:
- [ ] Transferred all repository access
- [ ] Transferred contract ownership (if applicable)
- [ ] Securely transferred private keys (if applicable)
- [ ] Provided all documentation and support materials
- [ ] Deleted all private keys from my systems (if applicable)
- [ ] Answered all buyer questions to date

**Seller Signature:** _______________  
**Date:** _______________

### Buyer Confirmation
I confirm that I have:
- [ ] Received repository access and all code
- [ ] Received contract ownership (if applicable)
- [ ] Received and secured private keys (if applicable)
- [ ] Successfully built and tested code locally
- [ ] Understood all documentation
- [ ] Verified contract ownership on-chain (if applicable)
- [ ] No outstanding critical questions

**Buyer Signature:** _______________  
**Date:** _______________

---

## 🔒 Post-Handover (Buyer Responsibilities)

### Immediate Actions
- [ ] Change all passwords and API keys
- [ ] Move deployer funds to secure cold wallet
- [ ] Set up monitoring for contracts (Tenderly, OpenZeppelin Defender)
- [ ] Backup all private keys to secure offline storage
- [ ] Update frontend environment variables
- [ ] Test disaster recovery process

### Ongoing Security
- [ ] Never commit private keys to repositories
- [ ] Use hardware wallets for high-value operations
- [ ] Keep dependencies updated (npm audit, cargo audit)
- [ ] Monitor contract for unusual activity
- [ ] Have incident response plan

---

## 📞 Emergency Contacts

**Seller (during support period):**  
- Email: _______________  
- Discord/Telegram: _______________  
- Availability: _______________

**Blockchain Explorers:**  
- BaseScan: https://basescan.org  
- Base Sepolia: https://sepolia.basescan.org

**Community Resources:**  
- Hardhat Docs: https://hardhat.org/docs  
- OpenZeppelin: https://docs.openzeppelin.com  
- Base Docs: https://docs.base.org

---

**Last Updated:** March 4, 2026  
**Version:** 1.0  
**Project:** MAREV Token + DEX Stack
