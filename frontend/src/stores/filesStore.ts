import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface FilesState {
  selectedFiles: Set<string>;
  deleteConfirm: boolean;
}

interface FilesActions {
  toggleFileSelection: (sourceId: string) => void;
  selectAll: (fileIds: string[]) => void;
  deselectAll: () => void;
  setDeleteConfirm: (value: boolean) => void;
  reset: () => void;
}

type FilesStore = FilesState & FilesActions;

const initialState: FilesState = {
  selectedFiles: new Set<string>(),
  deleteConfirm: false,
};

export const useFilesStore = create<FilesStore>()(
  persist(
    (set) => ({
      ...initialState,
      toggleFileSelection: (sourceId) =>
        set((state) => {
          const newSet = new Set(state.selectedFiles);
          if (newSet.has(sourceId)) {
            newSet.delete(sourceId);
          } else {
            newSet.add(sourceId);
          }
          return { selectedFiles: newSet };
        }),
      selectAll: (fileIds) =>
        set({ selectedFiles: new Set(fileIds) }),
      deselectAll: () =>
        set({ selectedFiles: new Set<string>() }),
      setDeleteConfirm: (value) =>
        set({ deleteConfirm: value }),
      reset: () => set(initialState),
    }),
    {
      name: 'rag-files-store',
      partialize: (state) => ({
        selectedFiles: Array.from(state.selectedFiles),
        deleteConfirm: state.deleteConfirm,
      }),
      storage: {
        getItem: (name) => {
          const str = sessionStorage.getItem(name);
          if (!str) return null;
          const parsed = JSON.parse(str);
          // Converti array di selectedFiles in Set durante il rehydrate
          if (parsed?.state?.selectedFiles && Array.isArray(parsed.state.selectedFiles)) {
            parsed.state.selectedFiles = new Set(parsed.state.selectedFiles);
          }
          return parsed;
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

