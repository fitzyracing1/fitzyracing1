const hre = require("hardhat");

const MAREV_ADDRESS = "0x77F7188853DD13D7CE3E9bfDeb070a9544eCf446";
const DEX_ADDRESS = "0x3169b0d384480533d691ad8F0a9A4ed776153627";
const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

const ERC20_ABI = [
  "function approve(address spender, uint256 amount) returns (bool)",
  "function balanceOf(address account) view returns (uint256)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function symbol() view returns (string)",
];

async function main() {
  const marevAmountInput = process.env.MAREV_AMOUNT || "1000";
  const usdcAmountInput = process.env.USDC_AMOUNT || "1000";

  const marevAmount = hre.ethers.parseEther(marevAmountInput);
  const usdcAmount = hre.ethers.parseUnits(usdcAmountInput, 6);

  const [signer] = await hre.ethers.getSigners();
  const nonce = await hre.ethers.provider.getTransactionCount(signer.address, "pending");
  const feeData = await hre.ethers.provider.getFeeData();
  const gasPrice = feeData.gasPrice ? (feeData.gasPrice * 130n) / 100n : null;
  console.log("Using signer:", signer.address);

  const marev = await hre.ethers.getContractAt("MAREVToken", MAREV_ADDRESS, signer);
  const dex = await hre.ethers.getContractAt("MAREVDex", DEX_ADDRESS, signer);
  const usdc = await hre.ethers.getContractAt(ERC20_ABI, USDC_ADDRESS, signer);

  const marevBalance = await marev.balanceOf(signer.address);
  const usdcBalance = await usdc.balanceOf(signer.address);

  console.log("MAREV balance:", hre.ethers.formatEther(marevBalance));
  console.log("USDC balance:", hre.ethers.formatUnits(usdcBalance, 6));

  if (marevBalance < marevAmount) {
    throw new Error(`Insufficient MAREV balance. Need ${marevAmountInput}`);
  }

  if (usdcBalance < usdcAmount) {
    throw new Error(`Insufficient USDC balance. Need ${usdcAmountInput}`);
  }

  console.log("Approving MAREV...");
  const marevApproveTx = await marev.approve(DEX_ADDRESS, marevAmount, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce,
  });
  await marevApproveTx.wait();

  console.log("Approving USDC...");
  const usdcApproveTx = await usdc.approve(DEX_ADDRESS, usdcAmount, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: nonce + 1,
  });
  await usdcApproveTx.wait();

  console.log("Adding liquidity...");
  const addLiquidityTx = await dex.addLiquidity(marevAmount, usdcAmount, {
    ...(gasPrice ? { gasPrice } : {}),
    nonce: nonce + 2,
  });
  await addLiquidityTx.wait();

  const [marevReserve, usdcReserve] = await dex.getReserves();
  const marevAllowance = await marev.allowance(signer.address, DEX_ADDRESS);
  const usdcAllowance = await usdc.allowance(signer.address, DEX_ADDRESS);

  console.log("Liquidity added successfully.");
  console.log("New MAREV reserve:", hre.ethers.formatEther(marevReserve));
  console.log("New USDC reserve:", hre.ethers.formatUnits(usdcReserve, 6));
  console.log("Remaining MAREV allowance:", hre.ethers.formatEther(marevAllowance));
  console.log("Remaining USDC allowance:", hre.ethers.formatUnits(usdcAllowance, 6));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
