const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const TOKEN_NAME = process.env.MEME_NAME || "joshua";
const TOKEN_SYMBOL = process.env.MEME_SYMBOL || "joshua";
const TOKEN_DECIMALS = 18;
const TOKEN_SUPPLY = process.env.MEME_SUPPLY || "1000000";
const TOKEN_LIQUIDITY = process.env.TOKEN_LIQUIDITY || "50";
const USDC_LIQUIDITY = process.env.USDC_LIQUIDITY || "0.05";
const BASE_TOKEN = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

function readDeployment() {
  const file = path.join(__dirname, "..", "deployments-factory-base.json");
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

async function main() {
  const deployment = readDeployment();
  const [signer] = await hre.ethers.getSigners();
  const startNonce = await hre.ethers.provider.getTransactionCount(signer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const factory = await hre.ethers.getContractAt("TokenFactory", deployment.factory, signer);
  const listingManager = await hre.ethers.getContractAt("StandardDexLiquidityManager", deployment.listingManager, signer);
  const usdc = await hre.ethers.getContractAt([
    "function balanceOf(address account) view returns (uint256)",
    "function approve(address spender, uint256 amount) returns (bool)",
  ], BASE_TOKEN, signer);

  const launchFee = await factory.launchFee();
  const supplyWithDecimals = hre.ethers.parseUnits(TOKEN_SUPPLY, TOKEN_DECIMALS);
  const tokenLiquidity = hre.ethers.parseUnits(TOKEN_LIQUIDITY, TOKEN_DECIMALS);
  const usdcLiquidity = hre.ethers.parseUnits(USDC_LIQUIDITY, 6);

  const usdcBalance = await usdc.balanceOf(signer.address);
  if (usdcBalance < usdcLiquidity) {
    throw new Error(`Insufficient USDC for launch. Need ${USDC_LIQUIDITY}`);
  }

  console.log("Creating fresh Joshua...");
  const createTx = await factory.createToken(
    TOKEN_NAME,
    TOKEN_SYMBOL,
    TOKEN_DECIMALS,
    supplyWithDecimals,
    {
      value: launchFee,
      ...(gasPrice ? { gasPrice } : {}),
      nonce: startNonce,
    }
  );
  const receipt = await createTx.wait();
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

  const tokenAddress = event.args.tokenAddress;
  console.log("Token created:", tokenAddress);

  const token = await hre.ethers.getContractAt("MemeToken", tokenAddress, signer);

  const approveTokenTx = await token.approve(deployment.listingManager, tokenLiquidity, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: startNonce + 1,
  });
  await approveTokenTx.wait();
  console.log("Token approved.");

  const approveUsdcTx = await usdc.approve(deployment.listingManager, usdcLiquidity, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: startNonce + 2,
  });
  await approveUsdcTx.wait();
  console.log("USDC approved.");

  const deadline = Math.floor(Date.now() / 1000) + 20 * 60;
  const launchTx = await listingManager.launchToken(
    tokenAddress,
    tokenLiquidity,
    usdcLiquidity,
    (tokenLiquidity * 95n) / 100n,
    (usdcLiquidity * 95n) / 100n,
    deadline,
    {
      ...(gasPrice ? { gasPrice } : {}),
      nonce: startNonce + 3,
    }
  );
  await launchTx.wait();
  console.log("Joshua launched with initial liquidity.");
  console.log(`TOKEN_ADDRESS=${tokenAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
