import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const CONFIDENCE_STYLES: Record<string, string> = {
  high: "bg-green-500/10 text-green-500 border-green-500/20",
  medium: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  low: "bg-red-500/10 text-red-500 border-red-500/20",
};

export function ConfidenceBadge({
  confidence,
}: {
  confidence: string;
}) {
  const style = CONFIDENCE_STYLES[confidence] || CONFIDENCE_STYLES.medium;

  return (
    <Badge variant="outline" className={cn("rounded-none text-xs", style)}>
      {confidence}
    </Badge>
  );
}
