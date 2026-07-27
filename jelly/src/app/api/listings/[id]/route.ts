import { NextRequest, NextResponse } from "next/server";
import { getListing, getMerchant } from "@/lib/merchant-store";

export const runtime = "nodejs";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const listing = await getListing(id);
  if (!listing) {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }
  const merchant = await getMerchant(listing.merchant);
  return NextResponse.json({ listing, merchant });
}
