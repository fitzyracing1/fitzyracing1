"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { formatEther } from "viem";
import type { Listing, ListingType, Merchant } from "@/lib/merchant-store";

const TYPE_LABEL: Record<ListingType, string> = {
  digital_link: "Digital",
  physical_good: "Physical",
  service: "Service",
};

export default function SellPage() {
  const { address, isConnected } = useAccount();
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!address) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/merchants/${address}`);
      if (res.status === 404) {
        setMerchant(null);
        setListings([]);
      } else if (res.ok) {
        const json = await res.json();
        setMerchant(json.merchant);
        setListings(json.listings);
      } else {
        setErr(`HTTP ${res.status}`);
      }
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [address]);

  useEffect(() => {
    if (isConnected) refresh();
  }, [isConnected, refresh]);

  if (!isConnected) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6 text-center">
        <h1 className="text-2xl font-bold">Connect to sell</h1>
        <p className="text-white/60 max-w-sm">
          Your wallet is your storefront. Buyers send ETH directly to you.
        </p>
        <ConnectButton />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-white/60">
        Loading…
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col items-center pt-6 pb-12 px-4">
      <div className="w-full max-w-md space-y-4">
        {err && <div className="text-xs text-red-400">{err}</div>}
        {merchant ? (
          <Dashboard
            merchant={merchant}
            listings={listings}
            onCreated={refresh}
          />
        ) : (
          <RegisterForm address={address!} onDone={refresh} />
        )}
      </div>
    </div>
  );
}

function RegisterForm({
  address,
  onDone,
}: {
  address: string;
  onDone: () => void;
}) {
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch("/api/merchants", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ address, name, bio }),
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(json.error ?? `HTTP ${res.status}`);
      onDone();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-2xl bg-white/5 border border-white/10 p-4 space-y-3"
    >
      <h2 className="text-lg font-bold">Open your jelly shop</h2>
      <label className="block">
        <span className="text-xs text-white/60">Display name</span>
        <input
          value={name}
          onChange={(e) => setName(e.target.value.slice(0, 60))}
          placeholder="Carrot Coach"
          className="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30"
        />
      </label>
      <label className="block">
        <span className="text-xs text-white/60">Bio</span>
        <textarea
          value={bio}
          onChange={(e) => setBio(e.target.value.slice(0, 500))}
          rows={3}
          placeholder="What you sell, in one paragraph."
          className="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30 resize-none"
        />
      </label>
      {err && <div className="text-xs text-red-400">{err}</div>}
      <button
        type="submit"
        disabled={busy || !name.trim()}
        className="w-full py-3 rounded-xl bg-[#ff2d87] text-black font-semibold disabled:opacity-50"
      >
        {busy ? "Creating…" : "Create shop"}
      </button>
    </form>
  );
}

function Dashboard({
  merchant,
  listings,
  onCreated,
}: {
  merchant: Merchant;
  listings: Listing[];
  onCreated: () => void;
}) {
  return (
    <>
      <div className="rounded-2xl bg-white/5 border border-white/10 p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="text-lg font-bold truncate">{merchant.name}</div>
            {merchant.bio && (
              <p className="text-sm text-white/70 mt-1">{merchant.bio}</p>
            )}
          </div>
          <Link
            href={`/creator/${merchant.address}`}
            className="text-xs px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/20 shrink-0"
          >
            View shop
          </Link>
        </div>
      </div>

      <NewListingForm merchant={merchant.address} onCreated={onCreated} />

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-white/80">
          Your listings ({listings.length})
        </h3>
        {listings.length === 0 ? (
          <div className="text-sm text-white/50 rounded-xl bg-white/5 p-4 text-center">
            No listings yet.
          </div>
        ) : (
          listings.map((l) => (
            <Link
              key={l.id}
              href={`/listing/${l.id}`}
              className="block rounded-xl bg-white/5 border border-white/10 p-3 hover:bg-white/10"
            >
              <div className="flex items-baseline justify-between gap-2">
                <div className="font-semibold truncate">{l.title}</div>
                <div className="text-sm font-mono text-[#ff2d87] shrink-0">
                  {formatEther(BigInt(l.priceWei))} ETH
                </div>
              </div>
              <div className="text-[10px] uppercase tracking-wide text-white/50 mt-0.5">
                {TYPE_LABEL[l.type]}
              </div>
            </Link>
          ))
        )}
      </div>
    </>
  );
}

function NewListingForm({
  merchant,
  onCreated,
}: {
  merchant: string;
  onCreated: () => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priceEth, setPriceEth] = useState("");
  const [type, setType] = useState<ListingType>("digital_link");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch("/api/listings", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ merchant, title, description, priceEth, type }),
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(json.error ?? `HTTP ${res.status}`);
      setTitle("");
      setDescription("");
      setPriceEth("");
      setType("digital_link");
      onCreated();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-2xl bg-white/5 border border-white/10 p-4 space-y-3"
    >
      <h3 className="text-sm font-semibold">New listing</h3>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value.slice(0, 120))}
        placeholder="Title"
        className="w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30"
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value.slice(0, 1000))}
        rows={3}
        placeholder="Description"
        className="w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30 resize-none"
      />
      <div className="flex gap-2">
        <input
          value={priceEth}
          onChange={(e) =>
            setPriceEth(e.target.value.replace(/[^0-9.]/g, ""))
          }
          inputMode="decimal"
          placeholder="0.001"
          className="flex-1 rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30"
        />
        <span className="text-sm text-white/60 self-center">ETH</span>
        <select
          value={type}
          onChange={(e) => setType(e.target.value as ListingType)}
          className="rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30"
        >
          <option value="digital_link" className="bg-black">
            Digital
          </option>
          <option value="physical_good" className="bg-black">
            Physical
          </option>
          <option value="service" className="bg-black">
            Service
          </option>
        </select>
      </div>
      {err && <div className="text-xs text-red-400">{err}</div>}
      <button
        type="submit"
        disabled={busy || !title.trim() || !priceEth}
        className="w-full py-2.5 rounded-xl bg-[#ff2d87] text-black font-semibold disabled:opacity-50"
      >
        {busy ? "Posting…" : "Post listing"}
      </button>
    </form>
  );
}
