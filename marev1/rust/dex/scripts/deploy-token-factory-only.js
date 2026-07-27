const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(deployer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;
  const launchFee = hre.ethers.parseEther("0.001");

  const TokenFactory = await hre.ethers.getContractFactory("TokenFactory");
  const factory = await TokenFactory.deploy(launchFee, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce,
  });
  await factory.waitForDeployment();

  console.log(`FACTORY_ADDRESS=${await factory.getAddress()}`);
  console.log(`DEPLOYER=${deployer.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
