const hre = require("hardhat");

const TOKEN_ADDRESS = process.env.TOKEN_ADDRESS || "0xDD0C7e78229672Af3103d4771238ab3A384c5083";
const LISTING_MANAGER = process.env.LISTING_MANAGER || "0x4B99195d925B46Ec8e5620659657407cdD9698D2";
const TOKEN_LIQUIDITY = process.env.TOKEN_LIQUIDITY || "50";
const USDC_LIQUIDITY = process.env.USDC_LIQUIDITY || "0.05";

async function main() {
  const [signer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(signer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;

  const listingManager = await hre.ethers.getContractAt("StandardDexLiquidityManager", LISTING_MANAGER, signer);
  const tokenLiquidity = hre.ethers.parseUnits(TOKEN_LIQUIDITY, 18);
  const usdcLiquidity = hre.ethers.parseUnits(USDC_LIQUIDITY, 6);
  const deadline = Math.floor(Date.now() / 1000) + 20 * 60;

  const tx = await listingManager.launchToken(
    TOKEN_ADDRESS,
    tokenLiquidity,
    usdcLiquidity,
    (tokenLiquidity * 95n) / 100n,
    (usdcLiquidity * 95n) / 100n,
    deadline,
    {
      ...(gasPrice ? { gasPrice } : {}),
      nonce,
    }
  );
  console.log("Launch tx:", tx.hash);
  await tx.wait();
  console.log("Token launched.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
