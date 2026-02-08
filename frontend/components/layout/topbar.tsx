"use client";

import { usePathname } from "next/navigation";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./theme-toggle";
import { MobileNav } from "./mobile-nav";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/analysis": "Analysis",
  "/documents": "Documents",
  "/integrations": "Integrations",
  "/history": "History",
};

export function Topbar({
  onOpenCommandPalette,
}: {
  onOpenCommandPalette: () => void;
}) {
  const pathname = usePathname();
  const title = PAGE_TITLES[pathname] || "Squash";

  return (
    <header className="h-14 border-b border-border bg-card/80 backdrop-blur-sm flex items-center justify-between px-4 md:px-6 sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <MobileNav />
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">Squash</span>
          <span className="text-muted-foreground">/</span>
          <span className="font-medium">{title}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onOpenCommandPalette}
          className="hidden sm:flex items-center gap-2 text-muted-foreground"
        >
          <Search className="size-3.5" />
          <span className="text-xs">Search...</span>
          <kbd className="ml-2 pointer-events-none inline-flex h-5 items-center gap-0.5 rounded border border-border bg-muted px-1.5 font-mono text-[10px] text-muted-foreground">
            <span className="text-xs">⌘</span>K
          </kbd>
        </Button>
        <ThemeToggle />
      </div>
    </header>
  );
}
