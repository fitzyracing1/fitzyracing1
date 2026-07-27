"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { formatEther } from "viem";
import type { Listing } from "@/lib/merchant-store";

const MAX_MB = 50;

export default function UploadPage() {
  const { address, isConnected } = useAccount();
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [caption, setCaption] = useState("");
  const [unlockToken, setUnlockToken] = useState("");
  const [unlockPrice, setUnlockPrice] = useState("");
  const [listingId, setListingId] = useState("");
  const [myListings, setMyListings] = useState<Listing[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!address) {
      setMyListings([]);
      return;
    }
    fetch(`/api/merchants/${address}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => setMyListings(j?.listings ?? []))
      .catch(() => setMyListings([]));
  }, [address]);

  function pick(f: File | null) {
    setErr(null);
    if (!f) {
      setFile(null);
      setPreviewUrl(null);
      return;
    }
    if (!f.type.startsWith("video/")) {
      setErr("Pick a video file.");
      return;
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      setErr(`File over ${MAX_MB}MB.`);
      return;
    }
    setFile(f);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(f));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !address) return;
    if (unlockToken && !unlockPrice) {
      setErr("Set a price (in ETH) for your unlock token, or clear the token.");
      return;
    }

    setSubmitting(true);
    setErr(null);
    try {
      const fd = new FormData();
      fd.append("video", file);
      fd.append("creator", address);
      fd.append("caption", caption);
      if (listingId) fd.append("listingId", listingId);
      if (unlockToken) fd.append("unlockToken", unlockToken);
      if (unlockPrice) fd.append("unlockPrice", unlockPrice);

      const res = await fetch("/api/upload", { method: "POST", body: fd });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(json.error ?? `HTTP ${res.status}`);

      router.push("/feed");
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!isConnected) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6 text-center">
        <h1 className="text-2xl font-bold">Connect to upload</h1>
        <p className="text-white/60 max-w-sm">
          Your wallet address is the creator handle on jelly.
        </p>
        <ConnectButton />
      </div>
    );
  }

  return (
    <div className="flex-1 flex justify-center pt-6 pb-12 px-4">
      <form
        onSubmit={submit}
        className="w-full max-w-md rounded-2xl bg-white/5 border border-white/10 p-4 space-y-4"
      >
        <h1 className="text-lg font-bold">Upload video</h1>

        <div
          onClick={() => fileRef.current?.click()}
          className="aspect-[9/16] rounded-xl border-2 border-dashed border-white/20 hover:border-white/40 cursor-pointer flex items-center justify-center bg-black overflow-hidden"
        >
          {previewUrl ? (
            <video
              src={previewUrl}
              controls
              playsInline
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="text-white/60 text-sm text-center px-6">
              Tap to pick a video
              <div className="text-xs text-white/40 mt-1">
                mp4 / webm / mov · up to {MAX_MB}MB
              </div>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="video/mp4,video/webm,video/quicktime"
            onChange={(e) => pick(e.target.files?.[0] ?? null)}
            className="hidden"
          />
        </div>

        <label className="block">
          <span className="text-xs text-white/60">Caption</span>
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value.slice(0, 280))}
            rows={2}
            placeholder="say something…"
            className="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30 resize-none"
          />
          <div className="text-[10px] text-white/40 text-right">
            {caption.length}/280
          </div>
        </label>

        {myListings.length > 0 && (
          <label className="block">
            <span className="text-xs text-white/60">Attach a listing (optional)</span>
            <select
              value={listingId}
              onChange={(e) => setListingId(e.target.value)}
              className="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none focus:border-white/30"
            >
              <option value="" className="bg-black">
                — none —
              </option>
              {myListings.map((l) => (
                <option key={l.id} value={l.id} className="bg-black">
                  {l.title} · {formatEther(BigInt(l.priceWei))} ETH
                </option>
              ))}
            </select>
          </label>
        )}

        <fieldset className="rounded-lg bg-white/5 p-3 space-y-2">
          <legend className="text-xs text-white/60 px-1">
            Token-gate (optional)
          </legend>
          <div className="flex gap-2">
            <label className="flex-1">
              <span className="text-[10px] text-white/50">Unlock token</span>
              <input
                value={unlockToken}
                onChange={(e) =>
                  setUnlockToken(
                    e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "")
                  )
                }
                maxLength={12}
                placeholder="CARROT"
                className="mt-0.5 w-full rounded-md bg-white/5 border border-white/10 px-2 py-1.5 text-sm outline-none focus:border-white/30"
              />
            </label>
            <label className="flex-1">
              <span className="text-[10px] text-white/50">Price (ETH)</span>
              <input
                value={unlockPrice}
                onChange={(e) =>
                  setUnlockPrice(e.target.value.replace(/[^0-9.]/g, ""))
                }
                inputMode="decimal"
                placeholder="0.001"
                className="mt-0.5 w-full rounded-md bg-white/5 border border-white/10 px-2 py-1.5 text-sm outline-none focus:border-white/30"
              />
            </label>
          </div>
        </fieldset>

        {err && (
          <div className="text-xs text-red-400 break-all">{err}</div>
        )}

        <button
          type="submit"
          disabled={!file || submitting}
          className="w-full py-3 rounded-xl bg-[#ff2d87] text-black font-semibold disabled:opacity-50"
        >
          {submitting ? "Uploading…" : "Post"}
        </button>

        <div className="text-[10px] text-white/40 text-center">
          Stored locally for dev. Swap to Vercel Blob / R2 / IPFS for prod.
        </div>
      </form>
    </div>
  );
}
