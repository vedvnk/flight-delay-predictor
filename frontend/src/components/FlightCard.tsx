'use client';

import { motion } from 'framer-motion';
import { Clock, MapPin, Plane, ArrowRight, AlertTriangle } from 'lucide-react';
import { NormalizedFlight } from '@/lib/adapters/normalize';
import { getStatusConfig } from '@/lib/status';
import { cn } from '@/lib/utils';

interface FlightCardProps {
  flight: NormalizedFlight;
  className?: string;
}

export function FlightCard({ flight, className }: FlightCardProps) {
  const statusConfig = getStatusConfig(flight.status);

  // Prediction fields (mocked if not present)
  // You may need to pass these in via parent/adapters (add actual bindings as appropriate):
  const predictedDelayRisk = flight.delayRisk || 'LOW';
  const predictedDelayPercent =
    typeof flight.delayProbability === 'number'
      ? Math.round(flight.delayProbability * 100)
      : 9; // fallback
  const predictedDelayMinutes = flight.predictedDelayMinutes || 4; // fallback

  // Risk badge config
  const riskColors: Record<string, string> = {
    LOW: 'bg-green-500/20 text-green-400 border-green-400/30',
    MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30',
    HIGH: 'bg-red-500/20 text-red-400 border-red-400/30',
  };
  const riskText: Record<string, string> = {
    LOW: 'Low',
    MEDIUM: 'Medium',
    HIGH: 'High',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
      className={cn(
        'group relative overflow-hidden rounded-2xl glass-morphism-advanced hover-lift transition-all duration-300',
        className
      )}
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      <div className="relative p-6">
        {/* Header with status and PREDICTION badge */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center relative floating-element">
              <Plane className="w-5 h-5 text-white/80" />
              <div className="absolute inset-0 bg-blue-400/20 rounded-xl animate-ping"></div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white tabular-nums text-shadow">
                {flight.flightNumber}
              </h3>
              <p className="text-sm text-white/70">{flight.airline}</p>
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <div
              className={cn(
                'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border',
                riskColors[predictedDelayRisk] || 'bg-white/10 text-white/70 border-white/20'
              )}
              title={`Predicted risk: ${riskText[predictedDelayRisk]}`}
            >
              <span className="mr-2">Risk:</span>
              {riskText[predictedDelayRisk] || predictedDelayRisk}
              <span className="ml-3">{predictedDelayPercent}% • {predictedDelayMinutes}m</span>
            </div>
            <div
              className={cn(
                'inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border backdrop-blur-sm',
                statusConfig.bgColor,
                statusConfig.textColor,
                statusConfig.borderColor
              )}
            >
              <div className="w-1.5 h-1.5 rounded-full bg-current mr-2" />
              {statusConfig.label}
            </div>
          </div>
        </div>

        {/* Route and times (unchanged) */}
        <div className="space-y-4">
          {/* Route */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-white tabular-nums">
                  {flight.departureTimeText}
                </div>
                <div className="text-xs text-white/60 uppercase tracking-wide">
                  {flight.from}
                </div>
              </div>

              <ArrowRight className="w-5 h-5 text-white/50 flex-shrink-0" />

              <div className="text-center">
                <div className="text-2xl font-bold text-white tabular-nums">
                  {flight.estimatedTimeText || flight.departureTimeText}
                </div>
                <div className="text-xs text-white/60 uppercase tracking-wide">
                  {flight.to}
                </div>
              </div>
            </div>
          </div>

          {/* Delay information (unchanged, but now always visible under prediction badge) */}
          {flight.isDelayed && flight.delayMinutes && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center space-x-2 text-amber-200 bg-amber-400/10 border border-amber-300/20 rounded-lg px-3 py-2"
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm font-medium">
                {flight.delayText} delay
              </span>
            </motion.div>
          )}

          {/* Gate and additional info (unchanged) */}
          <div className="flex items-center justify-between text-sm text-white/70">
            <div className="flex items-center space-x-4">
              {flight.gate && (
                <div className="flex items-center space-x-1">
                  <MapPin className="w-4 h-4" />
                  <span>Gate {flight.gate}</span>
                </div>
              )}

              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>Updated {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </div>
          </div>
        </div>
        {/* REMOVE ACTION BUTTON! */}
      </div>
    </motion.div>
  );
}
