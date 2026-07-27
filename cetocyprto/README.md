# Ceto Token

Ceto is an Ethereum-based ERC20 token with a **20% rolling mint capacity**. Each rolling window (1 day) caps additional minting to 20% of the supply recorded at the start of that window, aiming to provide predictable issuance for a currency-like token.

## Requirements
- Node.js 18+
- npm

## Install
```powershell
npm install
```

## Test
```powershell
npx hardhat test
```

## Deploy locally (Hardhat network)
```powershell
npx hardhat run scripts/deploy.js --network hardhat
```

## Check status (deploys temporary if no address set)
```powershell
# Option A: attach to an existing deployment
$env:TOKEN_ADDRESS="0xYourTokenAddress"
npx hardhat run scripts/status.js --network hardhat

# Option B: run without TOKEN_ADDRESS to deploy a temporary token on the target network
npx hardhat run scripts/status.js --network hardhat
```

## Rolling capacity rules
- Window length: 1 day (configurable in contract source before deployment).
- Limit per window: 20% of the supply snapshot at window start.
- Owner-only minting; exceeding the window allowance reverts.

## Files of interest
- `contracts/CetoToken.sol` — ERC20 with rolling capacity controls.
- `test/CetoToken.js` — coverage for mint caps and window resets.
- `scripts/deploy.js` — deploys the token with 1,000,000 initial supply to the deployer.
- `scripts/status.js` — prints total supply and remaining mint capacity (deploys temporary instance if no address provided).

## Next steps
- Add named networks and private keys to `hardhat.config.js` for real deployments.
- Adjust window length or initial supply as needed for your rollout plan.
