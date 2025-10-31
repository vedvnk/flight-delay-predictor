'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, Plane, Calendar, MapPin } from 'lucide-react';
import { isValidIATACode, isValidRoute, getAirportSuggestions } from '@/lib/iata';
import { cn } from '@/lib/utils';

interface SearchFormProps {
  onSubmit: (data: { from: string; to: string; date: string }) => void;
  isLoading?: boolean;
  className?: string;
}

interface RecentSearch {
  from: string;
  to: string;
  date: string;
  timestamp: Date;
}

const today = new Date().toISOString().split('T')[0];
export function SearchForm({ onSubmit, isLoading = false, className }: SearchFormProps) {
  const [from, setFrom] = useState('LAX');
  const [to, setTo] = useState('ORD');
  const [date, setDate] = useState(today);
  
  const [fromSuggestions, setFromSuggestions] = useState<Array<{code: string; name: string; fullText: string}>>([]);
  const [toSuggestions, setToSuggestions] = useState<Array<{code: string; name: string; fullText: string}>>([]);
  const [showFromSuggestions, setShowFromSuggestions] = useState(false);
  const [showToSuggestions, setShowToSuggestions] = useState(false);
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);

  const handleFromChange = useCallback((value: string) => {
    setFrom(value.toUpperCase());
    if (value.length >= 1) {
      const suggestions = getAirportSuggestions(value, 5);
      setFromSuggestions(suggestions);
      setShowFromSuggestions(true);
    } else {
      setShowFromSuggestions(false);
    }
  }, []);

  const handleToChange = useCallback((value: string) => {
    setTo(value.toUpperCase());
    if (value.length >= 1) {
      const suggestions = getAirportSuggestions(value, 5);
      setToSuggestions(suggestions);
      setShowToSuggestions(true);
    } else {
      setShowToSuggestions(false);
    }
  }, []);

  const handleFromSelect = (suggestion: {code: string; name: string; fullText: string}) => {
    setFrom(suggestion.code);
    setShowFromSuggestions(false);
  };

  const handleToSelect = (suggestion: {code: string; name: string; fullText: string}) => {
    setTo(suggestion.code);
    setShowToSuggestions(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (from.length < 3 || to.length < 3 || from === to) {
      return;
    }

    const searchData = { from, to, date };
    
    // Add to recent searches
    const newSearch: RecentSearch = {
      ...searchData,
      timestamp: new Date(),
    };
    
    setRecentSearches(prev => {
      const filtered = prev.filter(s => !(s.from === from && s.to === to));
      return [newSearch, ...filtered].slice(0, 5);
    });

    onSubmit(searchData);
  };

  const handleRecentSearch = (search: RecentSearch) => {
    setFrom(search.from);
    setTo(search.to);
    setDate(search.date);
    onSubmit(search);
  };

  const isValid = from.length >= 3 && to.length >= 3 && date && from !== to;

  return (
    <div className={cn('space-y-6', className)}>
      {/* Main search form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="glass-morphism-advanced rounded-2xl p-6 hover-lift relative overflow-hidden"
      >
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 rounded-xl bg-blue-500/20 border border-blue-400/30">
            <Plane className="w-5 h-5 text-blue-300" />
          </div>
          <h2 className="text-xl font-semibold text-white">Search Flights</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* From airport */}
            <div className="relative">
              <label className="block text-sm font-medium text-white/80 mb-2">
                From
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={from}
                  onChange={(e) => handleFromChange(e.target.value)}
                  placeholder="SEA"
                  maxLength={3}
                  className="w-full px-4 py-3 glass-input rounded-xl text-white placeholder-white/50 focus:outline-none transition-all duration-200"
                />
                <MapPin className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/50" />
              </div>
              
              {/* From suggestions */}
              {showFromSuggestions && fromSuggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white/10 border border-white/20 rounded-xl backdrop-blur-xl shadow-lg z-10">
                  {fromSuggestions.map((suggestion) => (
                    <button
                      key={suggestion.code}
                      type="button"
                      onClick={() => handleFromSelect(suggestion)}
                      className="w-full px-4 py-2 text-left text-white hover:bg-white/20 transition-colors first:rounded-t-xl last:rounded-b-xl"
                    >
                      <div className="font-medium">{suggestion.code}</div>
                      <div className="text-sm text-white/70">{suggestion.name}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* To airport */}
            <div className="relative">
              <label className="block text-sm font-medium text-white/80 mb-2">
                To
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={to}
                  onChange={(e) => handleToChange(e.target.value)}
                  placeholder="SFO"
                  maxLength={3}
                  className="w-full px-4 py-3 glass-input rounded-xl text-white placeholder-white/50 focus:outline-none transition-all duration-200"
                />
                <MapPin className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/50" />
              </div>
              
              {/* To suggestions */}
              {showToSuggestions && toSuggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white/10 border border-white/20 rounded-xl backdrop-blur-xl shadow-lg z-10">
                  {toSuggestions.map((suggestion) => (
                    <button
                      key={suggestion.code}
                      type="button"
                      onClick={() => handleToSelect(suggestion)}
                      className="w-full px-4 py-2 text-left text-white hover:bg-white/20 transition-colors first:rounded-t-xl last:rounded-b-xl"
                    >
                      <div className="font-medium">{suggestion.code}</div>
                      <div className="text-sm text-white/70">{suggestion.name}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Date */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Date
              </label>
              <div className="relative">
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full px-4 py-3 glass-input rounded-xl text-white focus:outline-none transition-all duration-200"
                />
                <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/50" />
              </div>
            </div>

            {/* Submit button */}
            <div className="flex items-end">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={!isValid || isLoading}
                className={cn(
                  'w-full px-4 py-3 rounded-xl font-medium transition-all duration-200 flex items-center justify-center space-x-2 relative overflow-hidden',
                  isValid && !isLoading
                    ? 'glass-button text-blue-200 hover:text-blue-100 neon-glow-hover'
                    : 'bg-white/10 border border-white/20 text-white/50 cursor-not-allowed'
                )}
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Search</span>
                  </>
                )}
              </motion.button>
            </div>
          </div>
        </form>
      </motion.div>

      {/* Recent searches */}
      {recentSearches.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-white/5 border border-white/10 rounded-xl p-4"
        >
          <h3 className="text-sm font-medium text-white/80 mb-3">Recent Searches</h3>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((search, index) => (
              <motion.button
                key={`${search.from}-${search.to}-${search.date}-${index}`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleRecentSearch(search)}
                className="px-3 py-1.5 bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 rounded-lg text-sm text-white/80 hover:text-white transition-all duration-200"
              >
                {search.from} → {search.to} ({new Date(search.date).toLocaleDateString()})
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
