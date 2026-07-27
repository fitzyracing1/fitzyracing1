import { NextRequest, NextResponse } from "next/server";
import { isAddress, getAddress } from "viem";
import { listMerchants, upsertMerchant } from "@/lib/merchant-store";

export const runtime = "nodejs";

export async function GET() {
  const all = await listMerchants();
  return NextResponse.json({ merchants: all });
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid json" }, { status: 400 });

  const address = String(body.address ?? "");
  const name = String(body.name ?? "").trim().slice(0, 60);
  const bio = String(body.bio ?? "").trim().slice(0, 500);

  if (!isAddress(address, { strict: false })) {
    return NextResponse.json({ error: "valid address required" }, { status: 400 });
  }
  if (!name) {
    return NextResponse.json({ error: "name required" }, { status: 400 });
  }

  const merchant = {
    address: getAddress(address),
    name,
    bio,
    createdAt: Date.now(),
  };
  await upsertMerchant(merchant);
  return NextResponse.json({ ok: true, merchant });
}
