const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const TOKEN_NAME = process.env.MEME_NAME || "attnproof";
const TOKEN_SYMBOL = process.env.MEME_SYMBOL || "ATPR";
const TOKEN_DECIMALS = Number(process.env.MEME_DECIMALS || "18");
const TOKEN_SUPPLY = process.env.MEME_SUPPLY || "1000000";

function readDeployment() {
  const file = path.join(__dirname, "..", "deployments-factory-base.json");
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

async function main() {
  const deployment = readDeployment();
  const [signer] = await hre.ethers.getSigners();
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const factory = await hre.ethers.getContractAt("TokenFactory", deployment.factory, signer);
  const launchFee = await factory.launchFee();
  const supplyWithDecimals = hre.ethers.parseUnits(TOKEN_SUPPLY, TOKEN_DECIMALS);

  const tx = await factory.createToken(
    TOKEN_NAME,
    TOKEN_SYMBOL,
    TOKEN_DECIMALS,
    supplyWithDecimals,
    {
      value: launchFee,
      ...(gasPrice ? { gasPrice } : {}),
    }
  );
  const receipt = await tx.wait();
  const event = receipt.logs
    .map((log) => {
      try {
        return factory.interface.parseLog(log);
      } catch {
        return null;
      }
    })
    .find((entry) => entry && entry.name === "TokenCreated");

  if (!event) {
    throw new Error("TokenCreated event not found");
  }

  console.log(`TOKEN_ADDRESS=${event.args.tokenAddress}`);
  console.log(`CREATOR=${signer.address}`);
  console.log(`CREATE_TX=${tx.hash}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
