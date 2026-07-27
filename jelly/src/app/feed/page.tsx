import { VideoCard } from "@/components/VideoCard";
import { sampleFeed } from "@/lib/sample-videos";
import { readFeed } from "@/lib/feed-store";

export const dynamic = "force-dynamic";

export default async function FeedPage() {
  const uploaded = await readFeed();
  const items = [...uploaded, ...sampleFeed];

  return (
    <div className="h-[calc(100dvh-57px)] overflow-y-scroll snap-y snap-mandatory">
      {items.map((item) => (
        <VideoCard key={item.id} item={item} />
      ))}
    </div>
  );
}
