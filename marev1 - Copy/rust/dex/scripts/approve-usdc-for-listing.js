const hre = require("hardhat");

const LISTING_MANAGER = process.env.LISTING_MANAGER || "0x4B99195d925B46Ec8e5620659657407cdD9698D2";
const BASE_TOKEN = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const USDC_LIQUIDITY = process.env.USDC_LIQUIDITY || "0.05";

async function main() {
  const [signer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(signer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const usdc = await hre.ethers.getContractAt([
    "function approve(address spender, uint256 amount) returns (bool)",
  ], BASE_TOKEN, signer);

  const usdcLiquidity = hre.ethers.parseUnits(USDC_LIQUIDITY, 6);
  const tx = await usdc.approve(LISTING_MANAGER, usdcLiquidity, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce,
  });
  console.log("USDC approval tx:", tx.hash);
  await tx.wait();
  console.log("USDC approved.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
