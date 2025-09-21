'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Wifi, WifiOff } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  type?: 'network' | 'server' | 'validation' | 'generic';
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title,
  message,
  type = 'generic',
  onRetry,
  className,
}: ErrorStateProps) {
  const getErrorConfig = () => {
    switch (type) {
      case 'network':
        return {
          icon: <WifiOff className="w-12 h-12 text-rose-400/60" />,
          title: title || 'Connection Error',
          message: message || 'Unable to connect to the server. Please check your internet connection and try again.',
          bgColor: 'bg-rose-400/10',
          borderColor: 'border-rose-300/20',
        };
      case 'server':
        return {
          icon: <AlertTriangle className="w-12 h-12 text-amber-400/60" />,
          title: title || 'Server Error',
          message: message || 'The server encountered an error. Please try again in a few moments.',
          bgColor: 'bg-amber-400/10',
          borderColor: 'border-amber-300/20',
        };
      case 'validation':
        return {
          icon: <AlertTriangle className="w-12 h-12 text-blue-400/60" />,
          title: title || 'Validation Error',
          message: message || 'Please check your input and try again.',
          bgColor: 'bg-blue-400/10',
          borderColor: 'border-blue-300/20',
        };
      default:
        return {
          icon: <AlertTriangle className="w-12 h-12 text-white/40" />,
          title: title || 'Something went wrong',
          message: message || 'An unexpected error occurred. Please try again.',
          bgColor: 'bg-white/5',
          borderColor: 'border-white/10',
        };
    }
  };

  const config = getErrorConfig();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`flex flex-col items-center justify-center py-12 px-6 text-center ${className}`}
    >
      <div className={`mb-6 p-4 rounded-2xl ${config.bgColor} border ${config.borderColor}`}>
        {config.icon}
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-2">
        {config.title}
      </h3>
      
      <p className="text-white/70 max-w-md mb-6 leading-relaxed">
        {config.message}
      </p>
      
      {onRetry && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onRetry}
          className="inline-flex items-center space-x-2 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 rounded-xl text-white font-medium transition-all duration-200 backdrop-blur-sm"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </motion.button>
      )}
    </motion.div>
  );
}
