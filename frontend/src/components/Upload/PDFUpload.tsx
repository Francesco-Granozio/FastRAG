import { useState, useCallback, DragEvent, ChangeEvent } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadAPI, pollUntilComplete, UploadStatus } from '../../services/api';
import type { UploadStatusState } from '../../types';

const PDFUpload = () => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatusState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    async (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        await handleFile(e.dataTransfer.files[0]);
      }
    },
    []
  );

  const handleFileInput = useCallback(async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFile(e.target.files[0]);
    }
  }, []);

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files are allowed');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadStatus({ status: 'uploading', message: 'Uploading file...' });

    try {
      // Upload file
      const uploadResult = await uploadAPI.uploadPDF(file);
      setUploadStatus({
        status: 'processing',
        message: 'Processing file...',
        eventId: uploadResult.event_id,
      });

      // Poll for completion
      await pollUntilComplete(
        () => uploadAPI.getUploadStatus(uploadResult.event_id),
        (status) => {
          const uploadStatus = status as UploadStatus;
          setUploadStatus({
            status: uploadStatus.status.toLowerCase(),
            message: uploadStatus.status === 'Running' ? 'Processing file...' : 'Upload complete',
            eventId: uploadResult.event_id,
          });
        },
        {
          interval: 2000,
          timeout: 300000, // 5 minutes
        }
      );

      setUploadStatus({
        status: 'completed',
        message: 'File uploaded and processed successfully!',
        filename: file.name,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setUploadStatus(null);
    } finally {
      setUploading(false);
    }
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">
          Upload a PDF to Ingest
        </h2>
        <p className="mt-1 text-sm text-slate-300">
          Upload a PDF file to be processed and embedded in the vector database
        </p>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-900/30'
            : 'border-slate-600 hover:border-blue-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        <div className="space-y-4">
          <Upload className="mx-auto h-12 w-12 text-slate-400" />
          <div>
            <p className="text-lg font-medium text-slate-100">
              Drag and drop a PDF file here
            </p>
            <p className="mt-1 text-sm text-slate-300">
              or click to browse
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Limit 200MB per file • PDF only
            </p>
          </div>
        </div>
      </div>

      {uploading && uploadStatus && (
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
          <div className="flex items-center">
            <Loader2 className="animate-spin h-5 w-5 text-blue-400 mr-3" />
            <p className="text-sm font-medium text-blue-200">
              {uploadStatus.message}
            </p>
          </div>
        </div>
      )}

      {uploadStatus?.status === 'completed' && (
        <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-400 mr-3" />
            <div>
              <p className="text-sm font-medium text-green-200">
                {uploadStatus.message}
              </p>
              {uploadStatus.filename && (
                <p className="text-xs text-green-300 mt-1">
                  {uploadStatus.filename}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3" />
            <p className="text-sm font-medium text-red-200">
              {error}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PDFUpload;

