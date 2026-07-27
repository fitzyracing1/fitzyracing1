const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.resolve(file), "utf8"));
}

async function main() {
  const activityPath = path.join(__dirname, "..", "deployments-attention-activity-base.json");
  const activity = readJson(activityPath);
  const attentionPath = path.join(__dirname, "..", "deployments-attention-base.json");
  const attention = readJson(attentionPath);
  const [signer] = await hre.ethers.getSigners();
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const rewards = await hre.ethers.getContractAt("AttentionActivityRewards", activity.rewardsHook, signer);
  const token = await hre.ethers.getContractAt("AttentionToken", attention.token, signer);
  const day = await rewards.currentDay();
  const before = await token.balanceOf(signer.address);

  const tx = await rewards.claim(day, {
    ...(gasPrice ? { gasPrice } : {}),
  });
  await tx.wait();

  const after = await token.balanceOf(signer.address);
  console.log(`CLAIM_TX=${tx.hash}`);
  console.log(`BALANCE_BEFORE=${before.toString()}`);
  console.log(`BALANCE_AFTER=${after.toString()}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
