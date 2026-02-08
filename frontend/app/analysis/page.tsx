"use client";

import { useState } from "react";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { QueryInput } from "@/components/analysis/query-input";
import { FileSelector } from "@/components/analysis/file-selector";
import { AnalysisLoading } from "@/components/analysis/analysis-loading";
import { AnalysisResults } from "@/components/analysis/analysis-results";
import { useFiles } from "@/lib/hooks/use-files";
import { useAnalysisHistory } from "@/lib/hooks/use-analysis-history";
import { runQuery } from "@/lib/api-client";
import { generateId } from "@/lib/utils";
import type { QueryResponse } from "@/lib/types";

export default function AnalysisPage() {
  const [query, setQuery] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const { files, loading: filesLoading } = useFiles();
  const { addEntry } = useAnalysisHistory();

  const toggleFile = (filename: string) => {
    setSelectedFiles((prev) =>
      prev.includes(filename)
        ? prev.filter((f) => f !== filename)
        : [...prev, filename]
    );
  };

  const handleRun = async () => {
    if (!query.trim()) return;

    setIsRunning(true);
    setResult(null);

    try {
      const response = await runQuery(query, selectedFiles);
      setResult(response);

      // Save to history
      addEntry({
        id: generateId(),
        query,
        files: selectedFiles,
        timestamp: Date.now(),
        result: response,
      });

      toast.success("Analysis complete");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Analysis failed"
      );
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Analysis"
        description="Query your customer data and discover feature opportunities"
      />

      <div className="space-y-4">
        <QueryInput
          query={query}
          onQueryChange={setQuery}
          onRun={handleRun}
          isRunning={isRunning}
        />

        <FileSelector
          files={files}
          selectedFiles={selectedFiles}
          onToggleFile={toggleFile}
          loading={filesLoading}
        />
      </div>

      {isRunning && <AnalysisLoading />}

      {result && !isRunning && <AnalysisResults result={result} />}
    </div>
  );
}
