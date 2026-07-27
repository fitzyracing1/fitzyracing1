const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const FACTORY_ADDRESS = process.env.FACTORY_ADDRESS || "0xD3C690a57A0165d379ff89545c5A2C4B191baE20";
const DEX_ROUTER = process.env.STANDARD_DEX_ROUTER || "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb";
const DEX_FACTORY = process.env.STANDARD_DEX_FACTORY || "0x02a84c1b3BBD7401a5f7fa98a384EBC70bB5749E";
const BASE_TOKEN = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const startNonce = await hre.ethers.provider.getTransactionCount(deployer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  console.log("Configuring factory stack...");
  console.log("Deployer:", deployer.address);
  console.log("Factory:", FACTORY_ADDRESS);
  console.log("Router:", DEX_ROUTER);
  console.log("Factory:", DEX_FACTORY);
  console.log("Base token:", BASE_TOKEN);
  console.log("Start nonce:", startNonce);

  const factory = await hre.ethers.getContractAt("TokenFactory", FACTORY_ADDRESS, deployer);
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
  const listingManagerAddress = await listingManager.getAddress();
  console.log("Listing manager deployed:", listingManagerAddress);

  const setDexTx = await factory.setDexAddress(DEX_ROUTER, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: startNonce + 1,
  });
  await setDexTx.wait();
  console.log("Factory default listing target set.");

  const setManagerTx = await factory.setListingManager(listingManagerAddress, true, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: startNonce + 2,
  });
  await setManagerTx.wait();
  console.log("Listing manager authorized.");

  const deploymentInfo = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    factory: FACTORY_ADDRESS,
    listingManager: listingManagerAddress,
    dexRouter: DEX_ROUTER,
    dexFactory: DEX_FACTORY,
    dex: DEX_ROUTER,
    baseToken: BASE_TOKEN,
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
