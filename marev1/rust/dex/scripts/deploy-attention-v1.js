const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const network = hre.network.name;

  console.log(`Deploying Attention V1 to ${network}...`);
  console.log(`Deployer: ${deployer.address}`);

  const cap = hre.ethers.parseEther("1000000000"); // 1B ATTN

  const AttentionToken = await hre.ethers.getContractFactory("AttentionToken");
  const token = await AttentionToken.deploy("Attention Token", "ATTN", cap, deployer.address);
  await token.waitForDeployment();
  const tokenAddress = await token.getAddress();
  console.log(`AttentionToken: ${tokenAddress}`);

  const AttentionOracle = await hre.ethers.getContractFactory("AttentionOracle");
  const oracle = await AttentionOracle.deploy(deployer.address);
  await oracle.waitForDeployment();
  const oracleAddress = await oracle.getAddress();
  console.log(`AttentionOracle: ${oracleAddress}`);

  const AttentionDistributor = await hre.ethers.getContractFactory("AttentionDistributor");
  const distributor = await AttentionDistributor.deploy(tokenAddress, oracleAddress, deployer.address);
  await distributor.waitForDeployment();
  const distributorAddress = await distributor.getAddress();
  console.log(`AttentionDistributor: ${distributorAddress}`);

  const setMinterTx = await token.setMinter(distributorAddress, true);
  await setMinterTx.wait();
  console.log("Distributor granted minter role");

  const deploymentInfo = {
    network,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    deployer: deployer.address,
    cap: cap.toString(),
    token: tokenAddress,
    oracle: oracleAddress,
    distributor: distributorAddress,
    deploymentTime: new Date().toISOString(),
  };

  const filename = `deployments-attention-${network}.json`;
  const outputPath = path.join(__dirname, "..", filename);
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`Saved: ${filename}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
