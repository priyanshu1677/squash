import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Integration } from "@/lib/types";

export function IntegrationCard({
  integration,
}: {
  integration: Integration;
}) {
  return (
    <Card className="py-4">
      <CardHeader className="pb-0">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="size-10 bg-muted flex items-center justify-center text-sm font-bold text-muted-foreground">
              {integration.name.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <CardTitle className="text-sm">{integration.name}</CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">
                {integration.description}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="size-2 rounded-full bg-yellow-500" />
            <span className="text-xs text-muted-foreground">Mock</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-3">
        <div className="flex flex-wrap gap-1.5 mb-3">
          {integration.capabilities.map((cap) => (
            <Badge
              key={cap}
              variant="outline"
              className="rounded-none text-[10px] text-muted-foreground"
            >
              {cap.replace(/_/g, " ")}
            </Badge>
          ))}
        </div>
        <Button variant="orange" size="sm" className="w-full" disabled>
          Configure
        </Button>
      </CardContent>
    </Card>
  );
}
