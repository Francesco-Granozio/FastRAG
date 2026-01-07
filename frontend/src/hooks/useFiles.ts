import { useState, useCallback } from 'react';
import { useQuery as useReactQuery } from '@tanstack/react-query';
import { filesAPI, FilesResponse, ChunksResponse } from '../services/api';
import type { UseFilesReturn } from '../types';

export const useFiles = (): UseFilesReturn => {
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [deleteConfirm, setDeleteConfirm] = useState<boolean>(false);

  // Fetch all files with React Query
  const {
    data: filesData,
    isLoading,
    error,
    refetch,
  } = useReactQuery<FilesResponse>({
    queryKey: ['files'],
    queryFn: () => filesAPI.getAllFiles(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const toggleFileSelection = useCallback((sourceId: string): void => {
    setSelectedFiles((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(sourceId)) {
        newSet.delete(sourceId);
      } else {
        newSet.add(sourceId);
      }
      return newSet;
    });
  }, []);

  const selectAll = useCallback((): void => {
    if (filesData?.files) {
      setSelectedFiles(new Set(filesData.files.map((f) => f.source_id)));
    }
  }, [filesData]);

  const deselectAll = useCallback((): void => {
    setSelectedFiles(new Set());
  }, []);

  const deleteFiles = useCallback(async (sourceIds: string[]): Promise<any> => {
    try {
      const result = await filesAPI.deleteFiles(sourceIds);
      await refetch();
      setSelectedFiles(new Set());
      setDeleteConfirm(false);
      return result;
    } catch (err) {
      throw err;
    }
  }, [refetch]);

  const deleteFile = useCallback(
    async (sourceId: string): Promise<boolean> => {
      try {
        await filesAPI.deleteFile(sourceId);
        await refetch();
        return true;
      } catch (err) {
        throw err;
      }
    },
    [refetch]
  );

  return {
    files: filesData?.files || [],
    totalFiles: filesData?.total_files || 0,
    totalChunks: filesData?.total_chunks || 0,
    isLoading,
    error: error as Error | null,
    refetch,
    selectedFiles,
    toggleFileSelection,
    selectAll,
    deselectAll,
    deleteFiles,
    deleteFile,
    deleteConfirm,
    setDeleteConfirm,
  };
};

export const useFileChunks = (sourceId: string, enabled: boolean = false) => {
  return useReactQuery<ChunksResponse>({
    queryKey: ['file-chunks', sourceId],
    queryFn: () => filesAPI.getFileChunks(sourceId, 20, 0),
    enabled: enabled && !!sourceId,
  });
};

