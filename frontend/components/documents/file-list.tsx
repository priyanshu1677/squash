"use client";

import { FileText } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { FileInfo } from "@/lib/types";
import {
  formatBytes,
  formatRelativeTime,
  getFileTypeColor,
  getFileTypeLabel,
} from "@/lib/utils";

export function FileList({ files }: { files: FileInfo[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Modified</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {files.map((file) => (
          <TableRow key={file.name}>
            <TableCell>
              <div className="flex items-center gap-2">
                <FileText className="size-4 text-muted-foreground shrink-0" />
                <span className="font-medium truncate">{file.name}</span>
              </div>
            </TableCell>
            <TableCell>
              <Badge
                variant="outline"
                className={`rounded-none text-xs ${getFileTypeColor(file.name)}`}
              >
                {getFileTypeLabel(file.name)}
              </Badge>
            </TableCell>
            <TableCell className="text-muted-foreground font-mono text-sm">
              {formatBytes(file.size)}
            </TableCell>
            <TableCell className="text-muted-foreground text-sm">
              {formatRelativeTime(file.modified)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
