const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.resolve(file), "utf8"));
}

async function main() {
  const activityPath = process.env.ATTN_ACTIVITY_DEPLOYMENT || path.join(__dirname, "..", "deployments-attention-activity-base.json");
  const factoryPath = process.env.FACTORY_DEPLOYMENT || path.join(__dirname, "..", "deployments-factory-base.json");
  const attentionPath = process.env.ATTENTION_DEPLOYMENT || path.join(__dirname, "..", "deployments-attention-base.json");

  const activity = readJson(activityPath);
  const factoryDeployment = readJson(factoryPath);
  const attentionDeployment = readJson(attentionPath);

  const [deployer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(deployer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const token = await hre.ethers.getContractAt("AttentionToken", attentionDeployment.token, deployer);
  const rewards = await hre.ethers.getContractAt("AttentionActivityRewards", activity.rewardsHook, deployer);
  const factory = await hre.ethers.getContractAt("TokenFactory", factoryDeployment.factory, deployer);

  const setMinterTx = await token.setMinter(activity.rewardsHook, true, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce,
  });
  await setMinterTx.wait();
  console.log("Attention activity hook set as ATTN minter.");

  const setHookAuthTx = await rewards.setAuthorizedHook(factoryDeployment.factory, true, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: nonce + 1,
  });
  await setHookAuthTx.wait();
  console.log("Factory authorized in rewards hook.");

  const setFactoryHookTx = await factory.setAttentionRewardsHook(activity.rewardsHook, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: nonce + 2,
  });
  await setFactoryHookTx.wait();
  console.log("Factory connected to on-chain ATTN rewards hook.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
