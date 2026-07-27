const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");

function getArg(flag, fallback = null) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function normalizeAddress(address) {
  return ethers.getAddress(address);
}

function leafHash(day, wallet, score, amount) {
  const coder = ethers.AbiCoder.defaultAbiCoder();
  return ethers.keccak256(
    coder.encode(["uint256", "address", "uint256", "uint256"], [day, wallet, score, amount])
  );
}

function hashPair(a, b) {
  return a.toLowerCase() < b.toLowerCase()
    ? ethers.keccak256(ethers.concat([a, b]))
    : ethers.keccak256(ethers.concat([b, a]));
}

function buildLayers(leaves) {
  const layers = [leaves.slice()];
  while (layers[layers.length - 1].length > 1) {
    const prev = layers[layers.length - 1];
    const next = [];
    for (let i = 0; i < prev.length; i += 2) {
      const left = prev[i];
      const right = i + 1 < prev.length ? prev[i + 1] : prev[i];
      next.push(hashPair(left, right));
    }
    layers.push(next);
  }
  return layers;
}

function buildProof(index, layers) {
  const proof = [];
  let idx = index;
  for (let layer = 0; layer < layers.length - 1; layer++) {
    const nodes = layers[layer];
    const pairIndex = idx ^ 1;
    if (pairIndex < nodes.length) {
      proof.push(nodes[pairIndex]);
    } else {
      proof.push(nodes[idx]);
    }
    idx = Math.floor(idx / 2);
  }
  return proof;
}

function main() {
  const dayRaw = getArg("--day");
  const inputPathRaw = getArg("--input");
  const outputPathRaw = getArg("--output", "./data/attention-merkle-output.json");

  if (!dayRaw || !inputPathRaw) {
    console.error("Usage: node scripts/attention-build-merkle.js --day <DAY> --input <INPUT_JSON> [--output <OUTPUT_JSON>]");
    process.exit(1);
  }

  const day = BigInt(dayRaw);
  const inputPath = path.resolve(inputPathRaw);
  const outputPath = path.resolve(outputPathRaw);

  const records = JSON.parse(fs.readFileSync(inputPath, "utf8"));
  if (!Array.isArray(records) || records.length === 0) {
    throw new Error("Input must be a non-empty JSON array");
  }

  const claims = records.map((r) => {
    const wallet = normalizeAddress(r.wallet);
    const score = BigInt(r.score);
    const amount = BigInt(r.amountWei);
    if (score <= 0n || amount <= 0n) {
      throw new Error(`Invalid score/amount for ${wallet}`);
    }
    const leaf = leafHash(day, wallet, score, amount);
    return { wallet, score, amount, leaf };
  });

  claims.sort((a, b) => a.leaf.toLowerCase().localeCompare(b.leaf.toLowerCase()));
  const leaves = claims.map((c) => c.leaf);
  const layers = buildLayers(leaves);
  const root = layers[layers.length - 1][0];

  const totalScore = claims.reduce((acc, c) => acc + c.score, 0n);
  const totalAmount = claims.reduce((acc, c) => acc + c.amount, 0n);

  const outputClaims = {};
  claims.forEach((claim, index) => {
    outputClaims[claim.wallet] = {
      score: claim.score.toString(),
      amountWei: claim.amount.toString(),
      leaf: claim.leaf,
      proof: buildProof(index, layers),
    };
  });

  const output = {
    day: day.toString(),
    root,
    totalScore: totalScore.toString(),
    totalAmountWei: totalAmount.toString(),
    claims: outputClaims,
  };

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`Merkle root: ${root}`);
  console.log(`Claims: ${claims.length}`);
  console.log(`Output: ${outputPath}`);
}

main();
