# Attention Token V1

This module implements a minimal multi-platform attention rewards flow:

1. `AttentionOracle` stores one Merkle root per day and finalizes it.
2. `AttentionDistributor` verifies claims against finalized roots.
3. `AttentionToken` mints claim rewards to wallets with valid proofs.

## Contracts

- `contracts/AttentionToken.sol`
- `contracts/AttentionOracle.sol`
- `contracts/AttentionDistributor.sol`

## Leaf Format

Claims are validated with:

`keccak256(abi.encode(day, wallet, score, amount))`

Where:

- `day`: settlement day index
- `wallet`: claimant address
- `score`: normalized score computed off-chain
- `amount`: token reward amount

## Local Test

Run from `dex/`:

```powershell
npx hardhat test test/attention.test.js
```

## Deploy (Base)

```powershell
npm run deploy:attention
```

This writes `deployments-attention-base.json` with contract addresses.

## Build Daily Merkle Claims

Create an input file (example `data/day-1-input.json`):

```json
[
	{
		"wallet": "0x1111111111111111111111111111111111111111",
		"score": "250",
		"amountWei": "100000000000000000000"
	},
	{
		"wallet": "0x2222222222222222222222222222222222222222",
		"score": "750",
		"amountWei": "300000000000000000000"
	}
]
```

Then generate root + proofs:

```powershell
node scripts/attention-build-merkle.js --day 1 --input .\data\day-1-input.json --output .\data\day-1-output.json
```

## Build ATTN Rewards From Meme Factory Activity

If you want meme coin creators/listed projects to become claimable on `/attention`, generate a day input directly from the live factory:

```powershell
node scripts/attention-build-factory-day.js --day 2 --output .\data\day-2-factory-input.json
```

Default scoring:

- `+100` score for each created token
- `+400` score and `100 ATTN` for each listed token

You can override these with flags or env vars:

```powershell
node scripts/attention-build-factory-day.js --day 2 --created-score 100 --listed-score 400 --listed-amount-wei 100000000000000000000
```

If you also have manual reward rows, merge them before building the Merkle tree:

```powershell
node scripts/attention-merge-inputs.js --input .\data\day-2-manual-input.json --input .\data\day-2-factory-input.json --output .\data\day-2-input.json
node scripts/attention-build-merkle.js --day 2 --input .\data\day-2-input.json --output .\data\day-2-output.json
```

Use the generated output to:

1. Submit root to `AttentionOracle.submitDayRoot(...)`
2. Finalize day with `AttentionOracle.finalizeDay(day)`
3. Claim from frontend at `/attention.html` with `day`, `score`, `amountWei`, and `proof`
