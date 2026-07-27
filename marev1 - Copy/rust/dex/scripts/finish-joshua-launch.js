const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const TOKEN_ADDRESS = process.env.TOKEN_ADDRESS || "0xDD0C7e78229672Af3103d4771238ab3A384c5083";
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

  const listingManager = await hre.ethers.getContractAt("StandardDexLiquidityManager", deployment.listingManager, signer);
  const token = await hre.ethers.getContractAt("MemeToken", TOKEN_ADDRESS, signer);
  const usdc = await hre.ethers.getContractAt([
    "function balanceOf(address account) view returns (uint256)",
    "function approve(address spender, uint256 amount) returns (bool)",
  ], BASE_TOKEN, signer);

  const tokenLiquidity = hre.ethers.parseUnits(TOKEN_LIQUIDITY, 18);
  const usdcLiquidity = hre.ethers.parseUnits(USDC_LIQUIDITY, 6);
  const usdcBalance = await usdc.balanceOf(signer.address);
  if (usdcBalance < usdcLiquidity) {
    throw new Error(`Insufficient USDC for launch. Need ${USDC_LIQUIDITY}`);
  }

  const approveTokenTx = await token.approve(deployment.listingManager, tokenLiquidity, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: startNonce,
  });
  await approveTokenTx.wait();
  console.log("Token approved.");

  const approveUsdcTx = await usdc.approve(deployment.listingManager, usdcLiquidity, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: startNonce + 1,
  });
  await approveUsdcTx.wait();
  console.log("USDC approved.");

  const deadline = Math.floor(Date.now() / 1000) + 20 * 60;
  const launchTx = await listingManager.launchToken(
    TOKEN_ADDRESS,
    tokenLiquidity,
    usdcLiquidity,
    (tokenLiquidity * 95n) / 100n,
    (usdcLiquidity * 95n) / 100n,
    deadline,
    {
      ...(gasPrice ? { gasPrice } : {}),
      nonce: startNonce + 2,
    }
  );
  await launchTx.wait();
  console.log("Joshua launched with initial liquidity.");
  console.log(`TOKEN_ADDRESS=${TOKEN_ADDRESS}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
