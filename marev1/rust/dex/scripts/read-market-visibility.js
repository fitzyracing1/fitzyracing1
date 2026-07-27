const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

const ERC20_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
];

const PAIR_ABI = [
  "function token0() view returns (address)",
  "function token1() view returns (address)",
  "function getReserves() view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)",
];

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.resolve(file), "utf8"));
}

async function main() {
  const dexDeployment = readJson(path.join(__dirname, "..", "deployments-base.json"));
  const factoryDeployment = readJson(path.join(__dirname, "..", "deployments-factory-base.json"));

  const dex = await hre.ethers.getContractAt([
    "function getReserves() view returns (uint256 marevReserve, uint256 usdcReserve)"
  ], dexDeployment.dex);

  const factory = await hre.ethers.getContractAt([
    "function getTotalTokens() view returns (uint256)",
    "function allTokens(uint256) view returns (address)",
    "function getTokenInfo(address) view returns (string,string,address,uint256,uint256,bool)",
    "function getListingInfo(address) view returns (bool,address,address)"
  ], factoryDeployment.factory);

  const [marevToken, latestIndex, reserves] = await Promise.all([
    hre.ethers.getContractAt(ERC20_ABI, dexDeployment.marevToken),
    factory.getTotalTokens(),
    dex.getReserves(),
  ]);

  const totalTokens = Number(latestIndex);
  const latestTokenAddress = totalTokens > 0 ? await factory.allTokens(totalTokens - 1) : null;

  let latestToken = null;
  if (latestTokenAddress) {
    const [info, listing, tokenContract] = await Promise.all([
      factory.getTokenInfo(latestTokenAddress),
      factory.getListingInfo(latestTokenAddress),
      hre.ethers.getContractAt(ERC20_ABI, latestTokenAddress),
    ]);
    const [name, symbol, decimals, supply] = await Promise.all([
      tokenContract.name(),
      tokenContract.symbol(),
      tokenContract.decimals(),
      tokenContract.totalSupply(),
    ]);

    let pairSummary = null;
    if (listing[0] && listing[2] && listing[2] !== hre.ethers.ZeroAddress) {
      const pair = await hre.ethers.getContractAt(PAIR_ABI, listing[2]);
      const [token0, pairReserves] = await Promise.all([
        pair.token0(),
        pair.getReserves(),
      ]);
      const tokenIs0 = token0.toLowerCase() === latestTokenAddress.toLowerCase();
      pairSummary = {
        pairAddress: listing[2],
        tokenReserve: hre.ethers.formatUnits(tokenIs0 ? pairReserves[0] : pairReserves[1], decimals),
        usdcReserve: hre.ethers.formatUnits(tokenIs0 ? pairReserves[1] : pairReserves[0], 6),
      };
    }

    latestToken = {
      address: latestTokenAddress,
      name,
      symbol,
      decimals: Number(decimals),
      totalSupply: hre.ethers.formatUnits(supply, decimals),
      creator: info[2],
      isListed: listing[0],
      pair: pairSummary,
    };
  }

  console.log(JSON.stringify({
    marev: {
      address: dexDeployment.marevToken,
      name: await marevToken.name(),
      symbol: await marevToken.symbol(),
      totalSupply: hre.ethers.formatUnits(await marevToken.totalSupply(), 18),
      dexReserves: {
        marev: hre.ethers.formatUnits(reserves[0], 18),
        usdc: hre.ethers.formatUnits(reserves[1], 6),
      },
    },
    latestFactoryToken: latestToken,
  }, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
