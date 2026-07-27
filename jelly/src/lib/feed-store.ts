import { promises as fs } from "fs";
import path from "path";
import type { FeedItem } from "./sample-videos";

export type StoredFeedItem = FeedItem & { createdAt: number };

const DATA_DIR = path.join(process.cwd(), "data");
const FEED_FILE = path.join(DATA_DIR, "feed.json");

async function ensure() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  try {
    await fs.access(FEED_FILE);
  } catch {
    await fs.writeFile(FEED_FILE, "[]", "utf-8");
  }
}

export async function readFeed(): Promise<StoredFeedItem[]> {
  await ensure();
  const raw = await fs.readFile(FEED_FILE, "utf-8");
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export async function appendFeed(item: StoredFeedItem) {
  const all = await readFeed();
  all.unshift(item);
  await fs.writeFile(FEED_FILE, JSON.stringify(all, null, 2), "utf-8");
}
