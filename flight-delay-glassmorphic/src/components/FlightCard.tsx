'use client';

import { motion } from 'framer-motion';
import { Clock, MapPin, Plane, ArrowRight, AlertTriangle } from 'lucide-react';
import { NormalizedFlight } from '@/lib/adapters/normalize';
import { getStatusConfig, getDelayRiskConfig } from '@/lib/status';
import { cn } from '@/lib/utils';

interface FlightCardProps {
  flight: NormalizedFlight;
  onViewAlternatives: (flightNumber: string) => void;
  className?: string;
}

export function FlightCard({ flight, onViewAlternatives, className }: FlightCardProps) {
  // Use delay risk if available, otherwise fall back to status
  const displayConfig = flight.delayRisk 
    ? getDelayRiskConfig(flight.delayRisk)
    : getStatusConfig(flight.status);
  
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
        {/* Header with airline and flight number */}
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
          
          {/* Delay Risk pill */}
          <div className={cn(
            'inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border backdrop-blur-sm',
            displayConfig.bgColor,
            displayConfig.textColor,
            displayConfig.borderColor
          )}>
            <div className="w-1.5 h-1.5 rounded-full bg-current mr-2" />
            {flight.delayRiskPercentage || displayConfig.label}
          </div>
        </div>

        {/* Route and times */}
        <div className="space-y-4">
          {/* Route */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-white tabular-nums">
                  {flight.estimatedDepartureText || flight.departureTimeText}
                </div>
                <div className="text-xs text-white/60 uppercase tracking-wide">
                  {flight.from}
                </div>
              </div>
              
              <ArrowRight className="w-5 h-5 text-white/50 flex-shrink-0" />
              
              <div className="text-center">
                <div className="text-2xl font-bold text-white tabular-nums">
                  {flight.estimatedArrivalText || flight.arrivalTimeText}
                </div>
                <div className="text-xs text-white/60 uppercase tracking-wide">
                  {flight.to}
                </div>
              </div>
            </div>
          </div>

          {/* Delay information */}
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

          {/* Gate and additional info */}
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

        {/* Action button */}
        <div className="mt-6 pt-4 border-t border-white/10">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onViewAlternatives(flight.flightNumber)}
            className="w-full glass-button rounded-xl px-4 py-2.5 text-sm font-medium text-white relative overflow-hidden group"
          >
            <span className="relative z-10">View Alternatives</span>
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
