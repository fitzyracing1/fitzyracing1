# Contract Verification Guide

Verify your deployed contracts on BaseScan so buyers can see the source code and trust the deployment.

---

## 🎯 Why Verify?

- ✅ Increases buyer confidence
- ✅ Makes contract readable on BaseScan
- ✅ Shows you're not hiding anything
- ✅ Required for serious DeFi projects
- ✅ Helps with debugging

---

## 📋 Base Mainnet Contracts to Verify

| Contract | Address |
|----------|---------|
| MAREV Token | `0xbb73AC0044F8798924474d66E5c81937BDcdEccF` |
| MAREV DEX | `0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039` |

---

## 🔧 Method 1: Hardhat Verify (Recommended)

### Prerequisites
```powershell
cd dex
npm install --save-dev @nomicfoundation/hardhat-verify
```

### Update `hardhat.config.js`

Add this to your config:

```javascript
require("@nomicfoundation/hardhat-verify");

module.exports = {
  // ... existing config
  etherscan: {
    apiKey: {
      base: process.env.BASESCAN_API_KEY,
      baseSepolia: process.env.BASESCAN_API_KEY
    },
    customChains: [
      {
        network: "base",
        chainId: 8453,
        urls: {
          apiURL: "https://api.basescan.org/api",
          browserURL: "https://basescan.org"
        }
      },
      {
        network: "baseSepolia",
        chainId: 84532,
        urls: {
          apiURL: "https://api-sepolia.basescan.org/api",
          browserURL: "https://sepolia.basescan.org"
        }
      }
    ]
  }
};
```

### Get BaseScan API Key

1. Go to https://basescan.org/myapikey
2. Sign up / log in
3. Create new API key
4. Add to `.env`:
   ```
   BASESCAN_API_KEY=YOUR_KEY_HERE
   ```

### Verify MAREV Token

```powershell
cd dex
npx hardhat verify --network base 0xbb73AC0044F8798924474d66E5c81937BDcdEccF
```

If constructor arguments were used, add them:
```powershell
npx hardhat verify --network base 0xbb73AC0044F8798924474d66E5c81937BDcdEccF "Constructor Arg 1" "Constructor Arg 2"
```

### Verify MAREV DEX

```powershell
npx hardhat verify --network base 0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039 "0xbb73AC0044F8798924474d66E5c81937BDcdEccF" "0x833589fcd6edb6e08f4c7c32d4f71b1566469c3d"
```

*(Adjust constructor args to match your deployment)*

---

## 🔧 Method 2: Manual Verification (BaseScan UI)

### Step 1: Get Contract Source

Flatten your contract:
```powershell
cd dex
npx hardhat flatten contracts/MAREVToken.sol > MAREVToken_flat.sol
npx hardhat flatten contracts/MAREVDex.sol > MAREVDex_flat.sol
```

### Step 2: Submit to BaseScan

1. Go to your contract on BaseScan
   - Token: https://basescan.org/address/0xbb73AC0044F8798924474d66E5c81937BDcdEccF
   - DEX: https://basescan.org/address/0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039

2. Click "Contract" tab → "Verify and Publish"

3. Fill in:
   - **Compiler Type:** Solidity (Single file)
   - **Compiler Version:** v0.8.20+commit... (match yours)
   - **License:** MIT
   - **Optimization:** Yes (if you used it, check `hardhat.config.js`)
   - **Runs:** 200 (default, or your custom value)

4. Paste flattened source code

5. Enter constructor arguments (ABI-encoded)
   - Use https://abi.hashex.org/ to encode if needed

6. Complete CAPTCHA and submit

### Step 3: Verify Success

After submission:
- ✅ Green checkmark appears on contract page
- ✅ "Read Contract" and "Write Contract" tabs enabled
- ✅ Source code visible to everyone

---

## 🧪 Get Constructor Arguments (if needed)

### Using Etherscan

1. Go to contract page
2. Click "Contract" tab
3. Scroll to bottom → "Constructor Arguments"
4. Copy the hex string

### Using Cast

```bash
cast creation 0xbb73AC0044F8798924474d66E5c81937BDcdEccF --rpc-url https://mainnet.base.org
```

### Using Hardhat

Create `scripts/get-constructor-args.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const tokenAddress = "0xbb73AC0044F8798924474d66E5c81937BDcdEccF";
  const dexAddress = "0x96b3e11bD0Af3D985f2A23a092D66821EB5Ba039";
  
  // For DEX, constructor args are likely:
  // constructor(address _marevToken, address _usdc)
  
  const args = [
    "0xbb73AC0044F8798924474d66E5c81937BDcdEccF", // MAREV Token
    "0x833589fcd6edb6e08f4c7c32d4f71b1566469c3d"  // USDC
  ];
  
  console.log("Constructor arguments:", args);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

Run:
```powershell
npx hardhat run scripts/get-constructor-args.js
```

---

## ✅ Verification Checklist

- [ ] BaseScan API key obtained and added to `.env`
- [ ] Hardhat verify plugin installed
- [ ] Compiler version matches deployment
- [ ] Optimization settings match deployment
- [ ] Constructor arguments identified
- [ ] MAREV Token verified on BaseScan
- [ ] MAREV DEX verified on BaseScan
- [ ] "Read Contract" tab working
- [ ] "Write Contract" tab working
- [ ] Source code visible and readable

---

## 🐛 Troubleshooting

### Error: "Already Verified"
✅ Good news! Contract is already verified. Check BaseScan.

### Error: "Bytecode Mismatch"
- Ensure compiler version matches exactly
- Check optimization settings (enabled/disabled, runs)
- Verify constructor arguments are correct
- Make sure you're using the exact same Solidity version

### Error: "Invalid API Key"
- Double-check `.env` has `BASESCAN_API_KEY=...`
- Ensure no extra spaces or quotes
- Try regenerating API key on BaseScan

### Error: "Constructor Arguments Invalid"
- Get exact args from deployment transaction
- Use ABI encoding tool: https://abi.hashex.org/
- Or use `cast creation <address>` command

### Can't Find Compiler Version
Check exact version used:
```powershell
cd dex
npx hardhat compile --verbose
```

Look for: `Solidity version: 0.8.20+commit.a1b79de6`

---

## 📞 After Verification

### Update Sale Package
- [ ] Mark contracts as verified in `SALE_PACKAGE.md`
- [ ] Update BaseScan links to show verified checkmark
- [ ] Take screenshots of verified contracts
- [ ] Add to buyer pitch/demo

### Buyer Benefits
- Buyers can read contract code directly on BaseScan
- Easier integration with wallets and DEX aggregators
- Increased trust and transparency
- Better SEO for your token

---

## 📚 Resources

- **BaseScan:** https://basescan.org
- **Hardhat Verify Plugin:** https://hardhat.org/hardhat-runner/plugins/nomicfoundation-hardhat-verify
- **ABI Encoder:** https://abi.hashex.org/
- **Base Docs:** https://docs.base.org/building-with-base/contract-verification

---

**Last Updated:** March 4, 2026  
**Project:** MAREV Token + DEX Stack
