import { MarkdownRenderer } from "@/components/shared/markdown-renderer";

export function UIProposalsTab({ markdown }: { markdown?: string }) {
  if (!markdown) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        No UI proposals generated for this analysis.
      </p>
    );
  }

  return (
    <div className="py-4">
      <MarkdownRenderer content={markdown} />
    </div>
  );
}
