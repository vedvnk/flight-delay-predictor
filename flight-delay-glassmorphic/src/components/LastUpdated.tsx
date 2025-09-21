'use client';

import { motion } from 'framer-motion';
import { RefreshCw, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface LastUpdatedProps {
  lastUpdated: Date | null;
  isRefreshing?: boolean;
  onRefresh?: () => void;
  autoRefresh?: boolean;
  onToggleAutoRefresh?: () => void;
  className?: string;
}

export function LastUpdated({
  lastUpdated,
  isRefreshing = false,
  onRefresh,
  autoRefresh = false,
  onToggleAutoRefresh,
  className,
}: LastUpdatedProps) {
  const handleRefresh = () => {
    if (onRefresh && !isRefreshing) {
      onRefresh();
    }
  };

  return (
    <div className={cn('flex items-center justify-between', className)}>
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 text-sm text-white/70">
          <Clock className="w-4 h-4" />
          <span>
            {lastUpdated ? (
              `Last updated ${formatDistanceToNow(lastUpdated, { addSuffix: true })}`
            ) : (
              'No data available'
            )}
          </span>
        </div>
        
        {lastUpdated && (
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        )}
      </div>

      <div className="flex items-center space-x-2">
        {/* Auto-refresh toggle */}
        {onToggleAutoRefresh && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleAutoRefresh}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-medium border transition-all duration-200',
              autoRefresh
                ? 'glass-button text-blue-200 border-blue-300/30 neon-glow'
                : 'glass-button text-white/70 border-white/20 hover:text-white'
            )}
          >
            Auto-refresh
          </motion.button>
        )}

        {/* Manual refresh button */}
        {onRefresh && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={cn(
              'p-2 rounded-lg border transition-all duration-200',
              isRefreshing
                ? 'glass-button text-white/50 border-white/20 cursor-not-allowed'
                : 'glass-button text-white/70 border-white/20 hover:text-white'
            )}
          >
            <RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />
          </motion.button>
        )}
      </div>
    </div>
  );
}
