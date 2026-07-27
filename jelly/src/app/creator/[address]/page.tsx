import Link from "next/link";
import { notFound } from "next/navigation";
import { isAddress } from "viem";
import { formatEther } from "viem";
import { getMerchant, listingsByMerchant } from "@/lib/merchant-store";

export const dynamic = "force-dynamic";

function truncate(addr: string) {
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

const TYPE_LABEL: Record<string, string> = {
  digital_link: "Digital",
  physical_good: "Physical",
  service: "Service",
};

export default async function CreatorPage({
  params,
}: {
  params: Promise<{ address: string }>;
}) {
  const { address } = await params;
  if (!isAddress(address, { strict: false })) notFound();
  const merchant = await getMerchant(address);
  if (!merchant) notFound();
  const listings = await listingsByMerchant(address);

  return (
    <div className="flex-1 flex flex-col items-center pt-6 pb-12 px-4">
      <div className="w-full max-w-md space-y-4">
        <header className="rounded-2xl bg-white/5 border border-white/10 p-5">
          <div className="text-2xl font-black">{merchant.name}</div>
          <div className="text-xs font-mono text-white/50 mt-1">
            {truncate(merchant.address)}
          </div>
          {merchant.bio && (
            <p className="text-sm text-white/80 mt-3">{merchant.bio}</p>
          )}
        </header>

        <h2 className="text-sm font-semibold text-white/80">
          Listings ({listings.length})
        </h2>

        {listings.length === 0 ? (
          <div className="text-sm text-white/50 rounded-xl bg-white/5 p-6 text-center">
            Nothing for sale yet.
          </div>
        ) : (
          <div className="space-y-2">
            {listings.map((l) => (
              <Link
                key={l.id}
                href={`/listing/${l.id}`}
                className="block rounded-xl bg-white/5 border border-white/10 p-4 hover:bg-white/10"
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
                {l.description && (
                  <p className="text-sm text-white/70 mt-2 line-clamp-2">
                    {l.description}
                  </p>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
