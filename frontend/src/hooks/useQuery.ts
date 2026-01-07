import { useCallback } from 'react';
import { queryAPI, pollUntilComplete } from '../services/api';
import { useQueryStore } from '../stores/queryStore';
import type { UseQueryReturn } from '../types';

export const useQuery = (): UseQueryReturn => {
  const {
    loading,
    error,
    result,
    progress,
    setLoading,
    setError,
    setResult,
    setProgress,
    reset: resetStore,
  } = useQueryStore();

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
  }, [setLoading, setError, setResult, setProgress]);

  const reset = useCallback((): void => {
    resetStore();
  }, [resetStore]);

  return {
    submitQuery,
    loading,
    error,
    result,
    progress,
    reset,
  };
};

