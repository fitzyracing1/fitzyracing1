const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const TOKEN_ADDRESS = process.env.TOKEN_ADDRESS;
const TOKEN_LIQUIDITY = process.env.TOKEN_LIQUIDITY || "10";

function readDeployment() {
  const file = path.join(__dirname, "..", "deployments-factory-base.json");
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

async function main() {
  if (!TOKEN_ADDRESS) throw new Error("TOKEN_ADDRESS is required");

  const deployment = readDeployment();
  const [signer] = await hre.ethers.getSigners();
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const token = await hre.ethers.getContractAt("MemeToken", TOKEN_ADDRESS, signer);
  const tx = await token.approve(
    deployment.listingManager,
    hre.ethers.parseUnits(TOKEN_LIQUIDITY, 18),
    {
      ...(gasPrice ? { gasPrice } : {}),
    }
  );
  await tx.wait();
  console.log(`TOKEN_APPROVAL_TX=${tx.hash}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
