'use client';

import { useState, useCallback } from 'react';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Plane, TrendingUp, BarChart3, AlertCircle, CheckCircle, Clock, PieChart, ArrowLeft } from 'lucide-react';

// Components
import { EmptyState } from '@/components/EmptyState';
import { ErrorState } from '@/components/ErrorState';

// API
import { apiClient, queryKeys } from '@/lib/api';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 seconds
      retry: 2,
    },
  },
});

function getRiskColor(category: string): string {
  switch (category) {
    case 'LOW':
      return 'text-green-400';
    case 'MEDIUM':
      return 'text-yellow-400';
    case 'HIGH':
      return 'text-red-400';
    default:
      return 'text-white';
  }
}

function getRiskBgColor(category: string): string {
  switch (category) {
    case 'LOW':
      return 'bg-green-500/20 border-green-400/30';
    case 'MEDIUM':
      return 'bg-yellow-500/20 border-yellow-400/30';
    case 'HIGH':
      return 'bg-red-500/20 border-red-400/30';
    default:
      return 'bg-white/10 border-white/20';
  }
}

function MonthlyDashboard() {
  const [selectedYear, setSelectedYear] = useState(2025);
  const [selectedMonth, setSelectedMonth] = useState(6);
  const [selectedAirline, setSelectedAirline] = useState('DL');

  // Fetch airlines
  const { data: airlinesData, isLoading: isLoadingAirlines } = useQuery({
    queryKey: queryKeys.airlines,
    queryFn: () => apiClient.getAirlines(),
  });

  // Fetch available months
  const { data: monthsData } = useQuery({
    queryKey: queryKeys.availableMonths,
    queryFn: () => apiClient.getAvailableMonths(),
  });

  // Fetch prediction
  const { data: predictionData, isLoading: isLoadingPrediction, error: predictionError } = useQuery({
    queryKey: queryKeys.monthlyPrediction(selectedYear, selectedMonth, selectedAirline),
    queryFn: () => apiClient.getMonthlyPrediction({
      year: selectedYear,
      month: selectedMonth,
      airline: selectedAirline,
    }),
    enabled: !!selectedYear && !!selectedMonth && !!selectedAirline,
  });

  const handleAirlineChange = useCallback((airline: string) => {
    setSelectedAirline(airline);
  }, []);

  const handleMonthChange = useCallback((year: number, month: number) => {
    setSelectedYear(year);
    setSelectedMonth(month);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b1220] to-[#0b1220]/80 relative overflow-hidden">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-xl bg-white/5 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Link
                href="/"
                className="flex items-center space-x-2 px-3 py-2 glass-button rounded-lg hover:bg-white/10 transition-all duration-200 mr-4"
              >
                <ArrowLeft className="w-4 h-4 text-blue-300" />
                <span className="text-sm text-white">Back</span>
              </Link>
              <div className="p-2 rounded-xl bg-blue-500/20 border border-blue-400/30 floating-element neon-glow">
                <TrendingUp className="w-6 h-6 text-blue-300" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white text-shadow">Monthly Delay Predictor</h1>
                <p className="text-sm text-white/70">Airline performance analysis</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Selectors */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="glass-morphism-advanced rounded-2xl p-6 hover-lift relative overflow-hidden"
          >
            <div className="space-y-4">
              {/* Airline selector */}
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Select Airline
                </label>
                <select
                  value={selectedAirline}
                  onChange={(e) => handleAirlineChange(e.target.value)}
                  className="w-full px-4 py-3 glass-input rounded-xl text-white focus:outline-none transition-all duration-200"
                >
                  {airlinesData?.airlines.map((airline) => (
                    <option key={airline.iata_code} value={airline.iata_code}>
                      {airline.name} ({airline.iata_code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Year and Month selectors */}
              <div className="grid grid-cols-2 gap-4">
                {/* Year selector */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Year
                  </label>
                  <select
                    value={selectedYear}
                    onChange={(e) => handleMonthChange(Number(e.target.value), selectedMonth)}
                    className="w-full px-4 py-3 glass-input rounded-xl text-white focus:outline-none transition-all duration-200"
                  >
                    {monthsData && Array.from(new Set(monthsData.periods.map(p => p.year))).sort((a, b) => b - a).map((year) => (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Month selector */}
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Month
                  </label>
                  <select
                    value={selectedMonth}
                    onChange={(e) => handleMonthChange(selectedYear, Number(e.target.value))}
                    className="w-full px-4 py-3 glass-input rounded-xl text-white focus:outline-none transition-all duration-200"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((month) => (
                      <option key={month} value={month}>
                        {new Date(selectedYear, month - 1, 1).toLocaleDateString('en-US', { month: 'long' })}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Quick access buttons for recent months */}
              {monthsData && monthsData.periods.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Quick Select
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {monthsData.periods.slice(0, 6).map((period) => (
                      <motion.button
                        key={period.label}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleMonthChange(period.year, period.month)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                          selectedYear === period.year && selectedMonth === period.month
                            ? 'bg-blue-500/30 text-blue-300 border-2 border-blue-400/50'
                            : 'bg-white/10 text-white/70 hover:bg-white/20 border-2 border-white/20'
                        }`}
                      >
                        {period.month_name}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Prediction Display */}
          {isLoadingPrediction ? (
            <div className="glass-morphism-advanced rounded-2xl p-6">
              <div className="flex items-center justify-center space-x-2 text-white/70">
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <span>Loading prediction...</span>
              </div>
            </div>
          ) : predictionError ? (
            <ErrorState
              type="network"
              onRetry={() => {}}
            />
          ) : predictionData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Main prediction card */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className={`glass-morphism-advanced rounded-2xl p-6 hover-lift border-2 ${getRiskBgColor(predictionData.prediction.delay_risk_category)}`}
              >
                <div className="flex items-center space-x-3 mb-4">
                  <Plane className="w-8 h-8 text-blue-300" />
                  <div>
                    <h2 className="text-xl font-bold text-white">
                      {predictionData.airline.name}
                    </h2>
                    <p className="text-sm text-white/70">
                      {new Date(predictionData.year, predictionData.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    </p>
                  </div>
                </div>

                {/* Delay probability */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-white/70">Delay Probability</span>
                    <span className={`text-3xl font-bold ${getRiskColor(predictionData.prediction.delay_risk_category)}`}>
                      {predictionData.prediction.delay_probability}%
                    </span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${predictionData.prediction.delay_probability}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className={`h-full ${predictionData.prediction.delay_risk_color === 'green' ? 'bg-green-500' : predictionData.prediction.delay_risk_color === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'}`}
                    />
                  </div>
                </div>

                {/* Delay duration */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 glass-morphism-advanced rounded-xl">
                    <div className="flex items-center space-x-3">
                      <Clock className="w-5 h-5 text-blue-300" />
                      <span className="text-white/70">Expected Delay</span>
                    </div>
                    <span className="text-xl font-bold text-white">
                      {predictionData.prediction.predicted_delay_duration_formatted}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-4 glass-morphism-advanced rounded-xl">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-300" />
                      <span className="text-white/70">On-Time Rate</span>
                    </div>
                    <span className="text-xl font-bold text-green-400">
                      {predictionData.metrics.on_time_percentage}%
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-4 glass-morphism-advanced rounded-xl">
                    <div className="flex items-center space-x-3">
                      <TrendingUp className="w-5 h-5 text-blue-300" />
                      <span className="text-white/70">Completion Factor</span>
                    </div>
                    <span className="text-xl font-bold text-blue-400">
                      {predictionData.metrics.estimated_completion_factor}%
                    </span>
                  </div>
                </div>
              </motion.div>

              {/* Delay causes chart */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="glass-morphism-advanced rounded-2xl p-6 hover-lift"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <PieChart className="w-8 h-8 text-purple-300" />
                  <h2 className="text-xl font-bold text-white">Delay Causes</h2>
                </div>

                <div className="space-y-4">
                  {predictionData.delay_causes.map((cause: any, index: number) => (
                    <motion.div
                      key={cause.cause}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      className="space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-white/80 text-sm">{cause.cause}</span>
                        <span className="text-white font-bold">{cause.percentage}%</span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${cause.percentage}%` }}
                          transition={{ duration: 1, ease: "easeOut", delay: index * 0.1 }}
                          className="h-full"
                          style={{ backgroundColor: cause.color }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}

export default function MonthlyPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <MonthlyDashboard />
    </QueryClientProvider>
  );
}

