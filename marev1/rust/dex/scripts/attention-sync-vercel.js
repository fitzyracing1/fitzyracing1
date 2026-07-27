const fs = require("fs");
const path = require("path");

const ROOT_DIR = path.join(__dirname, "..", "..");
const DEX_DIR = path.join(ROOT_DIR, "dex");
const DATA_DIR = path.join(DEX_DIR, "data");
const VERCEL_DIR = path.join(ROOT_DIR, "vercel");
const DEPLOYMENT_FILE = path.join(DEX_DIR, "deployments-attention-base.json");
const OUTPUT_FILE = path.join(VERCEL_DIR, "attention-claims.json");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function getDayOutputFiles() {
  if (!fs.existsSync(DATA_DIR)) return [];

  return fs.readdirSync(DATA_DIR)
    .filter((name) => /^day-\d+-output\.json$/i.test(name))
    .sort((a, b) => {
      const dayA = Number(a.match(/^day-(\d+)-output\.json$/i)[1]);
      const dayB = Number(b.match(/^day-(\d+)-output\.json$/i)[1]);
      return dayA - dayB;
    });
}

function main() {
  if (!fs.existsSync(DEPLOYMENT_FILE)) {
    throw new Error(`Missing deployment file: ${DEPLOYMENT_FILE}`);
  }

  const deployment = readJson(DEPLOYMENT_FILE);
  const dayFiles = getDayOutputFiles();

  const days = dayFiles.map((filename) => {
    const fullPath = path.join(DATA_DIR, filename);
    return readJson(fullPath);
  });

  const payload = {
    generatedAt: new Date().toISOString(),
    network: deployment.network,
    chainId: String(deployment.chainId),
    distributor: deployment.distributor,
    oracle: deployment.oracle,
    token: deployment.token,
    days,
  };

  fs.writeFileSync(OUTPUT_FILE, `${JSON.stringify(payload, null, 2)}\n`);

  console.log(`Wrote ${OUTPUT_FILE}`);
  console.log(`Distributor: ${payload.distributor}`);
  console.log(`Days synced: ${days.length}`);
}

main();
