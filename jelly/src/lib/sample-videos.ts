export type FeedItem = {
  id: string;
  src: string;
  creator: string;
  caption: string;
  unlockToken?: string;
  unlockPrice?: string;
  listingId?: string;
};

export const sampleFeed: FeedItem[] = [
  {
    id: "1",
    src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    creator: "0x742d35Cc6634C0532925a3b844Bc9e7595f1a234",
    caption: "Bunny's morning routine. swap $CARROT to unlock the workout plan.",
    unlockToken: "CARROT",
    unlockPrice: "0.001",
  },
  {
    id: "2",
    src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    creator: "0x8ba1f109551bD432803012645Ac136ddd64DBA72",
    caption: "Dream sequence. swap $DREAM for the uncut version.",
    unlockToken: "DREAM",
    unlockPrice: "0.005",
  },
  {
    id: "3",
    src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    creator: "0xab5801a7d398351b8be11c439e05c5b3259aec9b",
    caption: "Blaze it. free this week.",
  },
  {
    id: "4",
    src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    creator: "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",
    caption: "Escape room IRL — swap $KEY to book your slot.",
    unlockToken: "KEY",
    unlockPrice: "0.01",
  },
];
