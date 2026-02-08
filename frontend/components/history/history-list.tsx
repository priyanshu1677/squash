"use client";

import Link from "next/link";
import { Clock, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ConfidenceBadge } from "@/components/shared/confidence-badge";
import type { AnalysisHistoryEntry } from "@/lib/types";
import { formatDate } from "@/lib/utils";

interface HistoryListProps {
  history: AnalysisHistoryEntry[];
  onRemove: (id: string) => void;
}

export function HistoryList({ history, onRemove }: HistoryListProps) {
  return (
    <div className="space-y-3">
      {history.map((entry) => (
        <Card key={entry.id} className="py-3 group">
          <CardContent className="flex items-center gap-4">
            <Link
              href={`/history/${entry.id}`}
              className="flex-1 min-w-0 space-y-1"
            >
              <p className="text-sm font-medium group-hover:text-orange-500 transition-colors truncate">
                {entry.query}
              </p>
              <div className="flex items-center gap-3 flex-wrap">
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="size-3" />
                  {formatDate(entry.timestamp)}
                </div>
                {entry.result.top_feature && (
                  <>
                    <Badge
                      variant="outline"
                      className="rounded-none text-xs"
                    >
                      {entry.result.top_feature.name}
                    </Badge>
                    <ConfidenceBadge
                      confidence={entry.result.top_feature.confidence}
                    />
                  </>
                )}
                {entry.files.length > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {entry.files.length} file
                    {entry.files.length !== 1 ? "s" : ""}
                  </span>
                )}
              </div>
            </Link>
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={(e) => {
                e.preventDefault();
                onRemove(entry.id);
              }}
              className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
            >
              <Trash2 className="size-3.5" />
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
