import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";
import { randomUUID } from "crypto";
import { isAddress } from "viem";
import { appendFeed } from "@/lib/feed-store";

export const runtime = "nodejs";

const MAX_BYTES = 50 * 1024 * 1024; // 50 MB
const ALLOWED_MIME = new Set([
  "video/mp4",
  "video/webm",
  "video/quicktime",
]);
const EXT_BY_MIME: Record<string, string> = {
  "video/mp4": ".mp4",
  "video/webm": ".webm",
  "video/quicktime": ".mov",
};

const UPLOAD_DIR = path.join(process.cwd(), "public", "uploads");

export async function POST(req: NextRequest) {
  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    return NextResponse.json({ error: "invalid form" }, { status: 400 });
  }

  const file = form.get("video");
  const creator = String(form.get("creator") ?? "");
  const caption = String(form.get("caption") ?? "").slice(0, 280);
  const unlockToken = String(form.get("unlockToken") ?? "")
    .trim()
    .toUpperCase()
    .slice(0, 12) || undefined;
  const unlockPrice = String(form.get("unlockPrice") ?? "").trim() || undefined;
  const listingId = String(form.get("listingId") ?? "").trim() || undefined;

  if (!(file instanceof File)) {
    return NextResponse.json({ error: "video required" }, { status: 400 });
  }
  if (!isAddress(creator, { strict: false })) {
    return NextResponse.json({ error: "valid creator address required" }, { status: 400 });
  }
  if (!ALLOWED_MIME.has(file.type)) {
    return NextResponse.json(
      { error: `mime ${file.type} not allowed` },
      { status: 415 }
    );
  }
  if (file.size > MAX_BYTES) {
    return NextResponse.json({ error: "file too large" }, { status: 413 });
  }
  if (unlockToken && (!unlockPrice || isNaN(Number(unlockPrice)))) {
    return NextResponse.json(
      { error: "unlockPrice required when unlockToken set" },
      { status: 400 }
    );
  }

  await fs.mkdir(UPLOAD_DIR, { recursive: true });

  const id = randomUUID();
  const ext = EXT_BY_MIME[file.type] ?? ".mp4";
  const filename = `${id}${ext}`;
  const dest = path.join(UPLOAD_DIR, filename);
  const buf = Buffer.from(await file.arrayBuffer());
  await fs.writeFile(dest, buf);

  const item = {
    id,
    src: `/uploads/${filename}`,
    creator,
    caption: caption || "(no caption)",
    unlockToken,
    unlockPrice,
    listingId,
    createdAt: Date.now(),
  };

  await appendFeed(item);

  return NextResponse.json({ ok: true, item });
}
