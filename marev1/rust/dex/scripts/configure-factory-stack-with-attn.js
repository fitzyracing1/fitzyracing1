const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const FACTORY_ADDRESS = process.env.FACTORY_ADDRESS;
const LISTING_MANAGER = process.env.LISTING_MANAGER || "";
const DEX_ROUTER = process.env.STANDARD_DEX_ROUTER || "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb";
const DEX_FACTORY = process.env.STANDARD_DEX_FACTORY || "0x02a84c1b3BBD7401a5f7fa98a384EBC70bB5749E";
const BASE_TOKEN = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const ATTN_HOOK = process.env.ATTN_REWARDS_HOOK || "0x88cb287A480DCE4b88e6A0263dc4BCfc4cf7E7d6";

async function main() {
  if (!FACTORY_ADDRESS) throw new Error("FACTORY_ADDRESS is required");

  const [deployer] = await hre.ethers.getSigners();
  const startNonce = await hre.ethers.provider.getTransactionCount(deployer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const factory = await hre.ethers.getContractAt("TokenFactory", FACTORY_ADDRESS, deployer);
  const rewards = await hre.ethers.getContractAt("AttentionActivityRewards", ATTN_HOOK, deployer);

  let listingManagerAddress = LISTING_MANAGER;
  if (!listingManagerAddress) {
    const ListingManager = await hre.ethers.getContractFactory("StandardDexLiquidityManager");
    const listingManager = await ListingManager.deploy(
      BASE_TOKEN,
      DEX_ROUTER,
      DEX_FACTORY,
      FACTORY_ADDRESS,
      {
        ...(gasPrice ? { gasPrice } : {}),
        nonce: startNonce,
      }
    );
    await listingManager.waitForDeployment();
    listingManagerAddress = await listingManager.getAddress();
    console.log(`LISTING_MANAGER=${listingManagerAddress}`);
  }

  const baseNonce = listingManagerAddress === LISTING_MANAGER ? startNonce : startNonce + 1;

  const setDexTx = await factory.setDexAddress(DEX_ROUTER, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: baseNonce,
  });
  await setDexTx.wait();

  const setManagerTx = await factory.setListingManager(listingManagerAddress, true, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: baseNonce + 1,
  });
  await setManagerTx.wait();

  const setHookTx = await factory.setAttentionRewardsHook(ATTN_HOOK, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: baseNonce + 2,
  });
  await setHookTx.wait();

  const authFactoryTx = await rewards.setAuthorizedHook(FACTORY_ADDRESS, true, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: baseNonce + 3,
  });
  await authFactoryTx.wait();

  const deploymentInfo = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    factory: FACTORY_ADDRESS,
    listingManager: listingManagerAddress,
    dexRouter: DEX_ROUTER,
    dexFactory: DEX_FACTORY,
    dex: DEX_ROUTER,
    baseToken: BASE_TOKEN,
    attentionRewardsHook: ATTN_HOOK,
    launchFee: (await factory.launchFee()).toString(),
    deployer: deployer.address,
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

  console.log(JSON.stringify(deploymentInfo, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
