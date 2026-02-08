import { Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { ConfidenceBadge } from "@/components/shared/confidence-badge";
import { RiceScoreDisplay } from "@/components/shared/rice-score-display";
import type { TopFeature } from "@/lib/types";

export function TopFeatureCard({ feature }: { feature: TopFeature }) {
  return (
    <Card className="relative overflow-hidden border-orange-500/30 bg-gradient-to-br from-orange-500/5 via-transparent to-transparent">
      <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 blur-3xl" />
      <CardContent className="py-6 relative">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-3 flex-1">
            <div className="flex items-center gap-2">
              <Sparkles className="size-4 text-orange-500" />
              <span className="text-xs font-medium text-orange-500 uppercase tracking-wider">
                Top Feature
              </span>
            </div>
            <h2 className="text-xl font-semibold">{feature.name}</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {feature.description}
            </p>
            <div className="flex items-center gap-3 pt-1">
              <ConfidenceBadge confidence={feature.confidence} />
              <RiceScoreDisplay
                score={feature.rice_score}
                reach={feature.reach}
                impact={feature.impact}
                confidence={feature.confidence_score}
                effort={feature.effort}
              />
            </div>
          </div>
        </div>

        {feature.evidence && feature.evidence.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">
              Evidence
            </p>
            <ul className="space-y-1">
              {feature.evidence.map((ev, i) => (
                <li
                  key={i}
                  className="text-sm text-muted-foreground flex items-start gap-2"
                >
                  <span className="text-orange-500 mt-1">&#8226;</span>
                  {ev}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
