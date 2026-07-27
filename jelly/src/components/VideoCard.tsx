"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import type { FeedItem } from "@/lib/sample-videos";

function truncate(addr: string) {
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

export function VideoCard({ item }: { item: FeedItem }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [liked, setLiked] = useState(false);
  const [muted, setMuted] = useState(true);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const el = containerRef.current;
    const video = videoRef.current;
    if (!el || !video) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.6) {
          video.play().then(() => setPlaying(true)).catch(() => {});
        } else {
          video.pause();
          setPlaying(false);
        }
      },
      { threshold: [0, 0.6, 1] }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) {
      video.play();
      setPlaying(true);
    } else {
      video.pause();
      setPlaying(false);
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative h-[100dvh] w-full snap-start snap-always flex items-center justify-center bg-black"
    >
      <video
        ref={videoRef}
        src={item.src}
        loop
        muted={muted}
        playsInline
        onClick={togglePlay}
        className="h-full w-full object-cover sm:max-w-md sm:rounded-2xl"
      />

      {!playing && (
        <button
          onClick={togglePlay}
          aria-label="Play"
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
        >
          <span className="h-20 w-20 rounded-full bg-black/40 backdrop-blur flex items-center justify-center text-3xl pointer-events-auto">
            ▶
          </span>
        </button>
      )}

      <div className="absolute right-3 bottom-28 flex flex-col items-center gap-5">
        <button
          onClick={() => setLiked((v) => !v)}
          aria-label="Like"
          className="flex flex-col items-center"
        >
          <span
            className={`text-3xl transition ${
              liked ? "scale-110" : ""
            }`}
          >
            {liked ? "❤️" : "🤍"}
          </span>
          <span className="text-xs mt-1 text-white/80">
            {liked ? "1" : "0"}
          </span>
        </button>
        <button
          onClick={() => setMuted((v) => !v)}
          aria-label="Mute"
          className="text-2xl"
        >
          {muted ? "🔇" : "🔊"}
        </button>
      </div>

      <div className="absolute left-0 right-0 bottom-0 p-4 sm:max-w-md sm:mx-auto bg-gradient-to-t from-black/80 to-transparent">
        <div className="text-sm font-semibold">
          @{truncate(item.creator)}
        </div>
        <div className="text-sm text-white/90 mt-1">{item.caption}</div>
        {item.listingId ? (
          <Link
            href={`/listing/${item.listingId}`}
            className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#ff2d87] text-black text-sm font-semibold"
          >
            🛒 Buy this →
          </Link>
        ) : item.unlockToken ? (
          <Link
            href={`/swap?out=${item.unlockToken}`}
            className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#ff2d87] text-black text-sm font-semibold"
          >
            🔓 Unlock for {item.unlockPrice} ETH → ${item.unlockToken}
          </Link>
        ) : null}
      </div>
    </div>
  );
}
