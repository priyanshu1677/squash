"use client";

import { useState } from "react";
import { toast } from "sonner";
import { PageHeader } from "@/components/shared/page-header";
import { FileUploadZone } from "@/components/documents/file-upload-zone";
import { FileList } from "@/components/documents/file-list";
import { EmptyDocuments } from "@/components/documents/empty-documents";
import { useFiles } from "@/lib/hooks/use-files";
import { uploadFile } from "@/lib/api-client";
import { Skeleton } from "@/components/ui/skeleton";

export default function DocumentsPage() {
  const { files, loading, refetch } = useFiles();
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (uploadFiles: File[]) => {
    setIsUploading(true);
    let successCount = 0;

    for (const file of uploadFiles) {
      try {
        await uploadFile(file);
        successCount++;
      } catch (err) {
        toast.error(
          `Failed to upload ${file.name}: ${
            err instanceof Error ? err.message : "Unknown error"
          }`
        );
      }
    }

    if (successCount > 0) {
      toast.success(
        `${successCount} file${successCount > 1 ? "s" : ""} uploaded`
      );
      refetch();
    }

    setIsUploading(false);
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Documents"
        description="Upload and manage customer interview transcripts and reports"
      />

      <FileUploadZone onUpload={handleUpload} isUploading={isUploading} />

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-12 w-full rounded-none" />
          ))}
        </div>
      ) : files.length > 0 ? (
        <FileList files={files} />
      ) : (
        <EmptyDocuments />
      )}
    </div>
  );
}
