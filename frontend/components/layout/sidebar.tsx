"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Brain,
  FileText,
  Plug,
  Clock,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS } from "@/lib/constants";
import { useHealth } from "@/lib/hooks/use-health";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard,
  Brain,
  FileText,
  Plug,
  Clock,
};

export function Sidebar() {
  const pathname = usePathname();
  const { isOnline } = useHealth();

  return (
    <aside className="hidden md:flex w-60 flex-col border-r border-border bg-card h-screen sticky top-0">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 h-14 border-b border-border">
        <div className="size-8 bg-orange-500 flex items-center justify-center">
          <Zap className="size-5 text-white" />
        </div>
        <span className="font-semibold text-lg tracking-tight">Squash</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = ICONS[item.icon];
          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-orange-500/10 text-orange-500 border-l-2 border-orange-500"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent border-l-2 border-transparent"
              )}
            >
              {Icon && <Icon className="size-4" />}
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Health indicator */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div
            className={cn(
              "size-2 rounded-full",
              isOnline ? "bg-green-500" : "bg-red-500"
            )}
          />
          <span>Backend {isOnline ? "Connected" : "Offline"}</span>
        </div>
      </div>
    </aside>
  );
}
