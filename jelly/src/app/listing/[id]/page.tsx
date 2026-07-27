import Link from "next/link";
import { notFound } from "next/navigation";
import { getListing, getMerchant } from "@/lib/merchant-store";
import { ListingBuy } from "@/components/ListingBuy";

export const dynamic = "force-dynamic";

function truncate(addr: string) {
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

export default async function ListingPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const listing = await getListing(id);
  if (!listing) notFound();
  const merchant = await getMerchant(listing.merchant);
  const merchantName = merchant?.name ?? truncate(listing.merchant);

  return (
    <div className="flex-1 flex flex-col items-center pt-6 pb-12 px-4">
      <div className="w-full max-w-md space-y-4">
        <Link
          href={`/creator/${listing.merchant}`}
          className="text-xs text-white/60 hover:text-white"
        >
          ← {merchantName}
        </Link>

        <div className="rounded-2xl bg-white/5 border border-white/10 p-5 space-y-3">
          <h1 className="text-2xl font-bold">{listing.title}</h1>
          {listing.description && (
            <p className="text-sm text-white/80 whitespace-pre-wrap">
              {listing.description}
            </p>
          )}
        </div>

        <div className="rounded-2xl bg-white/5 border border-white/10 p-5">
          <ListingBuy listing={listing} merchantName={merchantName} />
        </div>
      </div>
    </div>
  );
}
