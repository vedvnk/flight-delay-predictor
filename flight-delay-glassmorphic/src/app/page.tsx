'use client';

import { useState, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { motion } from 'framer-motion';
import { Plane, TrendingUp, Users, Clock } from 'lucide-react';

// Components
import { SearchForm } from '@/components/SearchForm';
import { FlightCard } from '@/components/FlightCard';
import { AlternativesSheet } from '@/components/AlternativesSheet';
import { CompareTray } from '@/components/CompareTray';
import { LastUpdated } from '@/components/LastUpdated';
import { EmptyState } from '@/components/EmptyState';
import { ErrorState } from '@/components/ErrorState';
import { FlightCardSkeleton } from '@/components/Skeletons';

// Hooks and utilities
import { useFlightStatus } from '@/hooks/useFlightStatus';
import { useAlternatives } from '@/hooks/useAlternatives';
import { NormalizedFlight, NormalizedAlternative } from '@/lib/adapters/normalize';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 seconds
      retry: 2,
    },
  },
});

// Helper function to format date without timezone issues
function formatSearchDate(dateString: string): string {
  // Parse the date string manually to avoid timezone conversion
  const [year, month, day] = dateString.split('-').map(Number);
  const date = new Date(year, month - 1, day); // month is 0-indexed
  
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function FlightDelayApp() {
  const [searchParams, setSearchParams] = useState<{
    from: string;
    to: string;
    date: string;
  } | null>({
    from: 'LAX',
    to: 'ORD', 
    date: '2025-09-21'
  });
  
  const [selectedFlight, setSelectedFlight] = useState<string | null>(null);
  const [compareAlternatives, setCompareAlternatives] = useState<NormalizedAlternative[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Queries
  const {
    data: flightData,
    isLoading: isLoadingFlights,
    error: flightError,
    refetch: refetchFlights,
    lastUpdated,
  } = useFlightStatus(searchParams, {
    enabled: !!searchParams,
    refetchInterval: autoRefresh ? 60000 : false, // 60 seconds
  });


  const {
    data: alternativesData,
    isLoading: isLoadingAlternatives,
    error: alternativesError,
  } = useAlternatives(selectedFlight, {
    enabled: !!selectedFlight,
  });

  // Handlers
  const handleSearch = useCallback((params: { from: string; to: string; date: string }) => {
    setSearchParams(params);
    setSelectedFlight(null);
    setCompareAlternatives([]);
  }, []);

  const handleViewAlternatives = useCallback((flightNumber: string) => {
    setSelectedFlight(flightNumber);
  }, []);

  const handleCloseAlternatives = useCallback(() => {
    setSelectedFlight(null);
  }, []);

  const handleCompare = useCallback((alternative: NormalizedAlternative) => {
    if (compareAlternatives.length < 3) {
      setCompareAlternatives(prev => {
        const exists = prev.some(alt => alt.flightNumber === alternative.flightNumber);
        if (!exists) {
          return [...prev, alternative];
        }
        return prev;
      });
    }
  }, [compareAlternatives.length]);

  const handleRemoveFromCompare = useCallback((flightNumber: string) => {
    setCompareAlternatives(prev => prev.filter(alt => alt.flightNumber !== flightNumber));
  }, []);

  const handleClearCompare = useCallback(() => {
    setCompareAlternatives([]);
  }, []);

  const handleRefresh = useCallback(() => {
    refetchFlights();
  }, [refetchFlights]);

  const handleToggleAutoRefresh = useCallback(() => {
    setAutoRefresh(prev => !prev);
  }, []);

  const handleSelectAlternative = useCallback((alternative: NormalizedAlternative) => {
    // Handle alternative selection (e.g., redirect to booking)
    console.log('Selected alternative:', alternative);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b1220] to-[#0b1220]/80 relative overflow-hidden">
      {/* Enhanced Header with floating elements */}
      <header className="border-b border-white/10 backdrop-blur-xl bg-white/5 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-blue-500/20 border border-blue-400/30 floating-element neon-glow">
                <Plane className="w-6 h-6 text-blue-300" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-white tracking-wider drop-shadow-2xl">
                  OnTime
                </h1>
                <p className="text-sm font-medium bg-gradient-to-r from-white/80 to-blue-200/70 bg-clip-text text-transparent tracking-wide">
                  Real-time delay predictions
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <LastUpdated
                lastUpdated={lastUpdated}
                isRefreshing={isLoadingFlights}
                onRefresh={handleRefresh}
                autoRefresh={autoRefresh}
                onToggleAutoRefresh={handleToggleAutoRefresh}
              />
            </div>
          </div>
        </div>
        
        {/* Floating decorative elements - hidden on mobile for performance */}
        <div className="absolute top-4 left-1/4 w-2 h-2 bg-blue-400/30 rounded-full floating-element animate-pulse-slow hidden md:block"></div>
        <div className="absolute top-8 right-1/3 w-1 h-1 bg-purple-400/40 rounded-full floating-element animate-pulse-slow hidden md:block" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-2 left-1/2 w-1.5 h-1.5 bg-cyan-400/30 rounded-full floating-element animate-pulse-slow hidden md:block" style={{animationDelay: '2s'}}></div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Search form */}
          <SearchForm onSubmit={handleSearch} isLoading={isLoadingFlights} />

          {/* Results section */}
          {searchParams && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              {/* Results header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-extrabold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent tracking-tight leading-tight drop-shadow-lg">
                    Flight Results
                  </h2>
                  <p className="text-lg font-semibold bg-gradient-to-r from-blue-200/90 to-cyan-200/80 bg-clip-text text-transparent mt-2 tracking-wide">
                    {searchParams.from} → {searchParams.to} • {formatSearchDate(searchParams.date)}
                  </p>
                </div>
                
                {flightData && (
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-400/30 rounded-full backdrop-blur-sm">
                      <Plane className="w-4 h-4 text-blue-300" />
                      <span className="font-bold bg-gradient-to-r from-blue-200 to-cyan-200 bg-clip-text text-transparent">{flightData.flights.length} flights</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Loading state */}
              {isLoadingFlights && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {Array.from({ length: 6 }).map((_, index) => (
                    <FlightCardSkeleton key={index} />
                  ))}
                </div>
              )}

              {/* Error state */}
              {flightError && (
                <ErrorState
                  type="network"
                  onRetry={handleRefresh}
                />
              )}

              {/* Empty state */}
              {flightData && flightData.flights.length === 0 && !isLoadingFlights && (
                <EmptyState
                  type="flights"
                  title="No flights found"
                  description="No flights available for the selected route and date. Try adjusting your search criteria."
                />
              )}

              {/* Flight cards */}
              {flightData && flightData.flights.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {flightData.flights.map((flight, index) => (
                    <motion.div
                      key={flight.flightNumber}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <FlightCard
                        flight={flight}
                        onViewAlternatives={handleViewAlternatives}
                      />
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* Enhanced No search state */}
          {!searchParams && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-center py-12 relative"
            >
              <div className="max-w-md mx-auto relative">
                {/* Floating background elements - hidden on mobile for performance */}
                <div className="absolute -top-8 -left-8 w-16 h-16 bg-blue-500/10 rounded-full floating-element animate-pulse-slow hidden md:block"></div>
                <div className="absolute -bottom-4 -right-4 w-12 h-12 bg-purple-500/10 rounded-full floating-element animate-pulse-slow hidden md:block" style={{animationDelay: '1.5s'}}></div>
                
                <div className="p-6 rounded-2xl glass-morphism-advanced hover-lift mb-6 relative z-10">
                  <div className="relative">
                    <Plane className="w-16 h-16 text-white/40 mx-auto floating-element" />
                    <div className="absolute inset-0 w-16 h-16 mx-auto bg-blue-400/20 rounded-full animate-ping"></div>
                  </div>
                </div>
                <h3 className="text-3xl font-black bg-gradient-to-r from-white via-blue-200 to-purple-300 bg-clip-text text-transparent mb-6 tracking-tight leading-tight drop-shadow-2xl">
                  Find Your Flight
                </h3>
                <p className="text-lg font-medium bg-gradient-to-r from-white/90 via-blue-100/80 to-cyan-100/70 bg-clip-text text-transparent leading-relaxed tracking-wide">
                  Search for flights and get real-time delay predictions. 
                  Compare alternatives and make informed travel decisions.
                </p>
                
                {/* Additional floating elements - hidden on mobile for performance */}
                <div className="absolute top-1/2 -left-12 w-3 h-3 bg-cyan-400/30 rounded-full floating-element animate-bounce-gentle hidden md:block"></div>
                <div className="absolute top-1/3 -right-8 w-2 h-2 bg-yellow-400/40 rounded-full floating-element animate-bounce-gentle hidden md:block" style={{animationDelay: '1s'}}></div>
              </div>
            </motion.div>
          )}
        </div>
      </main>

      {/* Alternatives sheet */}
      {selectedFlight && alternativesData && (
        <AlternativesSheet
          isOpen={!!selectedFlight}
          onClose={handleCloseAlternatives}
          alternatives={alternativesData.alternatives}
          originalFlight={{
            flightNumber: selectedFlight,
            departureTime: '09:30',
            arrivalTime: '11:45',
            totalDuration: '2h 15m',
          }}
          onCompare={handleCompare}
          onSelect={handleSelectAlternative}
        />
      )}

      {/* Compare tray */}
      <CompareTray
        isOpen={compareAlternatives.length > 0}
        alternatives={compareAlternatives}
        onRemove={handleRemoveFromCompare}
        onClear={handleClearCompare}
      />
    </div>
  );
}

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <FlightDelayApp />
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}