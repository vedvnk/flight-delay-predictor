'use client';

import { motion } from 'framer-motion';
import { Plane, Search, Calendar, MapPin } from 'lucide-react';

interface EmptyStateProps {
  type: 'search' | 'flights' | 'alternatives';
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({ type, title, description, action, className }: EmptyStateProps) {
  const getIcon = () => {
    switch (type) {
      case 'search':
        return <Search className="w-12 h-12 text-white/40" />;
      case 'flights':
        return <Plane className="w-12 h-12 text-white/40" />;
      case 'alternatives':
        return <Calendar className="w-12 h-12 text-white/40" />;
      default:
        return <MapPin className="w-12 h-12 text-white/40" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`flex flex-col items-center justify-center py-12 px-6 text-center ${className}`}
    >
      <div className="mb-6 p-4 rounded-2xl bg-white/5 border border-white/10">
        {getIcon()}
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-2">
        {title}
      </h3>
      
      <p className="text-white/70 max-w-md mb-6 leading-relaxed">
        {description}
      </p>
      
      {action && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={action.onClick}
          className="px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 rounded-xl text-white font-medium transition-all duration-200 backdrop-blur-sm"
        >
          {action.label}
        </motion.button>
      )}
    </motion.div>
  );
}
