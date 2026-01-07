import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UploadStatusState } from '../types';

interface UploadState {
  uploadStatus: UploadStatusState | null;
  error: string | null;
  uploading: boolean;
}

interface UploadActions {
  setUploadStatus: (uploadStatus: UploadStatusState | null) => void;
  setError: (error: string | null) => void;
  setUploading: (uploading: boolean) => void;
  reset: () => void;
}

type UploadStore = UploadState & UploadActions;

const initialState: UploadState = {
  uploadStatus: null,
  error: null,
  uploading: false,
};

export const useUploadStore = create<UploadStore>()(
  persist(
    (set) => ({
      ...initialState,
      setUploadStatus: (uploadStatus) => set({ uploadStatus }),
      setError: (error) => set({ error }),
      setUploading: (uploading) => set({ uploading }),
      reset: () => set(initialState),
    }),
    {
      name: 'rag-upload-store',
      // Only persist completed status and errors, not uploading/processing states
      partialize: (state) => ({
        uploadStatus: state.uploadStatus?.status === 'completed' ? state.uploadStatus : null,
        error: state.error,
        uploading: false, // Always reset uploading to false on persist
      }),
      storage: {
        getItem: (name) => {
          const str = sessionStorage.getItem(name);
          if (!str) return null;
          return JSON.parse(str);
        },
        setItem: (name, value) => {
          sessionStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name) => {
          sessionStorage.removeItem(name);
        },
      },
    }
  )
);


