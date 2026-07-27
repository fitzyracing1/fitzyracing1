const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const ACCOUNT = process.env.ACCOUNT;

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.resolve(file), "utf8"));
}

async function main() {
  const activityPath = path.join(__dirname, "..", "deployments-attention-activity-base.json");
  const activity = readJson(activityPath);
  const account = ACCOUNT || (await hre.ethers.getSigners())[0].address;

  const rewards = await hre.ethers.getContractAt("AttentionActivityRewards", activity.rewardsHook);
  const day = await rewards.currentDay();
  const [score, amount, alreadyClaimed] = await rewards.previewRewards(day, account);

  console.log(JSON.stringify({
    day: day.toString(),
    account,
    score: score.toString(),
    amountWei: amount.toString(),
    amountFormatted: hre.ethers.formatEther(amount),
    alreadyClaimed,
  }, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
