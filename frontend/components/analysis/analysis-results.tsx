"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TopFeatureCard } from "./top-feature-card";
import { FeatureSpecTab } from "./feature-spec-tab";
import { UIProposalsTab } from "./ui-proposals-tab";
import { TaskBreakdownTab } from "./task-breakdown-tab";
import { OpportunitiesTab } from "./opportunities-tab";
import type { QueryResponse } from "@/lib/types";

export function AnalysisResults({ result }: { result: QueryResponse }) {
  return (
    <div className="space-y-6">
      {result.top_feature && <TopFeatureCard feature={result.top_feature} />}

      <Tabs defaultValue="spec" className="w-full">
        <TabsList className="w-full justify-start rounded-none border-b border-border bg-transparent p-0 h-auto">
          <TabsTrigger
            value="spec"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-orange-500 data-[state=active]:text-orange-500 data-[state=active]:bg-transparent px-4 py-2"
          >
            Feature Spec
          </TabsTrigger>
          <TabsTrigger
            value="ui"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-orange-500 data-[state=active]:text-orange-500 data-[state=active]:bg-transparent px-4 py-2"
          >
            UI Proposals
          </TabsTrigger>
          <TabsTrigger
            value="tasks"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-orange-500 data-[state=active]:text-orange-500 data-[state=active]:bg-transparent px-4 py-2"
          >
            Task Breakdown
          </TabsTrigger>
          <TabsTrigger
            value="opportunities"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-orange-500 data-[state=active]:text-orange-500 data-[state=active]:bg-transparent px-4 py-2"
          >
            Opportunities
          </TabsTrigger>
        </TabsList>
        <TabsContent value="spec">
          <FeatureSpecTab markdown={result.feature_spec_markdown} />
        </TabsContent>
        <TabsContent value="ui">
          <UIProposalsTab markdown={result.ui_proposals_markdown} />
        </TabsContent>
        <TabsContent value="tasks">
          <TaskBreakdownTab markdown={result.task_breakdown_markdown} />
        </TabsContent>
        <TabsContent value="opportunities">
          <OpportunitiesTab opportunities={result.all_opportunities} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
