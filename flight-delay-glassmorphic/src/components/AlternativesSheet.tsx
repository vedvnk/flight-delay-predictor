'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock, Users, TrendingUp, ArrowRight, Plus } from 'lucide-react';
import { NormalizedAlternative } from '@/lib/adapters/normalize';
import { getOnTimeProbabilityConfig, getSeatAvailabilityConfig } from '@/lib/status';
import { cn } from '@/lib/utils';

interface AlternativesSheetProps {
  isOpen: boolean;
  onClose: () => void;
  alternatives: NormalizedAlternative[];
  originalFlight: {
    flightNumber: string;
    departureTime: string;
    arrivalTime: string;
    totalDuration: string;
  };
  onCompare: (alternative: NormalizedAlternative) => void;
  onSelect: (alternative: NormalizedAlternative) => void;
}

export function AlternativesSheet({
  isOpen,
  onClose,
  alternatives,
  originalFlight,
  onCompare,
  onSelect,
}: AlternativesSheetProps) {
  const onTimeProbabilityStatus = (probability: number) => {
    if (probability >= 0.9) return 'excellent';
    if (probability >= 0.75) return 'good';
    if (probability >= 0.6) return 'fair';
    return 'poor';
  };

  const seatAvailabilityStatus = (seatsLeft: number) => {
    if (seatsLeft === 0) return 'full';
    if (seatsLeft <= 3) return 'limited';
    return 'available';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />
          
          {/* Sheet */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md glass-morphism-advanced border-l border-white/15 shadow-[0_0_50px_rgba(2,6,23,0.5)] z-50 overflow-hidden"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-white/10">
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    Alternative Flights
                  </h2>
                  <p className="text-sm text-white/70 mt-1">
                    {alternatives.length} options found
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onClose}
                  className="p-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 transition-colors"
                >
                  <X className="w-5 h-5 text-white" />
                </motion.button>
              </div>

              {/* Original flight reference */}
              <div className="p-6 border-b border-white/10">
                <h3 className="text-sm font-medium text-white/70 mb-3">Original Flight</h3>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-white">{originalFlight.flightNumber}</span>
                    <span className="text-sm text-white/70">{originalFlight.totalDuration}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-white/70">
                    <span>{originalFlight.departureTime}</span>
                    <ArrowRight className="w-4 h-4" />
                    <span>{originalFlight.arrivalTime}</span>
                  </div>
                </div>
              </div>

              {/* Alternatives list */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {alternatives.map((alternative) => {
                  const otpStatus = onTimeProbabilityStatus(alternative.onTimeProbability);
                  const seatStatus = seatAvailabilityStatus(alternative.seatsLeft);
                  const otpConfig = getOnTimeProbabilityConfig(otpStatus as any);
                  const seatConfig = getSeatAvailabilityConfig(seatStatus as any);

                  return (
                    <motion.div
                      key={alternative.flightNumber}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="glass-morphism-advanced rounded-xl p-4 hover-lift transition-all duration-300"
                    >
                      {/* Flight header */}
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-white">{alternative.flightNumber}</h4>
                          <p className="text-sm text-white/70">{alternative.airline}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-white tabular-nums">
                            {alternative.totalDuration}
                          </div>
                          <div className="text-xs text-white/60">duration</div>
                        </div>
                      </div>

                      {/* Times */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg font-bold text-white tabular-nums">
                            {alternative.departureTimeText}
                          </span>
                          <ArrowRight className="w-4 h-4 text-white/50" />
                          <span className="text-lg font-bold text-white tabular-nums">
                            {alternative.arrivalTimeText}
                          </span>
                        </div>
                      </div>

                      {/* Metrics */}
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        {/* On-time probability */}
                        <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                          <div className="flex items-center space-x-2 mb-2">
                            <TrendingUp className="w-4 h-4 text-white/70" />
                            <span className="text-xs text-white/70">On-time</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-semibold text-white">
                              {alternative.onTimePercentage}% chance of delay
                            </span>
                            <div className={cn(
                              'px-2 py-0.5 rounded-full text-xs border',
                              otpConfig.bgColor,
                              otpConfig.textColor,
                              otpConfig.borderColor
                            )}>
                              {otpConfig.label}
                            </div>
                          </div>
                        </div>

                        {/* Seat availability */}
                        <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                          <div className="flex items-center space-x-2 mb-2">
                            <Users className="w-4 h-4 text-white/70" />
                            <span className="text-xs text-white/70">Seats</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-semibold text-white">
                              {alternative.seatsLeft}
                            </span>
                            <div className={cn(
                              'px-2 py-0.5 rounded-full text-xs border',
                              seatConfig.bgColor,
                              seatConfig.textColor,
                              seatConfig.borderColor
                            )}>
                              {seatConfig.label}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex space-x-2">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => onCompare(alternative)}
                          className="flex-1 glass-button rounded-lg px-3 py-2 text-sm font-medium text-white transition-all duration-200 flex items-center justify-center space-x-2"
                        >
                          <Plus className="w-4 h-4" />
                          <span>Compare</span>
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => onSelect(alternative)}
                          className="flex-1 glass-button rounded-lg px-3 py-2 text-sm font-medium text-blue-200 transition-all duration-200 neon-glow-hover"
                        >
                          Select
                        </motion.button>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
