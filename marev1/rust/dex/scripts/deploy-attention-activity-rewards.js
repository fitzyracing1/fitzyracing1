const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const ATTN_TOKEN = process.env.ATTN_TOKEN || "0x9d2d92664bab6d667b8EfE1C81E276F4cff2eb35";

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(deployer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const startTimestamp = BigInt(process.env.ATTN_ACTIVITY_START || Math.floor(Date.now() / 1000));
  const dayDuration = BigInt(process.env.ATTN_ACTIVITY_DAY_DURATION || 86400);
  const createdScore = BigInt(process.env.ATTN_CREATED_SCORE || 100);
  const createdAmount = BigInt(process.env.ATTN_CREATED_AMOUNT_WEI || 0);
  const listedScore = BigInt(process.env.ATTN_LISTED_SCORE || 400);
  const listedAmount = BigInt(process.env.ATTN_LISTED_AMOUNT_WEI || hre.ethers.parseEther("100"));

  const Rewards = await hre.ethers.getContractFactory("AttentionActivityRewards");
  const rewards = await Rewards.deploy(
    ATTN_TOKEN,
    startTimestamp,
    dayDuration,
    createdScore,
    createdAmount,
    listedScore,
    listedAmount,
    deployer.address,
    {
      ...(gasPrice ? { gasPrice } : {}),
      nonce,
    }
  );
  await rewards.waitForDeployment();

  const address = await rewards.getAddress();
  const info = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    attentionToken: ATTN_TOKEN,
    rewardsHook: address,
    startTimestamp: startTimestamp.toString(),
    dayDuration: dayDuration.toString(),
    createdScore: createdScore.toString(),
    createdAmountWei: createdAmount.toString(),
    listedScore: listedScore.toString(),
    listedAmountWei: listedAmount.toString(),
    deployer: deployer.address,
    deploymentTime: new Date().toISOString(),
  };

  const file = path.join(__dirname, "..", `deployments-attention-activity-${hre.network.name}.json`);
  fs.writeFileSync(file, JSON.stringify(info, null, 2));

  console.log(`Attention activity rewards deployed: ${address}`);
  console.log(JSON.stringify(info, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
