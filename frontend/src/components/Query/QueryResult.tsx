import { CheckCircle, FileText } from 'lucide-react';
import type { QueryResultProps } from '../../types';

const QueryResult = ({ result, onReset }: QueryResultProps) => {
  return (
    <div className="space-y-4">
      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
        <div className="flex items-center mb-2">
          <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
          <h3 className="text-lg font-semibold text-green-200">
            Answer
          </h3>
        </div>
        <p className="text-slate-100 whitespace-pre-wrap">
          {result.answer || '(No answer provided)'}
        </p>
      </div>

      {result.sources && result.sources.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <FileText className="h-5 w-5 text-slate-400 mr-2" />
            <h3 className="text-sm font-semibold text-slate-300">
              Sources ({result.sources.length})
            </h3>
          </div>
          <ul className="space-y-1">
            {result.sources.map((source, index) => (
              <li
                key={index}
                className="text-sm text-slate-300"
              >
                • {source}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.num_contexts && (
        <p className="text-xs text-slate-400">
          Used {result.num_contexts} context chunks
        </p>
      )}
    </div>
  );
};

export default QueryResult;

