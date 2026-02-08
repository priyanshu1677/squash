import Link from "next/link";
import { Clock } from "lucide-react";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";

export function EmptyHistory() {
  return (
    <EmptyState
      icon={Clock}
      title="No analysis history"
      description="Run your first analysis to see results here. History is stored locally."
      action={
        <Button variant="orange" asChild>
          <Link href="/analysis">Run Analysis</Link>
        </Button>
      }
    />
  );
}
