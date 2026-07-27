const hre = require("hardhat");

const MAREV_ADDRESS = "0x77F7188853DD13D7CE3E9bfDeb070a9544eCf446";
const DEX_ADDRESS = "0x3169b0d384480533d691ad8F0a9A4ed776153627";

async function main() {
  const amountInput = process.env.SWAP_USDC_AMOUNT || "0.01";
  const slippageBps = BigInt(process.env.SLIPPAGE_BPS || "50"); // 0.50%

  const [signer] = await hre.ethers.getSigners();
  const dex = await hre.ethers.getContractAt("MAREVDex", DEX_ADDRESS, signer);
  const marev = await hre.ethers.getContractAt("MAREVToken", MAREV_ADDRESS, signer);

  const amountIn = hre.ethers.parseUnits(amountInput, 6);
  const quoteOut = await dex.getPrice(
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    MAREV_ADDRESS,
    amountIn
  );
  const minOut = (quoteOut * (10000n - slippageBps)) / 10000n;

  console.log("Using signer:", signer.address);
  console.log("Amount in (USDC):", amountInput);
  console.log("Quoted out (MAREV):", hre.ethers.formatEther(quoteOut));
  console.log("Min out (MAREV):", hre.ethers.formatEther(minOut));

  const tx = await dex.swapUSDCtoMAR(amountIn, minOut);
  console.log("Swap tx:", tx.hash);
  await tx.wait();

  const marevBalance = await marev.balanceOf(signer.address);
  console.log("New MAREV balance:", hre.ethers.formatEther(marevBalance));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
