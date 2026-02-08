"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AnalysisResults } from "@/components/analysis/analysis-results";
import { useAnalysisHistory } from "@/lib/hooks/use-analysis-history";
import { formatDate } from "@/lib/utils";

export default function HistoryDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { getEntry } = useAnalysisHistory();
  const entry = getEntry(id);

  if (!entry) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <div className="text-center py-16">
          <h2 className="text-lg font-medium mb-2">Analysis not found</h2>
          <p className="text-sm text-muted-foreground mb-6">
            This analysis may have been removed from history.
          </p>
          <Button variant="orange" asChild>
            <Link href="/history">Back to History</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="space-y-3">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/history">
            <ArrowLeft className="size-3.5 mr-1.5" />
            Back to History
          </Link>
        </Button>

        <div className="space-y-2">
          <h1 className="text-xl font-semibold">{entry.query}</h1>
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="size-3" />
              {formatDate(entry.timestamp)}
            </div>
            {entry.files.length > 0 && (
              <div className="flex gap-1.5">
                {entry.files.map((file) => (
                  <Badge
                    key={file}
                    variant="outline"
                    className="rounded-none text-xs"
                  >
                    {file}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <AnalysisResults result={entry.result} />
    </div>
  );
}
