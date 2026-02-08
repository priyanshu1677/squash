import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface RiceScoreDisplayProps {
  score?: number;
  reach?: number;
  impact?: number;
  confidence?: number;
  effort?: number;
}

export function RiceScoreDisplay({
  score,
  reach,
  impact,
  confidence,
  effort,
}: RiceScoreDisplayProps) {
  if (score === undefined) return null;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="inline-flex items-center gap-1.5">
            <span className="font-mono text-lg font-semibold text-orange-500">
              {score.toFixed(1)}
            </span>
            <span className="text-xs text-muted-foreground">RICE</span>
          </div>
        </TooltipTrigger>
        <TooltipContent className="rounded-none">
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <span className="text-muted-foreground">Reach</span>
            <span className="font-mono">{reach ?? "—"}</span>
            <span className="text-muted-foreground">Impact</span>
            <span className="font-mono">{impact ?? "—"}</span>
            <span className="text-muted-foreground">Confidence</span>
            <span className="font-mono">{confidence ?? "—"}</span>
            <span className="text-muted-foreground">Effort</span>
            <span className="font-mono">{effort ?? "—"}</span>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
