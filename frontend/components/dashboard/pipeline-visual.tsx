"use client";

import {
  Database,
  Layers,
  Brain,
  Target,
  FileText,
  CheckCircle,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { PIPELINE_NODES } from "@/lib/constants";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Database,
  Layers,
  Brain,
  Target,
  FileText,
  CheckCircle,
};

export function PipelineVisual() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">LangGraph Pipeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap items-center gap-2">
          {PIPELINE_NODES.map((node, index) => {
            const Icon = ICONS[node.icon];
            return (
              <div key={node.id} className="flex items-center gap-2">
                <div className="flex items-center gap-2 px-3 py-2 border border-border bg-muted/50 hover:border-orange-500/50 transition-colors">
                  {Icon && (
                    <Icon className="size-4 text-orange-500 shrink-0" />
                  )}
                  <div>
                    <p className="text-xs font-medium">{node.label}</p>
                    <p className="text-[10px] text-muted-foreground hidden sm:block">
                      {node.description}
                    </p>
                  </div>
                </div>
                {index < PIPELINE_NODES.length - 1 && (
                  <div className="w-4 h-px bg-border shrink-0" />
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
