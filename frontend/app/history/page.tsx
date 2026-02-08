"use client";

import { toast } from "sonner";
import { Trash2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { HistoryList } from "@/components/history/history-list";
import { EmptyHistory } from "@/components/history/empty-history";
import { Button } from "@/components/ui/button";
import { useAnalysisHistory } from "@/lib/hooks/use-analysis-history";

export default function HistoryPage() {
  const { history, removeEntry, clearHistory } = useAnalysisHistory();

  const handleClear = () => {
    clearHistory();
    toast.success("History cleared");
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-start justify-between">
        <PageHeader
          title="History"
          description="View past analyses and their results"
        />
        {history.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="size-3.5 mr-1.5" />
            Clear All
          </Button>
        )}
      </div>

      {history.length > 0 ? (
        <HistoryList history={history} onRemove={removeEntry} />
      ) : (
        <EmptyHistory />
      )}
    </div>
  );
}
