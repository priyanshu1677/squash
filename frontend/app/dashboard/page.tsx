"use client";

import { PageHeader } from "@/components/shared/page-header";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { RecentAnalyses } from "@/components/dashboard/recent-analyses";
import { PipelineVisual } from "@/components/dashboard/pipeline-visual";
import { useFiles } from "@/lib/hooks/use-files";
import { useHealth } from "@/lib/hooks/use-health";
import { useAnalysisHistory } from "@/lib/hooks/use-analysis-history";

export default function DashboardPage() {
  const { files } = useFiles();
  const { isOnline } = useHealth();
  const { history } = useAnalysisHistory();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Dashboard"
        description="Overview of your product intelligence workspace"
      />

      <StatsCards files={files} history={history} isOnline={isOnline} />

      <QuickActions />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentAnalyses history={history} />
        <PipelineVisual />
      </div>
    </div>
  );
}
