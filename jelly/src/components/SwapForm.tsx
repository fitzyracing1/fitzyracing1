"use client";

import { useEffect, useMemo, useState } from "react";
import {
  useAccount,
  useChainId,
  usePublicClient,
  useReadContract,
  useSwitchChain,
  useWriteContract,
} from "wagmi";
import { base } from "wagmi/chains";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { formatUnits, parseUnits, maxUint256 } from "viem";
import {
  TOKENS,
  type TokenSymbol,
  UNISWAP_V3_QUOTER_V2,
  UNISWAP_V3_SWAP_ROUTER_02,
  DEFAULT_FEE,
} from "@/lib/tokens";
import { quoterV2Abi, swapRouter02Abi, erc20Abi } from "@/lib/abis";

type Props = { presetOut?: TokenSymbol };

export function SwapForm({ presetOut }: Props) {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();
  const publicClient = usePublicClient({ chainId: base.id });
  const { writeContractAsync, isPending } = useWriteContract();

  const [tokenInSym, setTokenInSym] = useState<TokenSymbol>("WETH");
  const [tokenOutSym, setTokenOutSym] = useState<TokenSymbol>(
    presetOut && presetOut in TOKENS ? presetOut : "USDC"
  );
  const [amountIn, setAmountIn] = useState("");
  const [quote, setQuote] = useState<bigint | null>(null);
  const [quoting, setQuoting] = useState(false);
  const [txHash, setTxHash] = useState<`0x${string}` | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const tokenIn = TOKENS[tokenInSym];
  const tokenOut = TOKENS[tokenOutSym];

  const parsedAmountIn = useMemo(() => {
    if (!amountIn || isNaN(Number(amountIn))) return 0n;
    try {
      return parseUnits(amountIn, tokenIn.decimals);
    } catch {
      return 0n;
    }
  }, [amountIn, tokenIn.decimals]);

  const allowance = useReadContract({
    abi: erc20Abi,
    address: tokenIn.address as `0x${string}`,
    functionName: "allowance",
    args:
      address && parsedAmountIn > 0n
        ? [address, UNISWAP_V3_SWAP_ROUTER_02]
        : undefined,
    chainId: base.id,
    query: { enabled: !!address && parsedAmountIn > 0n },
  });

  const needsApproval =
    parsedAmountIn > 0n &&
    typeof allowance.data === "bigint" &&
    allowance.data < parsedAmountIn;

  useEffect(() => {
    if (parsedAmountIn === 0n || !publicClient) {
      setQuote(null);
      return;
    }
    let cancelled = false;
    setQuoting(true);
    setErr(null);
    publicClient
      .simulateContract({
        address: UNISWAP_V3_QUOTER_V2,
        abi: quoterV2Abi,
        functionName: "quoteExactInputSingle",
        args: [
          {
            tokenIn: tokenIn.address as `0x${string}`,
            tokenOut: tokenOut.address as `0x${string}`,
            amountIn: parsedAmountIn,
            fee: DEFAULT_FEE,
            sqrtPriceLimitX96: 0n,
          },
        ],
      })
      .then((res) => {
        if (!cancelled) setQuote(res.result[0] as bigint);
      })
      .catch((e) => {
        if (!cancelled) {
          setQuote(null);
          setErr(`No pool / quote failed: ${(e as Error).message.slice(0, 80)}`);
        }
      })
      .finally(() => {
        if (!cancelled) setQuoting(false);
      });
    return () => {
      cancelled = true;
    };
  }, [parsedAmountIn, tokenIn.address, tokenOut.address, publicClient]);

  const formattedQuote =
    quote != null
      ? formatUnits(quote, tokenOut.decimals)
      : null;

  async function handleApprove() {
    setErr(null);
    try {
      const hash = await writeContractAsync({
        abi: erc20Abi,
        address: tokenIn.address as `0x${string}`,
        functionName: "approve",
        args: [UNISWAP_V3_SWAP_ROUTER_02, maxUint256],
      });
      setTxHash(hash);
      await allowance.refetch();
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  async function handleSwap() {
    if (!address || quote == null) return;
    setErr(null);
    const minOut = (quote * 99n) / 100n; // 1% slippage
    try {
      const hash = await writeContractAsync({
        abi: swapRouter02Abi,
        address: UNISWAP_V3_SWAP_ROUTER_02,
        functionName: "exactInputSingle",
        args: [
          {
            tokenIn: tokenIn.address as `0x${string}`,
            tokenOut: tokenOut.address as `0x${string}`,
            fee: DEFAULT_FEE,
            recipient: address,
            amountIn: parsedAmountIn,
            amountOutMinimum: minOut,
            sqrtPriceLimitX96: 0n,
          },
        ],
      });
      setTxHash(hash);
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  function flip() {
    setTokenInSym(tokenOutSym);
    setTokenOutSym(tokenInSym);
    setAmountIn("");
    setQuote(null);
  }

  const wrongChain = isConnected && chainId !== base.id;

  return (
    <div className="w-full max-w-md mx-auto p-4">
      <div className="rounded-2xl bg-white/5 border border-white/10 p-4 space-y-3">
        <h2 className="text-lg font-bold">Swap</h2>

        <div className="rounded-xl bg-white/5 p-3">
          <div className="text-xs text-white/60 mb-1">You pay</div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              inputMode="decimal"
              value={amountIn}
              onChange={(e) =>
                setAmountIn(e.target.value.replace(/[^0-9.]/g, ""))
              }
              placeholder="0.0"
              className="flex-1 bg-transparent text-2xl outline-none"
            />
            <TokenSelector value={tokenInSym} onChange={setTokenInSym} />
          </div>
        </div>

        <div className="flex justify-center">
          <button
            onClick={flip}
            aria-label="Flip"
            className="h-9 w-9 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center"
          >
            ↓
          </button>
        </div>

        <div className="rounded-xl bg-white/5 p-3">
          <div className="text-xs text-white/60 mb-1">You receive</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 text-2xl text-white/80">
              {quoting
                ? "…"
                : formattedQuote
                ? Number(formattedQuote).toLocaleString(undefined, {
                    maximumFractionDigits: 6,
                  })
                : "0.0"}
            </div>
            <TokenSelector value={tokenOutSym} onChange={setTokenOutSym} />
          </div>
        </div>

        {err && (
          <div className="text-xs text-red-400 break-all">{err}</div>
        )}

        {!isConnected ? (
          <div className="flex justify-center">
            <ConnectButton />
          </div>
        ) : wrongChain ? (
          <button
            onClick={() => switchChain({ chainId: base.id })}
            className="w-full py-3 rounded-xl bg-yellow-500 text-black font-semibold"
          >
            Switch to Base
          </button>
        ) : needsApproval ? (
          <button
            onClick={handleApprove}
            disabled={isPending}
            className="w-full py-3 rounded-xl bg-[#ff2d87] text-black font-semibold disabled:opacity-50"
          >
            {isPending ? "Approving…" : `Approve ${tokenInSym}`}
          </button>
        ) : (
          <button
            onClick={handleSwap}
            disabled={
              isPending || quote == null || parsedAmountIn === 0n
            }
            className="w-full py-3 rounded-xl bg-[#ff2d87] text-black font-semibold disabled:opacity-50"
          >
            {isPending
              ? "Swapping…"
              : parsedAmountIn === 0n
              ? "Enter amount"
              : quote == null
              ? "No quote"
              : "Swap"}
          </button>
        )}

        {txHash && (
          <a
            href={`https://basescan.org/tx/${txHash}`}
            target="_blank"
            rel="noreferrer"
            className="block text-xs text-center text-white/70 underline"
          >
            View tx ↗
          </a>
        )}

        <div className="text-[10px] text-white/40 text-center pt-1">
          Uniswap v3 · Base · 0.05% fee tier · 1% slippage
        </div>
      </div>
    </div>
  );
}

function TokenSelector({
  value,
  onChange,
}: {
  value: TokenSymbol;
  onChange: (s: TokenSymbol) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as TokenSymbol)}
      className="bg-white/10 hover:bg-white/15 rounded-full px-3 py-1.5 text-sm font-semibold appearance-none cursor-pointer"
    >
      {(Object.keys(TOKENS) as TokenSymbol[]).map((sym) => (
        <option key={sym} value={sym} className="bg-black">
          {sym}
        </option>
      ))}
    </select>
  );
}
