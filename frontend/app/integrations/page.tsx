import { PageHeader } from "@/components/shared/page-header";
import { IntegrationGrid } from "@/components/integrations/integration-grid";

export default function IntegrationsPage() {
  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Integrations"
        description="Connect your analytics, support, sales, and project management tools"
      />
      <IntegrationGrid />
    </div>
  );
}
