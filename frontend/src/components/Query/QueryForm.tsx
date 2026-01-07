import { FormEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useQuery } from '../../hooks/useQuery';
import { useQueryStore } from '../../stores/queryStore';
import QueryResult from './QueryResult';

const QueryForm = () => {
  const { question, topK, setQuestion, setTopK } = useQueryStore();
  const { submitQuery, loading, error, result, progress, reset } = useQuery();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!question.trim()) return;
    await submitQuery(question.trim(), topK);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">
          Ask a question about your PDFs
        </h2>
        <p className="mt-1 text-sm text-slate-300">
          Query your embedded documents using the LLM
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="question"
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            Your question
          </label>
          <textarea
            id="question"
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full px-4 py-2 border border-slate-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-slate-800 text-slate-100 placeholder-slate-400"
            placeholder="Enter your question here..."
            disabled={loading}
          />
        </div>

        <div>
          <label
            htmlFor="top_k"
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            Number of chunks to retrieve
          </label>
          <input
            type="number"
            id="top_k"
            min={1}
            max={20}
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value) || 5)}
            className="max-w-xs w-full px-4 py-2 border border-slate-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-slate-800 text-slate-100"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="max-w-xs w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Processing...
            </>
          ) : (
            <>
              <Send className="h-5 w-5 mr-2" />
              Ask
            </>
          )}
        </button>
      </form>

      {progress && (
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
          <div className="flex items-center">
            <Loader2 className="animate-spin h-5 w-5 text-blue-400 mr-3" />
            <p className="text-sm font-medium text-blue-200">
              {progress.message}
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <p className="text-sm font-medium text-red-200">
            {error}
          </p>
        </div>
      )}

      {result && (
        <QueryResult result={result} onReset={reset} />
      )}
    </div>
  );
};

export default QueryForm;

