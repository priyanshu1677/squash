"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  onUpload: (files: File[]) => void;
  isUploading: boolean;
}

export function FileUploadZone({ onUpload, isUploading }: FileUploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onUpload(acceptedFiles);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/msword": [".doc"],
    },
    disabled: isUploading,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed p-12 text-center cursor-pointer transition-colors",
        isDragActive
          ? "border-orange-500 bg-orange-500/5"
          : "border-border hover:border-orange-500/50",
        isUploading && "opacity-50 cursor-not-allowed"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        {isDragActive ? (
          <FileText className="size-10 text-orange-500" />
        ) : (
          <Upload className="size-10 text-muted-foreground" />
        )}
        <div>
          <p className="text-sm font-medium">
            {isDragActive
              ? "Drop files here..."
              : isUploading
              ? "Uploading..."
              : "Drag & drop files here, or click to select"}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Supports PDF and DOCX files
          </p>
        </div>
      </div>
    </div>
  );
}
