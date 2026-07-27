const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");

const FACTORY_ABI = [
  "function getTotalTokens() view returns (uint256)",
  "function allTokens(uint256 index) view returns (address)",
  "function getTokenInfo(address token) view returns (string, string, address, uint256, uint256, bool)",
];

function getArg(flag, fallback = null) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function normalizeAddress(address) {
  return ethers.getAddress(address);
}

async function main() {
  const day = getArg("--day");
  const rpcUrl = process.env.BASE_RPC_URL || getArg("--rpc", "https://mainnet.base.org");
  const deploymentPath = process.env.FACTORY_DEPLOYMENT_PATH || getArg(
    "--deployment",
    path.join(__dirname, "..", "deployments-factory-base.json")
  );
  const outputPath = process.env.OUTPUT_PATH || getArg(
    "--output",
    path.join(__dirname, "..", "data", `day-${day}-factory-input.json`)
  );
  const createdScore = BigInt(process.env.ATTN_CREATED_SCORE || getArg("--created-score", "100"));
  const listedScore = BigInt(process.env.ATTN_LISTED_SCORE || getArg("--listed-score", "400"));
  const listedBonusWei = BigInt(process.env.ATTN_LISTED_AMOUNT_WEI || getArg("--listed-amount-wei", "100000000000000000000"));
  const createdBonusWei = BigInt(process.env.ATTN_CREATED_AMOUNT_WEI || getArg("--created-amount-wei", "0"));

  if (!day) {
    throw new Error("Missing --day <DAY>");
  }

  const deployment = JSON.parse(fs.readFileSync(path.resolve(deploymentPath), "utf8"));
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const factory = new ethers.Contract(deployment.factory, FACTORY_ABI, provider);

  const totalTokens = Number(await factory.getTotalTokens());
  const rewardMap = new Map();

  for (let i = 0; i < totalTokens; i++) {
    const tokenAddress = await factory.allTokens(i);
    const [, , creator, createdAt, , isListed] = await factory.getTokenInfo(tokenAddress);
    const wallet = normalizeAddress(creator);
    const current = rewardMap.get(wallet) || { wallet, score: 0n, amountWei: 0n, createdTokens: [], listedTokens: [] };

    current.score += createdScore;
    current.amountWei += createdBonusWei;
    current.createdTokens.push({
      tokenAddress,
      createdAt: createdAt.toString(),
    });

    if (isListed) {
      current.score += listedScore;
      current.amountWei += listedBonusWei;
      current.listedTokens.push(tokenAddress);
    }

    rewardMap.set(wallet, current);
  }

  const rewards = Array.from(rewardMap.values())
    .filter((entry) => entry.score > 0n && entry.amountWei > 0n)
    .sort((a, b) => a.wallet.localeCompare(b.wallet))
    .map((entry) => ({
      wallet: entry.wallet,
      score: entry.score.toString(),
      amountWei: entry.amountWei.toString(),
      createdTokens: entry.createdTokens,
      listedTokens: entry.listedTokens,
      source: "factory",
      day: String(day),
    }));

  fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
  fs.writeFileSync(path.resolve(outputPath), `${JSON.stringify(rewards, null, 2)}\n`);

  console.log(`Factory: ${deployment.factory}`);
  console.log(`Tokens scanned: ${totalTokens}`);
  console.log(`Reward wallets: ${rewards.length}`);
  console.log(`Output: ${path.resolve(outputPath)}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
