const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const attentionPath = path.join(__dirname, "..", "deployments-attention-base.json");
  const attention = JSON.parse(fs.readFileSync(attentionPath, "utf8"));
  const [signer] = await hre.ethers.getSigners();
  const token = await hre.ethers.getContractAt("AttentionToken", attention.token);

  console.log(JSON.stringify({
    account: signer.address,
    balanceWei: (await token.balanceOf(signer.address)).toString(),
    balanceFormatted: hre.ethers.formatEther(await token.balanceOf(signer.address)),
    totalSupplyWei: (await token.totalSupply()).toString(),
    totalSupplyFormatted: hre.ethers.formatEther(await token.totalSupply()),
  }, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
