import { NextRequest, NextResponse } from "next/server";
import { isAddress } from "viem";
import { getMerchant, listingsByMerchant } from "@/lib/merchant-store";

export const runtime = "nodejs";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ address: string }> }
) {
  const { address } = await params;
  if (!isAddress(address, { strict: false })) {
    return NextResponse.json({ error: "invalid address" }, { status: 400 });
  }
  const merchant = await getMerchant(address);
  if (!merchant) {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }
  const listings = await listingsByMerchant(address);
  return NextResponse.json({ merchant, listings });
}
