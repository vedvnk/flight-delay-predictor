import { useQuery } from '@tanstack/react-query';
import { apiClient, queryKeys } from '@/lib/api';
import { mockApiClient } from '@/lib/mockApi';
import { normalizeFlights, NormalizedFlight } from '@/lib/adapters/normalize';

interface UseFlightStatusOptions {
  enabled?: boolean;
  refetchInterval?: number | false;
  staleTime?: number;
}

export function useFlightStatus(
  searchParams: { from: string; to: string; date: string } | null,
  options: UseFlightStatusOptions = {}
) {
  const {
    enabled = true,
    refetchInterval = false,
    staleTime = 30 * 1000, // 30 seconds
  } = options;

  const query = useQuery({
    queryKey: searchParams ? queryKeys.flightStatus(searchParams.from, searchParams.to, searchParams.date) : [],
    queryFn: async () => {
      if (!searchParams) throw new Error('Search parameters required');
      
      console.log('useFlightStatus: Making query with params:', searchParams);
      const response = await apiClient.getFlightStatus(searchParams);
      console.log('useFlightStatus: Got response:', response);
      const normalizedFlights = normalizeFlights(response.flights);
      
      return {
        flights: normalizedFlights,
        lastUpdated: new Date(response.lastUpdated),
        rawResponse: response,
      };
    },
    enabled: enabled && !!searchParams,
    refetchInterval,
    staleTime,
    retry: (failureCount, error) => {
      // Don't retry on 404 (no flights found)
      if (error instanceof Error && error.message.includes('404')) {
        return false;
      }
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    lastUpdated: query.data?.lastUpdated || null,
    flights: query.data?.flights || [],
    rawResponse: query.data?.rawResponse,
  };
}
