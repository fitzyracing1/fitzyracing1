"use client";

import { useState } from "react";
import {
  useAccount,
  useChainId,
  useSendTransaction,
  useSwitchChain,
  useWaitForTransactionReceipt,
} from "wagmi";
import { base } from "wagmi/chains";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { formatEther } from "viem";
import type { Listing, ListingType } from "@/lib/merchant-store";

type Props = {
  listing: Listing;
  merchantName: string;
};

const TYPE_LABEL: Record<ListingType, string> = {
  digital_link: "Digital",
  physical_good: "Physical",
  service: "Service",
};

const POST_PURCHASE_HINT: Record<ListingType, string> = {
  digital_link:
    "The seller will send your access link to the wallet that paid (off-chain, e.g. Lens or XMTP).",
  physical_good:
    "Reply to the seller with your shipping address. Use a private channel — your address shouldn't sit on-chain.",
  service:
    "The seller will reach out to schedule. Watch for a message from their wallet.",
};

export function ListingBuy({ listing, merchantName }: Props) {
  const { isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();
  const {
    sendTransactionAsync,
    isPending: sending,
    data: hash,
  } = useSendTransaction();
  const { isLoading: confirming, isSuccess: confirmed } =
    useWaitForTransactionReceipt({ hash });

  const [err, setErr] = useState<string | null>(null);
  const wrongChain = isConnected && chainId !== base.id;

  async function buy() {
    setErr(null);
    try {
      await sendTransactionAsync({
        to: listing.merchant as `0x${string}`,
        value: BigInt(listing.priceWei),
        chainId: base.id,
      });
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  if (confirmed && hash) {
    return (
      <div className="rounded-xl bg-emerald-500/10 border border-emerald-400/30 p-4 space-y-2">
        <div className="font-semibold text-emerald-300">Payment confirmed</div>
        <p className="text-sm text-white/80">
          {formatEther(BigInt(listing.priceWei))} ETH sent to {merchantName}.
        </p>
        <p className="text-xs text-white/70">
          {POST_PURCHASE_HINT[listing.type]}
        </p>
        <a
          href={`https://basescan.org/tx/${hash}`}
          target="_blank"
          rel="noreferrer"
          className="text-xs underline text-white/70"
        >
          View tx ↗
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="text-[10px] uppercase tracking-wide text-white/50">
        {TYPE_LABEL[listing.type]}
      </div>
      <div className="text-2xl font-mono text-[#ff2d87]">
        {formatEther(BigInt(listing.priceWei))} ETH
      </div>

      {!isConnected ? (
        <ConnectButton />
      ) : wrongChain ? (
        <button
          onClick={() => switchChain({ chainId: base.id })}
          className="w-full py-3 rounded-xl bg-yellow-500 text-black font-semibold"
        >
          Switch to Base
        </button>
      ) : (
        <button
          onClick={buy}
          disabled={sending || confirming}
          className="w-full py-3 rounded-xl bg-[#ff2d87] text-black font-semibold disabled:opacity-50"
        >
          {sending
            ? "Confirming in wallet…"
            : confirming
            ? "Waiting for tx…"
            : `Pay ${formatEther(BigInt(listing.priceWei))} ETH`}
        </button>
      )}

      {hash && !confirmed && (
        <a
          href={`https://basescan.org/tx/${hash}`}
          target="_blank"
          rel="noreferrer"
          className="block text-xs text-center underline text-white/70"
        >
          Pending… view on Basescan ↗
        </a>
      )}

      {err && <div className="text-xs text-red-400 break-all">{err}</div>}

      <div className="text-[10px] text-white/40 text-center">
        ETH goes directly to the seller's wallet on Base. Non-refundable.
      </div>
    </div>
  );
}
