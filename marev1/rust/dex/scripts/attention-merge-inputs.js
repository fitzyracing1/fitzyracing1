const fs = require("fs");
const path = require("path");

function getArg(flag, fallback = null) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function main() {
  const outputPath = getArg("--output");
  const inputs = [];

  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i] === "--input" && process.argv[i + 1]) {
      inputs.push(process.argv[i + 1]);
    }
  }

  if (!outputPath || inputs.length === 0) {
    throw new Error("Usage: node scripts/attention-merge-inputs.js --input <FILE> [--input <FILE>...] --output <FILE>");
  }

  const merged = new Map();

  for (const input of inputs) {
    const rows = JSON.parse(fs.readFileSync(path.resolve(input), "utf8"));
    for (const row of rows) {
      const wallet = row.wallet;
      const current = merged.get(wallet) || { wallet, score: 0n, amountWei: 0n, sources: [] };
      current.score += BigInt(row.score);
      current.amountWei += BigInt(row.amountWei);
      current.sources.push({
        source: row.source || path.basename(input),
        createdTokens: row.createdTokens || [],
        listedTokens: row.listedTokens || [],
      });
      merged.set(wallet, current);
    }
  }

  const output = Array.from(merged.values())
    .filter((row) => row.score > 0n && row.amountWei > 0n)
    .sort((a, b) => a.wallet.localeCompare(b.wallet))
    .map((row) => ({
      wallet: row.wallet,
      score: row.score.toString(),
      amountWei: row.amountWei.toString(),
      sources: row.sources,
    }));

  fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
  fs.writeFileSync(path.resolve(outputPath), `${JSON.stringify(output, null, 2)}\n`);
  console.log(`Merged wallets: ${output.length}`);
  console.log(`Output: ${path.resolve(outputPath)}`);
}

main();
