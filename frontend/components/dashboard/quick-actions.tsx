"use client";

import Link from "next/link";
import { Brain, FileText, Plug } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const ACTIONS = [
  {
    href: "/analysis",
    label: "Run Analysis",
    description: "Analyze customer data and discover features",
    icon: Brain,
  },
  {
    href: "/documents",
    label: "Upload Documents",
    description: "Upload interview transcripts and reports",
    icon: FileText,
  },
  {
    href: "/integrations",
    label: "View Integrations",
    description: "Connect analytics, support, and PM tools",
    icon: Plug,
  },
];

export function QuickActions() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {ACTIONS.map((action) => (
        <Link key={action.href} href={action.href}>
          <Card className="py-4 border-2 border-transparent hover:border-orange-500 transition-colors cursor-pointer group h-full">
            <CardContent className="flex flex-col gap-3">
              <div className="size-10 bg-orange-500/10 flex items-center justify-center group-hover:bg-orange-500/20 transition-colors">
                <action.icon className="size-5 text-orange-500" />
              </div>
              <div>
                <p className="text-sm font-medium group-hover:text-orange-500 transition-colors">
                  {action.label}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {action.description}
                </p>
              </div>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
