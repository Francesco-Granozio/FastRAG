import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import type { ToastType } from '../../hooks/useToast';

interface ToastProps {
  message: string;
  type: ToastType;
  onClose: () => void;
}

const Toast = ({ message, type, onClose }: ToastProps) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-400" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-900/30 border-green-700 text-green-200';
      case 'error':
        return 'bg-red-900/30 border-red-700 text-red-200';
      case 'info':
        return 'bg-blue-900/30 border-blue-700 text-blue-200';
    }
  };

  return (
    <div
      className={`${getStyles()} border rounded-lg p-4 shadow-lg min-w-[300px] max-w-md transform transition-all duration-300 ease-in-out translate-x-0 opacity-100`}
      role="alert"
      style={{
        animation: 'slideInRight 0.3s ease-out',
      }}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0 mr-3">
          {getIcon()}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 ml-3 text-slate-400 hover:text-slate-200 transition-colors"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default Toast;

