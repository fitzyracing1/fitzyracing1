const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const initialSupply = hre.ethers.parseUnits("1000000", 18);

  console.log("Deploying with account:", deployer.address);
  console.log("Initial supply:", initialSupply.toString());

  const Token = await hre.ethers.getContractFactory("CetoToken");
  const token = await Token.deploy(initialSupply, deployer.address);
  await token.waitForDeployment();

  console.log("CetoToken deployed to:", await token.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
