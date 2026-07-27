import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { base, baseSepolia } from "wagmi/chains";

export const wagmiConfig = getDefaultConfig({
  appName: "jelly",
  projectId: process.env.NEXT_PUBLIC_WC_PROJECT_ID ?? "jelly-dev",
  chains: [base, baseSepolia],
  ssr: true,
});
