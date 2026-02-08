"use client";

import { FileText, Brain, Plug, Activity } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { FileInfo, AnalysisHistoryEntry } from "@/lib/types";

interface StatsCardsProps {
  files: FileInfo[];
  history: AnalysisHistoryEntry[];
  isOnline: boolean;
}

export function StatsCards({ files, history, isOnline }: StatsCardsProps) {
  const stats = [
    {
      label: "Documents",
      value: files.length,
      icon: FileText,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
    },
    {
      label: "Analyses",
      value: history.length,
      icon: Brain,
      color: "text-orange-500",
      bg: "bg-orange-500/10",
    },
    {
      label: "Integrations",
      value: "7",
      icon: Plug,
      color: "text-purple-500",
      bg: "bg-purple-500/10",
    },
    {
      label: "Backend",
      value: isOnline ? "Online" : "Offline",
      icon: Activity,
      color: isOnline ? "text-green-500" : "text-red-500",
      bg: isOnline ? "bg-green-500/10" : "bg-red-500/10",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="py-4">
          <CardContent className="flex items-center gap-4">
            <div
              className={`size-10 flex items-center justify-center ${stat.bg}`}
            >
              <stat.icon className={`size-5 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className="text-2xl font-semibold font-mono">{stat.value}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
