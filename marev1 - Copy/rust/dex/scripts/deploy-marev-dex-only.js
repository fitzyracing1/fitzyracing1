const hre = require("hardhat");

async function main() {
  const marevAddress = process.env.MAREV_TOKEN_ADDRESS;
  const usdcAddress = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

  if (!marevAddress) {
    throw new Error("MAREV_TOKEN_ADDRESS env var is required");
  }

  const [deployer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(deployer.address);
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 120n) / 100n : null;

  console.log("Deploying MAREV DEX only...");
  console.log("Deployer:", deployer.address);
  console.log("Nonce:", nonce);
  console.log("MAREV Token:", marevAddress);
  console.log("USDC:", usdcAddress);

  const MAREVDex = await hre.ethers.getContractFactory("MAREVDex");
  const dex = await MAREVDex.deploy(marevAddress, usdcAddress, deployer.address, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce,
  });
  await dex.waitForDeployment();

  const dexAddress = await dex.getAddress();
  const addresses = {
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    marevToken: marevAddress,
    dex: dexAddress,
    usdc: usdcAddress,
    deployer: deployer.address,
    deploymentTime: new Date().toISOString(),
    isTestnet: false,
  };

  const fs = require("fs");
  fs.writeFileSync("deployments-base.json", JSON.stringify(addresses, null, 2));

  console.log("DEX deployed to:", dexAddress);
  console.log(JSON.stringify(addresses, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
