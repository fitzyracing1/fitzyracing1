import { SwapForm } from "@/components/SwapForm";
import { TOKENS, type TokenSymbol } from "@/lib/tokens";

export default async function SwapPage({
  searchParams,
}: {
  searchParams: Promise<{ out?: string }>;
}) {
  const { out } = await searchParams;
  const presetOut =
    out && (out as string) in TOKENS ? (out as TokenSymbol) : undefined;
  return (
    <div className="flex-1 flex items-start justify-center pt-8">
      <SwapForm presetOut={presetOut} />
    </div>
  );
}
