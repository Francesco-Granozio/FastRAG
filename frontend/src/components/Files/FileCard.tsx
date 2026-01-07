import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, Eye } from 'lucide-react';
import { useFileChunks } from '../../hooks/useFiles';
import ChunkViewer from './ChunkViewer';
import type { FileCardProps } from '../../types';

const FileCard = ({ file, isSelected, onToggleSelect }: FileCardProps) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [showChunks, setShowChunks] = useState<boolean>(false);
  const { data: chunksData, isLoading: chunksLoading } = useFileChunks(
    file.source_id,
    showChunks
  );

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
      <div className="p-4">
        <div className="flex items-start">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggleSelect}
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-600 rounded bg-slate-700"
          />
          <div className="flex-1 ml-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-slate-400 mr-2" />
                <h3 className="text-lg font-medium text-slate-100">
                  {file.source_id}
                </h3>
                <span className="ml-3 px-2 py-1 text-xs font-medium bg-slate-700 text-slate-300 rounded">
                  {file.chunk_count} chunks
                </span>
              </div>
              <button
                onClick={() => setExpanded(!expanded)}
                className="p-1 text-slate-400 hover:text-slate-200"
              >
                {expanded ? (
                  <ChevronUp className="h-5 w-5" />
                ) : (
                  <ChevronDown className="h-5 w-5" />
                )}
              </button>
            </div>

            {expanded && (
              <div className="mt-4 space-y-3">
                <div className="text-sm text-slate-300">
                  <p>
                    <span className="font-medium">Source ID:</span> {file.source_id}
                  </p>
                  <p>
                    <span className="font-medium">Number of chunks:</span>{' '}
                    {file.chunk_count}
                  </p>
                </div>

                <button
                  onClick={() => setShowChunks(!showChunks)}
                  className="flex items-center px-3 py-2 text-sm font-medium text-blue-400 hover:bg-blue-900/30 rounded-lg"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  {showChunks ? 'Hide Chunks' : 'View Chunks'}
                </button>

                {showChunks && (
                  <ChunkViewer
                    sourceId={file.source_id}
                    chunks={chunksData?.chunks || []}
                    total={chunksData?.total || file.chunk_count}
                    loading={chunksLoading}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileCard;

