"use client";

import { INTEGRATIONS, INTEGRATION_TYPE_LABELS } from "@/lib/constants";
import { IntegrationCard } from "./integration-card";

export function IntegrationGrid() {
  const grouped = INTEGRATIONS.reduce<Record<string, typeof INTEGRATIONS>>(
    (acc, integration) => {
      const type = integration.type;
      if (!acc[type]) acc[type] = [];
      acc[type].push(integration);
      return acc;
    },
    {}
  );

  return (
    <div className="space-y-8">
      {Object.entries(grouped).map(([type, integrations]) => (
        <div key={type} className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            {INTEGRATION_TYPE_LABELS[type] || type}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {integrations.map((integration) => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
