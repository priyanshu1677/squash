import { MarkdownRenderer } from "@/components/shared/markdown-renderer";

export function TaskBreakdownTab({ markdown }: { markdown?: string }) {
  if (!markdown) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        No task breakdown generated for this analysis.
      </p>
    );
  }

  return (
    <div className="py-4">
      <MarkdownRenderer content={markdown} />
    </div>
  );
}
