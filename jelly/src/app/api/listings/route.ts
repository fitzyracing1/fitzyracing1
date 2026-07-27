import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { isAddress, getAddress, parseEther } from "viem";
import {
  appendListing,
  getMerchant,
  type ListingType,
} from "@/lib/merchant-store";

export const runtime = "nodejs";

const ALLOWED_TYPES: ListingType[] = [
  "digital_link",
  "physical_good",
  "service",
];

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid json" }, { status: 400 });

  const merchantAddr = String(body.merchant ?? "");
  const title = String(body.title ?? "").trim().slice(0, 120);
  const description = String(body.description ?? "").trim().slice(0, 1000);
  const priceEth = String(body.priceEth ?? "").trim();
  const type = String(body.type ?? "") as ListingType;

  if (!isAddress(merchantAddr, { strict: false })) {
    return NextResponse.json({ error: "valid merchant address required" }, { status: 400 });
  }
  if (!title) {
    return NextResponse.json({ error: "title required" }, { status: 400 });
  }
  if (!ALLOWED_TYPES.includes(type)) {
    return NextResponse.json({ error: "invalid type" }, { status: 400 });
  }
  if (!priceEth || isNaN(Number(priceEth)) || Number(priceEth) <= 0) {
    return NextResponse.json({ error: "priceEth must be > 0" }, { status: 400 });
  }

  const merchant = await getMerchant(merchantAddr);
  if (!merchant) {
    return NextResponse.json(
      { error: "merchant not registered" },
      { status: 404 }
    );
  }

  let priceWei: bigint;
  try {
    priceWei = parseEther(priceEth);
  } catch {
    return NextResponse.json({ error: "invalid priceEth" }, { status: 400 });
  }

  const listing = {
    id: randomUUID(),
    merchant: getAddress(merchantAddr),
    title,
    description,
    priceWei: priceWei.toString(),
    type,
    createdAt: Date.now(),
  };
  await appendListing(listing);
  return NextResponse.json({ ok: true, listing });
}
