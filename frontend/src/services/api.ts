import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request made but no response
      return Promise.reject(new Error('Network error. Please check your connection.'));
    } else {
      // Something else happened
      return Promise.reject(error);
    }
  }
);

// Types
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
}

// Upload API
export const uploadAPI = {
  uploadPDF: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getUploadStatus: async (eventId: string): Promise<UploadStatus> => {
    const response = await api.get<UploadStatus>(`/api/upload/status/${eventId}`);
    return response.data;
  },
};

// Query API
export const queryAPI = {
  submitQuery: async (question: string, topK: number = 5): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/api/query', {
      question,
      top_k: topK,
    });
    return response.data;
  },

  getQueryStatus: async (eventId: string): Promise<QueryStatus> => {
    const response = await api.get<QueryStatus>(`/api/query/status/${eventId}`);
    return response.data;
  },
};

// Files API
export const filesAPI = {
  getAllFiles: async (): Promise<FilesResponse> => {
    const response = await api.get<FilesResponse>('/api/files');
    return response.data;
  },

  getFileChunks: async (sourceId: string, limit: number = 20, offset: number = 0): Promise<ChunksResponse> => {
    const response = await api.get<ChunksResponse>(`/api/files/${sourceId}/chunks`, {
      params: { limit, offset },
    });
    return response.data;
  },

  deleteFile: async (sourceId: string): Promise<DeleteFileResponse> => {
    const response = await api.delete<DeleteFileResponse>(`/api/files/${sourceId}`);
    return response.data;
  },

  deleteFiles: async (sourceIds: string[]): Promise<DeleteFilesResponse> => {
    const response = await api.delete<DeleteFilesResponse>('/api/files', {
      data: { source_ids: sourceIds },
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },
};

// Polling utility
export interface PollOptions {
  interval?: number;
  timeout?: number;
  maxAttempts?: number | null;
}

export const pollUntilComplete = async (
  checkStatus: () => Promise<QueryStatus | UploadStatus>,
  onProgress?: (status: QueryStatus | UploadStatus) => void,
  options: PollOptions = {}
): Promise<QueryStatus | UploadStatus> => {
  const {
    interval = 2000,
    timeout = 600000, // 10 minutes
    maxAttempts = null,
  } = options;

  const startTime = Date.now();
  let attempts = 0;

  while (true) {
    const status = await checkStatus();
    
    if (onProgress) {
      onProgress(status);
    }

    // Check for completion (handle both QueryStatus and UploadStatus)
    const statusValue = typeof status.status === 'string' ? status.status : '';
    const statusLower = statusValue.toLowerCase();
    
    if (statusLower === 'completed' || statusLower === 'finished' || statusValue === 'Completed' || statusValue === 'Finished') {
      return status;
    }

    // Check for failure
    if (statusLower === 'failed' || statusLower === 'error' || statusValue === 'Failed') {
      const queryStatus = status as QueryStatus;
      throw new Error(queryStatus.error || 'Operation failed');
    }

    attempts++;
    if (maxAttempts && attempts >= maxAttempts) {
      throw new Error('Maximum polling attempts reached');
    }

    if (Date.now() - startTime > timeout) {
      throw new Error('Polling timeout');
    }

    await new Promise((resolve) => setTimeout(resolve, interval));
  }
};

export default api;

