"use client";

import Link from "next/link";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/feed", label: "Feed" },
  { href: "/upload", label: "Upload" },
  { href: "/sell", label: "Sell" },
  { href: "/swap", label: "Swap" },
];

export function Header() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/70 backdrop-blur">
      <Link href="/" className="text-xl font-black tracking-tight">
        <span className="text-[#ff2d87]">jelly</span>
      </Link>
      <nav className="flex gap-1">
        {tabs.map((t) => {
          const active = pathname.startsWith(t.href);
          return (
            <Link
              key={t.href}
              href={t.href}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${
                active
                  ? "bg-white text-black"
                  : "text-white/70 hover:text-white"
              }`}
            >
              {t.label}
            </Link>
          );
        })}
      </nav>
      <ConnectButton
        accountStatus="address"
        chainStatus="icon"
        showBalance={false}
      />
    </header>
  );
}
