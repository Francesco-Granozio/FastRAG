import { useState, useCallback } from 'react';
import { queryAPI, pollUntilComplete, QueryStatus } from '../services/api';

interface UseQueryReturn {
  submitQuery: (question: string, topK?: number) => Promise<void>;
  loading: boolean;
  error: string | null;
  result: QueryStatus['result'] | null;
  progress: {
    status: string;
    message: string;
    eventId?: string;
  } | null;
  reset: () => void;
}

export const useQuery = (): UseQueryReturn => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryStatus['result'] | null>(null);
  const [progress, setProgress] = useState<{
    status: string;
    message: string;
    eventId?: string;
  } | null>(null);

  const submitQuery = useCallback(async (question: string, topK: number = 5): Promise<void> => {
    setLoading(true);
    setError(null);
    setResult(null);
    setProgress({ status: 'submitting', message: 'Submitting query...' });

    try {
      // Submit query
      const { event_id } = await queryAPI.submitQuery(question, topK);
      setProgress({ status: 'running', message: 'Processing query...', eventId: event_id });

      // Poll for result
      const finalStatus = await pollUntilComplete(
        () => queryAPI.getQueryStatus(event_id),
        (status) => {
          if (status.status === 'running') {
            setProgress({
              status: 'running',
              message: 'Processing query...',
              eventId: event_id,
            });
          }
        },
        {
          interval: 2000,
          timeout: 600000, // 10 minutes
        }
      );

      if (finalStatus.status === 'completed' && finalStatus.result) {
        setResult(finalStatus.result);
        setProgress(null);
      } else {
        throw new Error(finalStatus.error || 'Query failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setProgress(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback((): void => {
    setLoading(false);
    setError(null);
    setResult(null);
    setProgress(null);
  }, []);

  return {
    submitQuery,
    loading,
    error,
    result,
    progress,
    reset,
  };
};

