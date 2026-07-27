import Link from "next/link";

export default function Home() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 text-center">
      <h1 className="text-5xl sm:text-7xl font-black tracking-tight">
        <span className="text-[#ff2d87]">jelly</span>
      </h1>
      <p className="mt-4 max-w-md text-white/70">
        Swap tokens. Watch shorts. Unlock real-world access.
      </p>
      <div className="mt-8 flex gap-3">
        <Link
          href="/feed"
          className="px-5 py-2.5 rounded-full bg-[#ff2d87] text-black font-semibold hover:opacity-90"
        >
          Open feed
        </Link>
        <Link
          href="/swap"
          className="px-5 py-2.5 rounded-full bg-white/10 hover:bg-white/20 font-semibold"
        >
          Swap
        </Link>
      </div>
    </div>
  );
}
