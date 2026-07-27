import { promises as fs } from "fs";
import path from "path";

export type Merchant = {
  address: string;
  name: string;
  bio: string;
  createdAt: number;
};

export type ListingType = "digital_link" | "physical_good" | "service";

export type Listing = {
  id: string;
  merchant: string; // address
  title: string;
  description: string;
  priceWei: string; // string-encoded bigint, ETH on Base
  type: ListingType;
  createdAt: number;
};

const DATA_DIR = path.join(process.cwd(), "data");
const MERCHANT_FILE = path.join(DATA_DIR, "merchants.json");
const LISTING_FILE = path.join(DATA_DIR, "listings.json");

async function ensureFile(file: string) {
  await fs.mkdir(DATA_DIR, { recursive: true });
  try {
    await fs.access(file);
  } catch {
    await fs.writeFile(file, "[]", "utf-8");
  }
}

async function readJson<T>(file: string): Promise<T[]> {
  await ensureFile(file);
  const raw = await fs.readFile(file, "utf-8");
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as T[]) : [];
  } catch {
    return [];
  }
}

async function writeJson<T>(file: string, items: T[]) {
  await fs.writeFile(file, JSON.stringify(items, null, 2), "utf-8");
}

function lc(addr: string) {
  return addr.toLowerCase();
}

export async function listMerchants(): Promise<Merchant[]> {
  return readJson<Merchant>(MERCHANT_FILE);
}

export async function getMerchant(address: string): Promise<Merchant | null> {
  const all = await listMerchants();
  return all.find((m) => lc(m.address) === lc(address)) ?? null;
}

export async function upsertMerchant(m: Merchant) {
  const all = await listMerchants();
  const idx = all.findIndex((x) => lc(x.address) === lc(m.address));
  if (idx >= 0) {
    all[idx] = { ...all[idx], ...m, createdAt: all[idx].createdAt };
  } else {
    all.push(m);
  }
  await writeJson(MERCHANT_FILE, all);
}

export async function listListings(): Promise<Listing[]> {
  return readJson<Listing>(LISTING_FILE);
}

export async function listingsByMerchant(address: string): Promise<Listing[]> {
  const all = await listListings();
  return all.filter((l) => lc(l.merchant) === lc(address));
}

export async function getListing(id: string): Promise<Listing | null> {
  const all = await listListings();
  return all.find((l) => l.id === id) ?? null;
}

export async function appendListing(l: Listing) {
  const all = await listListings();
  all.unshift(l);
  await writeJson(LISTING_FILE, all);
}
