import type { LucideIcon } from 'lucide-react';

// ============================================================================
// API Types
// ============================================================================

export interface UploadResponse {
  message: string;
  filename: string;
  event_id: string;
}

export interface UploadStatus {
  event_id: string;
  status: string;
  run?: {
    status?: string;
    output?: any;
    error?: string;
  } | null;
}

export interface QueryRequest {
  question: string;
  top_k: number;
}

export interface QueryResponse {
  event_id: string;
  status: string;
  message: string;
}

export interface QueryStatus {
  event_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: {
    answer: string;
    sources: string[];
    num_contexts: number;
  };
  error?: string;
}

export interface FileInfo {
  source_id: string;
  chunk_count: number;
}

export interface FilesResponse {
  files: FileInfo[];
  total_files: number;
  total_chunks: number;
}

export interface ChunkInfo {
  id: string;
  text: string;
  source: string;
}

export interface ChunksResponse {
  chunks: ChunkInfo[];
  total: number;
}

export interface DeleteFileResponse {
  message: string;
  source_id: string;
  chunks_deleted: number;
}

export interface DeleteFilesResponse {
  deleted: Array<{
    source_id: string;
    chunks_deleted: number;
    status: string;
  }>;
  errors: Array<{
    source_id: string;
    error: string;
    status: string;
  }>;
  total_deleted: number;
  total_errors: number;
  message?: string;
}

export interface PollOptions {
  interval?: number;
  timeout?: number;
  maxAttempts?: number | null;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
}

export interface QueryResultProps {
  result: {
    answer: string;
    sources?: string[];
    num_contexts?: number;
  };
  onReset: () => void;
}

export interface ChunkViewerProps {
  sourceId: string;
  chunks: ChunkInfo[];
  total: number;
  loading: boolean;
}

export interface FileCardProps {
  file: {
    source_id: string;
    chunk_count: number;
  };
  isSelected: boolean;
  onToggleSelect: () => void;
}

export interface UploadStatusState {
  status: string;
  message: string;
  eventId?: string;
  filename?: string;
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseQueryReturn {
  submitQuery: (question: string, topK?: number) => Promise<void>;
  loading: boolean;
  error: string | null;
  result: QueryStatus['result'] | null;
  progress: {
    status: string;
    message: string;
    eventId?: string;
  } | null;
  reset: () => void;
}

export interface UseFilesReturn {
  files: Array<{ source_id: string; chunk_count: number }>;
  totalFiles: number;
  totalChunks: number;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
  selectedFiles: Set<string>;
  toggleFileSelection: (sourceId: string) => void;
  selectAll: () => void;
  deselectAll: () => void;
  deleteFiles: (sourceIds: string[]) => Promise<any>;
  deleteFile: (sourceId: string) => Promise<boolean>;
  deleteConfirm: boolean;
  setDeleteConfirm: (value: boolean) => void;
}

