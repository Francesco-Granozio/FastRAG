import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { ChunkInfo } from '../../services/api';

interface ChunkViewerProps {
  sourceId: string;
  chunks: ChunkInfo[];
  total: number;
  loading: boolean;
}

const ChunkViewer = ({ sourceId, chunks, total, loading }: ChunkViewerProps) => {
  const [page, setPage] = useState<number>(1);
  const itemsPerPage = 20;
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const displayedChunks = chunks.slice(startIndex, endIndex);
  const totalPages = Math.ceil(chunks.length / itemsPerPage);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="animate-spin h-6 w-6 text-slate-400" />
      </div>
    );
  }

  return (
    <div className="mt-4 border-t border-slate-700 pt-4">
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-slate-300 mb-2">
          Chunks preview (showing {displayedChunks.length} of {chunks.length})
        </h4>
        {chunks.length === 20 && (
          <p className="text-xs text-slate-400">
            Showing first 20 chunks. Total chunks: {total}
          </p>
        )}
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {displayedChunks.map((chunk, index) => (
          <div
            key={chunk.id}
            className="bg-slate-900 border border-slate-700 rounded-lg p-4"
          >
            <div className="mb-2">
              <p className="text-xs font-mono text-slate-400">
                Chunk {startIndex + index + 1} (ID: {chunk.id.substring(0, 20)}...)
              </p>
            </div>
            <div className="bg-slate-800 rounded p-4 border border-slate-700">
              <p className="text-base text-slate-100 leading-relaxed whitespace-pre-wrap font-sans">
                {chunk.text}
              </p>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 text-sm font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-slate-400">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1 text-sm font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ChunkViewer;

