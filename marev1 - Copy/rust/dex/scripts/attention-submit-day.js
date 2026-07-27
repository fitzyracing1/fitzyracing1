const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

function getArg(flag, fallback = null) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

async function main() {
  const network = hre.network.name;
  const deploymentPath = process.env.DEPLOYMENT_PATH || getArg(
    "--deployment",
    path.join(__dirname, `..`, `deployments-attention-${network}.json`)
  );
  const inputPath = process.env.INPUT_PATH || getArg("--input");
  const finalize = (process.env.FINALIZE || getArg("--finalize", "true")) !== "false";

  if (!inputPath) {
    throw new Error("Missing --input <merkle-output-json>");
  }

  const deployment = JSON.parse(fs.readFileSync(path.resolve(deploymentPath), "utf8"));
  const merkleOutput = JSON.parse(fs.readFileSync(path.resolve(inputPath), "utf8"));
  const [deployer] = await hre.ethers.getSigners();

  console.log(`Network: ${network}`);
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Oracle: ${deployment.oracle}`);
  console.log(`Day: ${merkleOutput.day}`);
  console.log(`Root: ${merkleOutput.root}`);

  const oracle = await hre.ethers.getContractAt("AttentionOracle", deployment.oracle);

  const submitTx = await oracle.submitDayRoot(
    merkleOutput.day,
    merkleOutput.root,
    merkleOutput.totalScore,
    merkleOutput.totalAmountWei
  );
  console.log(`submitDayRoot tx: ${submitTx.hash}`);
  await submitTx.wait();
  console.log("Day submitted");

  if (finalize) {
    const finalizeTx = await oracle.finalizeDay(merkleOutput.day);
    console.log(`finalizeDay tx: ${finalizeTx.hash}`);
    await finalizeTx.wait();
    console.log("Day finalized");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
