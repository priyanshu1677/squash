"use client";

import { useEffect, useState } from "react";
import {
  Database,
  Layers,
  Brain,
  Target,
  FileText,
  CheckCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PIPELINE_NODES } from "@/lib/constants";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Database,
  Layers,
  Brain,
  Target,
  FileText,
  CheckCircle,
};

// Simulated timing for each step in ms
const STEP_DURATIONS = [2000, 3000, 5000, 3000, 4000, 2000];

export function AnalysisLoading() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    let currentStep = 0;

    const advanceStep = () => {
      if (currentStep < PIPELINE_NODES.length - 1) {
        currentStep++;
        setActiveStep(currentStep);
        timeout = setTimeout(advanceStep, STEP_DURATIONS[currentStep]);
      }
    };

    timeout = setTimeout(advanceStep, STEP_DURATIONS[0]);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className="py-12 space-y-8">
      <div className="text-center space-y-2">
        <h3 className="text-lg font-medium">Analyzing your data...</h3>
        <p className="text-sm text-muted-foreground">
          Running through the LangGraph pipeline
        </p>
      </div>

      <div className="max-w-2xl mx-auto space-y-3">
        {PIPELINE_NODES.map((node, index) => {
          const Icon = ICONS[node.icon];
          const isActive = index === activeStep;
          const isComplete = index < activeStep;

          return (
            <div
              key={node.id}
              className={cn(
                "flex items-center gap-4 px-4 py-3 border transition-all duration-500",
                isActive && "border-orange-500 bg-orange-500/5",
                isComplete && "border-border bg-muted/30 opacity-60",
                !isActive && !isComplete && "border-border opacity-30"
              )}
            >
              <div
                className={cn(
                  "size-8 flex items-center justify-center shrink-0",
                  isActive && "animate-pulse-orange",
                  isComplete && "bg-green-500/10"
                )}
              >
                {isComplete ? (
                  <CheckCircle className="size-4 text-green-500" />
                ) : (
                  Icon && (
                    <Icon
                      className={cn(
                        "size-4",
                        isActive
                          ? "text-orange-500"
                          : "text-muted-foreground"
                      )}
                    />
                  )
                )}
              </div>
              <div className="flex-1">
                <p
                  className={cn(
                    "text-sm font-medium",
                    isActive && "text-orange-500"
                  )}
                >
                  {node.label}
                </p>
                <p className="text-xs text-muted-foreground">
                  {node.description}
                </p>
              </div>
              {isActive && (
                <div className="flex gap-1">
                  <div className="size-1.5 bg-orange-500 rounded-full animate-bounce" />
                  <div className="size-1.5 bg-orange-500 rounded-full animate-bounce [animation-delay:150ms]" />
                  <div className="size-1.5 bg-orange-500 rounded-full animate-bounce [animation-delay:300ms]" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
