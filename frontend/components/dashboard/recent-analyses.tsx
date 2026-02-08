"use client";

import Link from "next/link";
import { Clock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AnalysisHistoryEntry } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export function RecentAnalyses({
  history,
}: {
  history: AnalysisHistoryEntry[];
}) {
  const recent = history.slice(0, 5);

  if (recent.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent Analyses</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No analyses yet. Run your first analysis to see results here.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent Analyses</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {recent.map((entry) => (
          <Link
            key={entry.id}
            href={`/history/${entry.id}`}
            className="flex items-center justify-between p-3 border border-border hover:bg-accent transition-colors group"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate group-hover:text-orange-500 transition-colors">
                {entry.query}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <Clock className="size-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  {formatDate(entry.timestamp)}
                </span>
              </div>
            </div>
            {entry.result.top_feature && (
              <Badge
                variant="outline"
                className="ml-2 rounded-none text-xs shrink-0"
              >
                {entry.result.top_feature.name}
              </Badge>
            )}
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}
