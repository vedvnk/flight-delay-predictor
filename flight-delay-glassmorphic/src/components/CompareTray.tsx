'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowRight, TrendingUp, Users, Clock } from 'lucide-react';
import { NormalizedAlternative } from '@/lib/adapters/normalize';
import { cn } from '@/lib/utils';

interface CompareTrayProps {
  isOpen: boolean;
  alternatives: NormalizedAlternative[];
  onRemove: (flightNumber: string) => void;
  onClear: () => void;
}

export function CompareTray({ isOpen, alternatives, onRemove, onClear }: CompareTrayProps) {
  if (!isOpen || alternatives.length === 0) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed bottom-0 left-0 right-0 z-50 p-4"
        >
          <div className="max-w-7xl mx-auto">
            <div className="glass-morphism-advanced rounded-2xl overflow-hidden hover-lift">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-white/10">
                <div className="flex items-center space-x-3">
                  <h3 className="text-lg font-semibold text-white">
                    Compare Flights ({alternatives.length})
                  </h3>
                  <div className="px-2 py-1 bg-blue-400/20 text-blue-200 text-xs rounded-full border border-blue-300/30">
                    {alternatives.length}/3
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {alternatives.length > 0 && (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={onClear}
                      className="px-3 py-1.5 text-sm text-white/70 hover:text-white bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                    >
                      Clear All
                    </motion.button>
                  )}
                </div>
              </div>

              {/* Comparison table */}
              <div className="overflow-x-auto">
                <div className="min-w-full">
                  {/* Table header */}
                  <div className="grid grid-cols-12 gap-4 p-4 text-xs font-medium text-white/70 uppercase tracking-wide border-b border-white/10">
                    <div className="col-span-2">Flight</div>
                    <div className="col-span-2">Airline</div>
                    <div className="col-span-2">Departure</div>
                    <div className="col-span-2">Arrival</div>
                    <div className="col-span-1">Duration</div>
                    <div className="col-span-1">On-time</div>
                    <div className="col-span-1">Seats</div>
                    <div className="col-span-1">Actions</div>
                  </div>

                  {/* Table rows */}
                  <div className="divide-y divide-white/10">
                    {alternatives.map((alternative, index) => (
                      <motion.div
                        key={alternative.flightNumber}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="grid grid-cols-12 gap-4 p-4 hover:bg-white/5 transition-colors"
                      >
                        {/* Flight number */}
                        <div className="col-span-2">
                          <div className="font-semibold text-white tabular-nums">
                            {alternative.flightNumber}
                          </div>
                          <div className="text-xs text-white/60">
                            {alternative.from} → {alternative.to}
                          </div>
                        </div>

                        {/* Airline */}
                        <div className="col-span-2">
                          <div className="text-sm text-white/90">{alternative.airline}</div>
                        </div>

                        {/* Departure time */}
                        <div className="col-span-2">
                          <div className="font-semibold text-white tabular-nums">
                            {alternative.departureTimeText}
                          </div>
                        </div>

                        {/* Arrival time */}
                        <div className="col-span-2">
                          <div className="font-semibold text-white tabular-nums">
                            {alternative.arrivalTimeText}
                          </div>
                        </div>

                        {/* Duration */}
                        <div className="col-span-1">
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3 text-white/50" />
                            <span className="text-sm text-white/90">{alternative.totalDuration}</span>
                          </div>
                        </div>

                        {/* On-time probability */}
                        <div className="col-span-1">
                          <div className="flex items-center space-x-1">
                            <TrendingUp className="w-3 h-3 text-white/50" />
                            <span className="text-sm font-semibold text-white">
                              {alternative.onTimePercentage}% chance of delay
                            </span>
                          </div>
                        </div>

                        {/* Seat availability */}
                        <div className="col-span-1">
                          <div className="flex items-center space-x-1">
                            <Users className="w-3 h-3 text-white/50" />
                            <span className={cn(
                              'text-sm font-semibold',
                              alternative.seatsLeft === 0 ? 'text-rose-300' :
                              alternative.seatsLeft <= 3 ? 'text-amber-300' :
                              'text-emerald-300'
                            )}>
                              {alternative.seatsLeft}
                            </span>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="col-span-1">
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => onRemove(alternative.flightNumber)}
                            className="p-1.5 rounded-lg bg-rose-400/20 hover:bg-rose-400/30 border border-rose-300/30 hover:border-rose-300/50 transition-colors"
                          >
                            <X className="w-4 h-4 text-rose-300" />
                          </motion.button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer with summary */}
              <div className="p-4 border-t border-white/10 bg-white/5">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-white/70">
                    {alternatives.length} flight{alternatives.length !== 1 ? 's' : ''} selected for comparison
                  </div>
                  <div className="flex items-center space-x-2">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 hover:border-blue-400/50 rounded-lg text-sm font-medium text-blue-200 transition-all duration-200"
                    >
                      Book Selected
                    </motion.button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
