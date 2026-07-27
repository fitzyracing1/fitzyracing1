const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const network = hre.network.name;

  console.log(`\nDeploying Meme Coin Factory to ${network.toUpperCase()}...`);
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Nonce: ${await deployer.getNonce()}`);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log(`Balance: ${hre.ethers.formatEther(balance)} ETH\n`);

  const launchFee = hre.ethers.parseEther("0.001");
  const baseToken = network === "base" || network === "localhost"
    ? "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    : "0x036CbD53842c5426634e7929541eC2318f3dCF7e";

  let dexRouter = process.env.STANDARD_DEX_ROUTER;
  let dexFactory = process.env.STANDARD_DEX_FACTORY;

  console.log("=".repeat(60));
  console.log("DEPLOYMENT PARAMETERS");
  console.log("=".repeat(60));
  console.log(`Launch Fee: ${hre.ethers.formatEther(launchFee)} ETH`);
  console.log(`Base Token (USDC): ${baseToken}`);
  console.log(`Fee Recipient: ${deployer.address}`);

  if (network === "localhost") {
    console.log("Deploying local standard DEX mocks...");

    const FactoryMock = await hre.ethers.getContractFactory("UniswapV2FactoryMock");
    const RouterMock = await hre.ethers.getContractFactory("UniswapV2RouterMock");

    const factoryMock = await FactoryMock.deploy();
    await factoryMock.waitForDeployment();

    const routerMock = await RouterMock.deploy(await factoryMock.getAddress());
    await routerMock.waitForDeployment();

    dexFactory = await factoryMock.getAddress();
    dexRouter = await routerMock.getAddress();
  }

  if (!dexRouter || !dexFactory) {
    throw new Error(
      "Missing standard DEX config. Set STANDARD_DEX_ROUTER and STANDARD_DEX_FACTORY."
    );
  }

  console.log(`Standard DEX Router: ${dexRouter}`);
  console.log(`Standard DEX Factory: ${dexFactory}\n`);

  console.log("1. Deploying TokenFactory...");
  const TokenFactory = await hre.ethers.getContractFactory("TokenFactory");
  const factory = await TokenFactory.deploy(launchFee);
  await factory.waitForDeployment();
  const factoryAddress = await factory.getAddress();
  console.log(`TokenFactory deployed: ${factoryAddress}\n`);

  console.log("2. Storing the default listing target...");
  const setDexTx = await factory.setDexAddress(dexRouter);
  await setDexTx.wait();
  console.log(`Factory default listing target set: ${dexRouter}\n`);

  console.log("3. Deploying StandardDexLiquidityManager...");
  const StandardDexLiquidityManager = await hre.ethers.getContractFactory("StandardDexLiquidityManager");
  const listingManager = await StandardDexLiquidityManager.deploy(
    baseToken,
    dexRouter,
    dexFactory,
    factoryAddress
  );
  await listingManager.waitForDeployment();
  const listingManagerAddress = await listingManager.getAddress();
  console.log(`Listing manager deployed: ${listingManagerAddress}\n`);

  console.log("4. Authorizing listing manager...");
  const setManagerTx = await factory.setListingManager(listingManagerAddress, true);
  await setManagerTx.wait();
  console.log("Listing manager authorized\n");

  const deploymentInfo = {
    network,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    factory: factoryAddress,
    listingManager: listingManagerAddress,
    dexRouter,
    dexFactory,
    dex: dexRouter,
    baseToken,
    launchFee: launchFee.toString(),
    deployer: deployer.address,
    deploymentTime: new Date().toISOString(),
    isTestnet: network !== "base"
  };

  const deploymentsDir = path.join(__dirname, "..");
  const filename = `deployments-factory-${network}.json`;
  const filepath = path.join(deploymentsDir, filename);

  fs.writeFileSync(filepath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`Deployment info saved to ${filename}`);

  const vercelDir = path.join(__dirname, "..", "..", "vercel");
  if (fs.existsSync(vercelDir)) {
    const vercelPath = path.join(vercelDir, filename);
    fs.writeFileSync(vercelPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`Deployment info copied to vercel/${filename}`);
  }

  console.log("\n" + "=".repeat(60));
  console.log("DEPLOYMENT SUMMARY");
  console.log("=".repeat(60));
  console.log(`Network: ${network}`);
  console.log(`Chain ID: ${deploymentInfo.chainId}`);
  console.log("\nContracts:");
  console.log(`  TokenFactory: ${factoryAddress}`);
  console.log(`  ListingMgr:   ${listingManagerAddress}`);
  console.log(`  Router:       ${dexRouter}`);
  console.log(`  Dex Factory:  ${dexFactory}`);
  console.log(`  Base Token:   ${baseToken}`);
  console.log("\nSettings:");
  console.log(`  Launch Fee: ${hre.ethers.formatEther(launchFee)} ETH`);
  console.log(`  Fee Recipient: ${deployer.address}`);
  console.log("\n" + "=".repeat(60));
  console.log("NEXT STEPS");
  console.log("=".repeat(60));
  console.log("1. Verify contracts on the block explorer:");
  console.log(`   npx hardhat verify --network ${network} ${factoryAddress} "${launchFee}"`);
  console.log(`   npx hardhat verify --network ${network} ${listingManagerAddress} "${baseToken}" "${dexRouter}" "${dexFactory}" "${factoryAddress}"`);
  console.log("\n2. Create a token from the factory UI.");
  console.log("3. Seed the first USDC pool from the token card.");
  console.log("4. Confirm the pair on BaseScan and your chosen DEX analytics.");
  console.log("=".repeat(60) + "\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
