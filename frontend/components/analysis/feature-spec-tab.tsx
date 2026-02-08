import { MarkdownRenderer } from "@/components/shared/markdown-renderer";

export function FeatureSpecTab({ markdown }: { markdown?: string }) {
  if (!markdown) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        No feature specification generated for this analysis.
      </p>
    );
  }

  return (
    <div className="py-4">
      <MarkdownRenderer content={markdown} />
    </div>
  );
}
