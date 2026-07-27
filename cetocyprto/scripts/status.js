const hre = require("hardhat");

async function main() {
  const [caller] = await hre.ethers.getSigners();
  const Token = await hre.ethers.getContractFactory("CetoToken");

  let token;
  if (process.env.TOKEN_ADDRESS) {
    token = await Token.attach(process.env.TOKEN_ADDRESS);
    console.log("Using existing token at", token.target);
  } else {
    const initialSupply = hre.ethers.parseUnits("1000000", 18);
    token = await Token.deploy(initialSupply, caller.address);
    await token.waitForDeployment();
    console.log("Deployed temporary token to", token.target);
  }

  const totalSupply = await token.totalSupply();
  const remaining = await token.remainingCapacity();
  const limit = await token.rollingLimit();

  console.log("Caller:", caller.address);
  console.log("Total supply:", totalSupply.toString());
  console.log("Rolling limit:", limit.toString());
  console.log("Remaining capacity this window:", remaining.toString());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
