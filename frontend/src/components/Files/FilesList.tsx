import { useState } from 'react';
import { useFiles } from '../../hooks/useFiles';
import FileCard from './FileCard';
import { Trash2, CheckSquare, Square, Loader2, AlertCircle } from 'lucide-react';

const FilesList = () => {
  const {
    files,
    totalFiles,
    totalChunks,
    isLoading,
    error,
    selectedFiles,
    toggleFileSelection,
    selectAll,
    deselectAll,
    deleteFiles,
    deleteConfirm,
    setDeleteConfirm,
  } = useFiles();

  const [deleting, setDeleting] = useState<boolean>(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleDelete = async (): Promise<void> => {
    if (selectedFiles.size === 0) return;

    setDeleting(true);
    setDeleteError(null);

    try {
      const result = await deleteFiles(Array.from(selectedFiles));
      // Controlla se ci sono errori nell'array errors
      if (result.errors && Array.isArray(result.errors) && result.errors.length > 0) {
        const failedFiles = result.errors.map((e: any) => e.source_id || e).join(', ');
        setDeleteError(`Some files failed to delete: ${failedFiles}`);
      } else if (result.total_errors && result.total_errors > 0) {
        // Fallback: controlla total_errors se presente
        setDeleteError(`Some files failed to delete. Check console for details.`);
      }
      // Se non ci sono errori, la cancellazione è riuscita
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Unknown error occurred while deleting files');
    } finally {
      setDeleting(false);
    }
  };

  const avgChunks = totalFiles > 0 ? (totalChunks / totalFiles).toFixed(1) : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin h-8 w-8 text-slate-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-400 mr-3" />
          <p className="text-sm font-medium text-red-200">
            Error loading files: {error.message}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">
          Embedded Files
        </h2>
        <p className="mt-1 text-sm text-slate-300">
          View and manage files that have been embedded in the vector database
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <p className="text-sm font-medium text-slate-300">
            Total Files
          </p>
          <p className="text-2xl font-bold text-slate-100">
            {totalFiles}
          </p>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <p className="text-sm font-medium text-slate-300">
            Total Chunks
          </p>
          <p className="text-2xl font-bold text-slate-100">
            {totalChunks}
          </p>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <p className="text-sm font-medium text-slate-300">
            Avg Chunks/File
          </p>
          <p className="text-2xl font-bold text-slate-100">
            {avgChunks}
          </p>
        </div>
      </div>

      {totalFiles === 0 ? (
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-6 text-center">
          <p className="text-sm text-blue-200">
            No files have been embedded yet. Upload a PDF in the 'Upload & Query' page to get started.
          </p>
        </div>
      ) : (
        <>
          {/* Bulk Actions */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={selectAll}
                  className="flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700 rounded-lg"
                >
                  <CheckSquare className="h-4 w-4 mr-2" />
                  Select All
                </button>
                <button
                  onClick={deselectAll}
                  className="flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700 rounded-lg"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Deselect All
                </button>
              </div>
              {selectedFiles.size > 0 && (
                <button
                  onClick={() => setDeleteConfirm(true)}
                  disabled={deleting}
                  className="flex items-center px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Selected ({selectedFiles.size})
                </button>
              )}
            </div>
          </div>

          {/* Delete Confirmation */}
          {deleteConfirm && (
            <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4">
              <p className="text-sm font-medium text-yellow-200 mb-4">
                ⚠️ Are you sure you want to delete {selectedFiles.size} file(s)? This action cannot be undone.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50"
                >
                  {deleting ? 'Deleting...' : 'Confirm Delete'}
                </button>
                <button
                  onClick={() => {
                    setDeleteConfirm(false);
                    setDeleteError(null);
                  }}
                  className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 rounded-lg"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {deleteError && (
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
              <p className="text-sm font-medium text-red-200">
                {deleteError}
              </p>
            </div>
          )}

          {/* Files List */}
          <div className="space-y-2">
            {files.map((file) => (
              <FileCard
                key={file.source_id}
                file={file}
                isSelected={selectedFiles.has(file.source_id)}
                onToggleSelect={() => toggleFileSelection(file.source_id)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default FilesList;

