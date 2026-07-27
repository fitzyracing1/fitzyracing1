const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const FACTORY_ADDRESS = process.env.FACTORY_ADDRESS;
const LISTING_MANAGER = process.env.LISTING_MANAGER;
const DEX_ROUTER = process.env.STANDARD_DEX_ROUTER || "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb";
const ATTN_HOOK = process.env.ATTN_REWARDS_HOOK || "0x88cb287A480DCE4b88e6A0263dc4BCfc4cf7E7d6";
const ACTION = process.env.ACTION;
const BASE_TOKEN = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const DEX_FACTORY = process.env.STANDARD_DEX_FACTORY || "0x02a84c1b3BBD7401a5f7fa98a384EBC70bB5749E";

async function writeDeployment(factoryAddress, listingManagerAddress, deployer) {
  const factory = await hre.ethers.getContractAt("TokenFactory", factoryAddress);
  const deploymentInfo = {
    network: hre.network.name,
    chainId: (hre.network.config.chainId || 0).toString(),
    factory: factoryAddress,
    listingManager: listingManagerAddress,
    dexRouter: DEX_ROUTER,
    dexFactory: DEX_FACTORY,
    dex: DEX_ROUTER,
    baseToken: BASE_TOKEN,
    attentionRewardsHook: ATTN_HOOK,
    launchFee: (await factory.launchFee()).toString(),
    deployer,
    deploymentTime: new Date().toISOString(),
    isTestnet: hre.network.name !== "base",
  };

  const dexDir = path.join(__dirname, "..");
  const vercelDir = path.join(__dirname, "..", "..", "vercel");
  const filename = `deployments-factory-${hre.network.name}.json`;
  fs.writeFileSync(path.join(dexDir, filename), JSON.stringify(deploymentInfo, null, 2));
  if (fs.existsSync(vercelDir)) {
    fs.writeFileSync(path.join(vercelDir, filename), JSON.stringify(deploymentInfo, null, 2));
  }
}

async function main() {
  if (!FACTORY_ADDRESS) throw new Error("FACTORY_ADDRESS is required");
  if (!ACTION) throw new Error("ACTION is required");

  const [deployer] = await hre.ethers.getSigners();
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const factory = await hre.ethers.getContractAt("TokenFactory", FACTORY_ADDRESS, deployer);
  const rewards = await hre.ethers.getContractAt("AttentionActivityRewards", ATTN_HOOK, deployer);

  let tx;
  if (ACTION === "setDex") {
    tx = await factory.setDexAddress(DEX_ROUTER, {
      ...(gasPrice ? { gasPrice } : {}),
    });
  } else if (ACTION === "setManager") {
    if (!LISTING_MANAGER) throw new Error("LISTING_MANAGER is required for setManager");
    tx = await factory.setListingManager(LISTING_MANAGER, true, {
      ...(gasPrice ? { gasPrice } : {}),
    });
  } else if (ACTION === "setHook") {
    tx = await factory.setAttentionRewardsHook(ATTN_HOOK, {
      ...(gasPrice ? { gasPrice } : {}),
    });
  } else if (ACTION === "authorizeFactory") {
    tx = await rewards.setAuthorizedHook(FACTORY_ADDRESS, true, {
      ...(gasPrice ? { gasPrice } : {}),
    });
  } else if (ACTION === "writeDeployment") {
    if (!LISTING_MANAGER) throw new Error("LISTING_MANAGER is required for writeDeployment");
    await writeDeployment(FACTORY_ADDRESS, LISTING_MANAGER, deployer.address);
    console.log("Deployment files updated.");
    return;
  } else {
    throw new Error(`Unknown ACTION: ${ACTION}`);
  }

  await tx.wait();
  console.log(`${ACTION} complete: ${tx.hash}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
