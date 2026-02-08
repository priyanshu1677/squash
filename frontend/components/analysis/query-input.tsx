"use client";

import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";
import { QUERY_SUGGESTIONS } from "@/lib/constants";

interface QueryInputProps {
  query: string;
  onQueryChange: (query: string) => void;
  onRun: () => void;
  isRunning: boolean;
}

export function QueryInput({
  query,
  onQueryChange,
  onRun,
  isRunning,
}: QueryInputProps) {
  return (
    <div className="space-y-3">
      <div className="relative">
        <Textarea
          placeholder="Ask about customer feedback, feature requests, or product priorities..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          className="min-h-[100px] resize-none rounded-none text-sm pr-20"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              onRun();
            }
          }}
        />
        <Button
          onClick={onRun}
          disabled={!query.trim() || isRunning}
          className="absolute bottom-3 right-3"
          size="sm"
        >
          <Play className="size-3.5" />
          {isRunning ? "Running..." : "Run"}
        </Button>
      </div>

      {/* Suggestion chips */}
      <div className="flex flex-wrap gap-2">
        {QUERY_SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onQueryChange(suggestion)}
            className="px-3 py-1 text-xs border border-border text-muted-foreground hover:border-orange-500 hover:text-orange-500 transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
