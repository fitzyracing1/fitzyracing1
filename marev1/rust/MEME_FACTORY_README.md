# MAREV Meme Coin Factory

**Launch your own meme coin in seconds** — No coding required!

---

## 🎯 What Is This?

A complete **permissionless token factory** that lets anyone create and launch their own ERC-20 meme coin with instant DEX listing capabilities. Perfect for:

- Meme coin enthusiasts
- Community token creators
- NFT project tokens
- DAO governance tokens
- Pump.fun style platforms

---

## ✨ Features

### Token Factory
- ✅ **One-click token creation** - No coding needed
- ✅ **Standard ERC-20** - Works with all wallets and DEXs
- ✅ **Customizable** - Name, symbol, decimals, supply
- ✅ **Low launch fee** - 0.001 ETH per token
- ✅ **Instant deployment** - Live in seconds
- ✅ **Token ownership** - You control your token

### Multi-Pair DEX
- ✅ **Automatic liquidity pools** - Create pools for any token
- ✅ **Low trading fees** - 0.3% per swap
- ✅ **Fair pricing** - Constant product AMM (like Uniswap)
- ✅ **Liquidity rewards** - Earn fees as LP
- ✅ **Slippage protection** - Safe trading

### Frontend
- ✅ **Beautiful UI** - Easy to use interface
- ✅ **MetaMask integration** - One-click connect
- ✅ **Token discovery** - Browse all created tokens
- ✅ **Mobile friendly** - Works on any device

---

## 🚀 Quick Start

### For Token Creators

1. **Connect Wallet**
   - Visit the factory website
   - Click "Connect Wallet"
   - Approve MetaMask connection

2. **Create Your Token**
   - Enter token name (e.g., "Pepe Coin")
   - Enter symbol (e.g., "PEPE")
   - Set decimals (usually 18)
   - Set initial supply (e.g., 1,000,000)
   - Pay 0.001 ETH launch fee
   - Confirm transaction

3. **Add Liquidity** (Optional)
   - Go to DEX interface
   - Create liquidity pool
   - Add your token + USDC
   - Enable trading

4. **Share & Promote**
   - Share your token address
   - Add to social media
   - Build your community

### For Developers

```bash
# Clone repository
git clone <repo-url>
cd marev1/rust

# Install dependencies
cd dex
npm install

# Deploy contracts
npx hardhat run scripts/deploy-factory.js --network base

# Run tests
npx hardhat test test/factory.test.js

# Deploy frontend
cd ../vercel
# Update contract addresses in factory.js
vercel deploy --prod
```

---

## 📊 Deployed Contracts

### Base Mainnet
- **Factory:** `YOUR_FACTORY_ADDRESS`
- **DEX:** `YOUR_DEX_ADDRESS`
- **Base Token:** `0x833589fcd6edb6e08f4c7c32d4f71b1566469c3d` (USDC)

### Base Sepolia Testnet
- **Factory:** `YOUR_TESTNET_FACTORY_ADDRESS`
- **DEX:** `YOUR_TESTNET_DEX_ADDRESS`
- **Base Token:** `0x036CbD53842c5426634e7929541eC2318f3dCF7e` (USDC)

---

## 💰 Economics

### Launch Fee
- **Cost:** 0.001 ETH per token
- **Purpose:** Prevent spam, fund development
- **Collected by:** Factory owner
- **Can change:** Yes (owner only)

### Trading Fees
- **Fee:** 0.3% per swap
- **Distribution:** Goes to liquidity providers
- **Standard:** Same as Uniswap V2

### Liquidity
- **Minimum:** 1000 units locked forever (prevents rug pulls)
- **Provider rewards:** Earn fees proportional to your share
- **Remove anytime:** Withdraw your liquidity whenever

---

## 🏗️ Architecture

### Smart Contracts

#### TokenFactory.sol
- Creates new MemeToken instances
- Tracks all created tokens
- Collects launch fees
- Links tokens to DEX

#### MemeToken.sol
- Standard ERC-20 implementation
- Mintable by owner
- Burnable by holders
- OpenZeppelin based

#### MemeDex.sol
- Multi-pair AMM DEX
- Constant product formula (x * y = k)
- Pool creation for any token
- Trading with slippage protection

### Frontend
- `factory.html` - Token creation interface
- `factory.js` - Web3 interactions
- `dex.html` - Trading interface (existing)
- `dex.js` - DEX interactions (existing)

---

## 🛠️ Development

### Prerequisites
- Node.js 18+
- npm or yarn
- MetaMask wallet
- Base ETH for gas

### Setup

```bash
# Install dependencies
cd dex
npm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Run local node
npx hardhat node

# Deploy locally
npx hardhat run scripts/deploy-factory.js --network localhost
```

### Testing

```bash
# All tests
npx hardhat test

# Factory tests only
npx hardhat test test/factory.test.js

# Original DEX tests
npx hardhat test test/dex.test.js

# With gas reporting
REPORT_GAS=true npx hardhat test
```

### Deployment

```bash
# Deploy to Base Sepolia (testnet)
npx hardhat run scripts/deploy-factory.js --network base-sepolia

# Deploy to Base Mainnet
npx hardhat run scripts/deploy-factory.js --network base

# Verify contracts
npx hardhat verify --network base <FACTORY_ADDRESS> "1000000000000000"
npx hardhat verify --network base <DEX_ADDRESS> "<BASE_TOKEN>" "<FEE_RECIPIENT>"
```

---

## 📖 Usage Examples

### Create Token (JavaScript)

```javascript
const factory = new ethers.Contract(FACTORY_ADDRESS, FACTORY_ABI, signer);
const launchFee = await factory.launchFee();

const tx = await factory.createToken(
  "Pepe Coin",           // name
  "PEPE",                // symbol
  18,                    // decimals
  ethers.parseEther("1000000"),  // supply
  { value: launchFee }
);

const receipt = await tx.wait();
const event = receipt.events.find(e => e.event === 'TokenCreated');
console.log("Token created at:", event.args.tokenAddress);
```

### Create Liquidity Pool

```javascript
const dex = new ethers.Contract(DEX_ADDRESS, DEX_ABI, signer);
const token = new ethers.Contract(TOKEN_ADDRESS, TOKEN_ABI, signer);
const usdc = new ethers.Contract(USDC_ADDRESS, TOKEN_ABI, signer);

// Approve tokens
await token.approve(DEX_ADDRESS, ethers.parseEther("10000"));
await usdc.approve(DEX_ADDRESS, ethers.parseUnits("100", 6));

// Create pool
await dex.createPool(
  TOKEN_ADDRESS,
  ethers.parseEther("10000"),    // 10,000 tokens
  ethers.parseUnits("100", 6)    // 100 USDC
);
```

### Swap Tokens

```javascript
const dex = new ethers.Contract(DEX_ADDRESS, DEX_ABI, signer);
const usdc = new ethers.Contract(USDC_ADDRESS, TOKEN_ABI, signer);

// Buy tokens with USDC
const swapAmount = ethers.parseUnits("10", 6); // 10 USDC
await usdc.approve(DEX_ADDRESS, swapAmount);

const minOut = await dex.getAmountOut(USDC_ADDRESS, TOKEN_ADDRESS, swapAmount);
await dex.swap(USDC_ADDRESS, TOKEN_ADDRESS, swapAmount, minOut);
```

---

## 🔐 Security

### Audits
- ⚠️ **Not audited** - Use at your own risk
- Built with OpenZeppelin contracts (battle-tested)
- Extensive unit tests (12 passing)

### Best Practices
- ✅ ReentrancyGuard on all state-changing functions
- ✅ SafeERC20 for token transfers
- ✅ Access control with Ownable
- ✅ Slippage protection on swaps
- ✅ Minimum liquidity locked forever

### Known Limitations
- No emergency pause mechanism
- No upgrade path for deployed tokens
- Factory owner can change launch fee
- No token blacklist/whitelist

---

## 🎨 Customization

### Change Launch Fee

```solidity
// Only factory owner
factory.setLaunchFee(ethers.parseEther("0.002")); // 0.002 ETH
```

### Change Trading Fee

Currently hardcoded at 0.3% (30 basis points). To change:
1. Edit `MemeDex.sol` → `FEE_BASIS_POINTS`
2. Recompile and redeploy
3. Update frontend

### Custom Token Features

Edit `MemeToken.sol` to add:
- Tax on transfers
- Max transaction limits
- Automatic buyback/burn
- Reflection rewards
- Anti-whale limits

---

## 📈 Roadmap

### Phase 1: Launch (Current)
- [x] TokenFactory contract
- [x] MemeDex multi-pair DEX
- [x] Web interface
- [x] Base mainnet deployment
- [x] Documentation

### Phase 2: Enhancement
- [ ] Token analytics dashboard
- [ ] Price charts (TradingView)
- [ ] Token search/filter
- [ ] Social links per token
- [ ] Trending tokens page

### Phase 3: Advanced
- [ ] Bonding curves (like pump.fun)
- [ ] Auto-liquidity lock
- [ ] Token vesting schedules
- [ ] Multi-chain deployment
- [ ] DAO governance

### Phase 4: Monetization
- [ ] Premium token features
- [ ] Promoted listings
- [ ] Advertisement space
- [ ] API for developers
- [ ] White-label solutions

---

## 💡 Business Model

### Revenue Streams
1. **Launch fees** - 0.001 ETH per token
2. **Trading fees** - 0.3% per swap (to LPs)
3. **Premium features** - Enhanced listings
4. **Promotions** - Featured tokens
5. **White-label** - Custom instances

### Scaling Strategy
- 1000 tokens/month = 1 ETH revenue (~$3,000)
- 10,000 tokens/month = 10 ETH revenue (~$30,000)
- Plus trading volume fees
- Plus premium services

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## ⚠️ Disclaimer

**IMPORTANT:** This is experimental software.

- **No financial advice** - DYOR before using
- **Use at own risk** - Smart contracts can have bugs
- **No guarantees** - Token value not guaranteed
- **Regulatory compliance** - Your responsibility
- **Not audited** - No professional security audit

By using this software, you agree to these terms.

---

## 📞 Support

- **Documentation:** This file + inline code comments
- **Issues:** GitHub Issues
- **Community:** Discord/Telegram (add links)
- **Email:** your@email.com

---

## 🙏 Credits

Built with:
- OpenZeppelin Contracts
- Hardhat
- Ethers.js
- Base Network

Inspired by:
- Uniswap V2
- Pump.fun
- SushiSwap Factory

---

**Built with ❤️ by the MAREV team**

Ready to launch your meme coin empire? 🚀
