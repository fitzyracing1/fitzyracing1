import { Token } from "@uniswap/sdk-core";
import { base } from "viem/chains";

export const WETH = new Token(
  base.id,
  "0x4200000000000000000000000000000000000006",
  18,
  "WETH",
  "Wrapped Ether"
);

export const USDC = new Token(
  base.id,
  "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  6,
  "USDC",
  "USD Coin"
);

export const TOKENS = { WETH, USDC } as const;
export type TokenSymbol = keyof typeof TOKENS;

// Uniswap v3 on Base
export const UNISWAP_V3_QUOTER_V2 =
  "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a" as const;
export const UNISWAP_V3_SWAP_ROUTER_02 =
  "0x2626664c2603336E57B271c5C0b26F421741e481" as const;
export const DEFAULT_FEE = 500; // 0.05%
