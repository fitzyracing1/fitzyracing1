const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const FACTORY_ADDRESS = process.env.FACTORY_ADDRESS || "0xD3C690a57A0165d379ff89545c5A2C4B191baE20";
const LISTING_MANAGER = process.env.LISTING_MANAGER || "0x4B99195d925B46Ec8e5620659657407cdD9698D2";
const DEX_ROUTER = process.env.STANDARD_DEX_ROUTER || "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb";
const DEX_FACTORY = process.env.STANDARD_DEX_FACTORY || "0x02a84c1b3BBD7401a5f7fa98a384EBC70bB5749E";
const BASE_TOKEN = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(deployer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const factory = await hre.ethers.getContractAt("TokenFactory", FACTORY_ADDRESS, deployer);
  const tx = await factory.setListingManager(LISTING_MANAGER, true, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce,
  });
  await tx.wait();

  const deploymentInfo = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    factory: FACTORY_ADDRESS,
    listingManager: LISTING_MANAGER,
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

  console.log("Listing manager authorized and deployment file written.");
  console.log(JSON.stringify(deploymentInfo, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
