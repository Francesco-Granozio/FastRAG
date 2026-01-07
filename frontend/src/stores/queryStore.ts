import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { QueryStatus } from '../types';

interface QueryState {
  question: string;
  topK: number;
  result: QueryStatus['result'] | null;
  progress: {
    status: string;
    message: string;
    eventId?: string;
  } | null;
  error: string | null;
  loading: boolean;
}

interface QueryActions {
  setQuestion: (question: string) => void;
  setTopK: (topK: number) => void;
  setResult: (result: QueryStatus['result'] | null) => void;
  setProgress: (progress: {
    status: string;
    message: string;
    eventId?: string;
  } | null) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;
}

type QueryStore = QueryState & QueryActions;

const initialState: QueryState = {
  question: '',
  topK: 5,
  result: null,
  progress: null,
  error: null,
  loading: false,
};

export const useQueryStore = create<QueryStore>()(
  persist(
    (set) => ({
      ...initialState,
      setQuestion: (question) => set({ question }),
      setTopK: (topK) => set({ topK }),
      setResult: (result) => set({ result }),
      setProgress: (progress) => set({ progress }),
      setError: (error) => set({ error }),
      setLoading: (loading) => set({ loading }),
      reset: () => set(initialState),
    }),
    {
      name: 'rag-query-store',
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


