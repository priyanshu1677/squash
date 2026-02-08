"use client";

import { useState } from "react";
import { ArrowUpDown } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ConfidenceBadge } from "@/components/shared/confidence-badge";
import type { ScoredFeature } from "@/lib/types";

type SortField = "name" | "rice_score" | "confidence";

export function OpportunitiesTab({
  opportunities,
}: {
  opportunities?: ScoredFeature[];
}) {
  const [sortField, setSortField] = useState<SortField>("rice_score");
  const [sortAsc, setSortAsc] = useState(false);

  if (!opportunities || opportunities.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        No feature opportunities identified.
      </p>
    );
  }

  const sorted = [...opportunities].sort((a, b) => {
    let cmp = 0;
    if (sortField === "name") {
      cmp = a.name.localeCompare(b.name);
    } else if (sortField === "rice_score") {
      cmp = (a.rice_score ?? 0) - (b.rice_score ?? 0);
    } else if (sortField === "confidence") {
      const order: Record<string, number> = { high: 3, medium: 2, low: 1 };
      cmp = (order[a.confidence] ?? 0) - (order[b.confidence] ?? 0);
    }
    return sortAsc ? cmp : -cmp;
  });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="py-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <button
                onClick={() => toggleSort("name")}
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                Feature
                <ArrowUpDown className="size-3" />
              </button>
            </TableHead>
            <TableHead className="hidden md:table-cell">Description</TableHead>
            <TableHead>
              <button
                onClick={() => toggleSort("confidence")}
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                Confidence
                <ArrowUpDown className="size-3" />
              </button>
            </TableHead>
            <TableHead>
              <button
                onClick={() => toggleSort("rice_score")}
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                RICE Score
                <ArrowUpDown className="size-3" />
              </button>
            </TableHead>
            <TableHead className="hidden lg:table-cell">Category</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((feature, index) => (
            <TableRow key={index}>
              <TableCell className="font-medium">{feature.name}</TableCell>
              <TableCell className="hidden md:table-cell text-muted-foreground text-sm max-w-xs truncate">
                {feature.description}
              </TableCell>
              <TableCell>
                <ConfidenceBadge confidence={feature.confidence} />
              </TableCell>
              <TableCell className="font-mono text-orange-500">
                {feature.rice_score?.toFixed(1) ?? "—"}
              </TableCell>
              <TableCell className="hidden lg:table-cell text-muted-foreground text-sm">
                {feature.category ?? "—"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
