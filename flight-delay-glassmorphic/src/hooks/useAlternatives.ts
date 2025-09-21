import { useQuery } from '@tanstack/react-query';
import { apiClient, queryKeys } from '@/lib/api';
import { mockApiClient } from '@/lib/mockApi';
import { normalizeAlternatives, NormalizedAlternative } from '@/lib/adapters/normalize';

interface UseAlternativesOptions {
  enabled?: boolean;
  staleTime?: number;
}

export function useAlternatives(
  flightNumber: string | null,
  options: UseAlternativesOptions = {}
) {
  const {
    enabled = true,
    staleTime = 60 * 1000, // 1 minute
  } = options;

  const query = useQuery({
    queryKey: flightNumber ? queryKeys.alternatives(flightNumber) : [],
    queryFn: async () => {
      if (!flightNumber) throw new Error('Flight number required');
      
      const response = await apiClient.getAlternatives(flightNumber);
      const normalizedAlternatives = normalizeAlternatives(response.alternatives);
      
      return {
        alternatives: normalizedAlternatives,
        rawResponse: response,
      };
    },
    enabled: enabled && !!flightNumber,
    staleTime,
    retry: (failureCount, error) => {
      // Don't retry on 404 (no alternatives found)
      if (error instanceof Error && error.message.includes('404')) {
        return false;
      }
      return failureCount < 2;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
  });

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    alternatives: query.data?.alternatives || [],
    rawResponse: query.data?.rawResponse,
  };
}
