import { FileText } from "lucide-react";
import { EmptyState } from "@/components/shared/empty-state";

export function EmptyDocuments() {
  return (
    <EmptyState
      icon={FileText}
      title="No documents yet"
      description="Upload customer interview transcripts, support reports, or product documents to analyze."
    />
  );
}
