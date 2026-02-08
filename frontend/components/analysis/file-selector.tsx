"use client";

import { FileText, Check } from "lucide-react";
import { cn, getFileTypeLabel } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { FileInfo } from "@/lib/types";

interface FileSelectorProps {
  files: FileInfo[];
  selectedFiles: string[];
  onToggleFile: (filename: string) => void;
  loading: boolean;
}

export function FileSelector({
  files,
  selectedFiles,
  onToggleFile,
  loading,
}: FileSelectorProps) {
  if (loading) {
    return (
      <div className="flex gap-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-8 w-32 bg-muted animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No documents uploaded. Upload files in the Documents page first.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
        Select documents to analyze
      </p>
      <div className="flex flex-wrap gap-2">
        {files.map((file) => {
          const isSelected = selectedFiles.includes(file.name);
          return (
            <button
              key={file.name}
              onClick={() => onToggleFile(file.name)}
              className={cn(
                "inline-flex items-center gap-2 px-3 py-1.5 text-xs border transition-colors",
                isSelected
                  ? "border-orange-500 bg-orange-500/10 text-orange-500"
                  : "border-border text-muted-foreground hover:border-foreground hover:text-foreground"
              )}
            >
              {isSelected ? (
                <Check className="size-3" />
              ) : (
                <FileText className="size-3" />
              )}
              <span className="truncate max-w-[150px]">{file.name}</span>
              <Badge
                variant="outline"
                className="rounded-none text-[10px] px-1 py-0"
              >
                {getFileTypeLabel(file.name)}
              </Badge>
            </button>
          );
        })}
      </div>
    </div>
  );
}
