import { useCallback } from 'react';
import { useQuery as useReactQuery } from '@tanstack/react-query';
import { filesAPI, FilesResponse, ChunksResponse } from '../services/api';
import { useFilesStore } from '../stores/filesStore';
import type { UseFilesReturn } from '../types';

export const useFiles = (): UseFilesReturn => {
  const {
    selectedFiles,
    deleteConfirm,
    toggleFileSelection: toggleSelection,
    selectAll: selectAllFiles,
    deselectAll: deselectAllFiles,
    setDeleteConfirm: setDeleteConfirmState,
  } = useFilesStore();

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
    toggleSelection(sourceId);
  }, [toggleSelection]);

  const selectAll = useCallback((): void => {
    if (filesData?.files) {
      selectAllFiles(filesData.files.map((f) => f.source_id));
    }
  }, [filesData, selectAllFiles]);

  const deselectAll = useCallback((): void => {
    deselectAllFiles();
  }, [deselectAllFiles]);

  const deleteFiles = useCallback(async (sourceIds: string[]): Promise<any> => {
    try {
      const result = await filesAPI.deleteFiles(sourceIds);
      await refetch();
      deselectAllFiles();
      setDeleteConfirmState(false);
      return result;
    } catch (err) {
      throw err;
    }
  }, [refetch, deselectAllFiles, setDeleteConfirmState]);

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
    setDeleteConfirm: setDeleteConfirmState,
  };
};

export const useFileChunks = (sourceId: string, enabled: boolean = false) => {
  return useReactQuery<ChunksResponse>({
    queryKey: ['file-chunks', sourceId],
    queryFn: () => filesAPI.getFileChunks(sourceId, 20, 0),
    enabled: enabled && !!sourceId,
  });
};

