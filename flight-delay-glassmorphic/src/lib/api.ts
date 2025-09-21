import { z } from 'zod';

// Zod schemas for API validation
export const flightStatusSchema = z.object({
  flightNumber: z.string(),
  airline: z.string(),
  from: z.string(),
  to: z.string(),
  schedDep: z.string(),
  estDep: z.string().nullable(),
  schedArr: z.string().optional(),
  estArr: z.string().nullable().optional(),
  gate: z.string().nullable(),
  status: z.enum(['ON_TIME', 'DELAYED', 'CANCELED', 'LANDED', 'SCHEDULED', 'BOARDING']),
  delayMinutes: z.number().nullable(),
  seatsAvailable: z.number().optional(),
  onTimeProbability: z.number().min(0).max(1).optional(),
  delayProbability: z.number().min(0).max(1).optional(),
  delayRisk: z.enum(['LOW', 'MEDIUM', 'HIGH']).optional(),
  delayRiskPercentage: z.string().optional(),
});

export const alternativeFlightSchema = z.object({
  flightNumber: z.string(),
  airline: z.string(),
  schedDep: z.string(),
  schedArr: z.string(),
  from: z.string(),
  to: z.string(),
  seatsLeft: z.number(),
  onTimeProbability: z.number().min(0).max(1),
  gate: z.string().nullable().optional(),
  status: z.enum(['ON_TIME', 'DELAYED', 'CANCELED', 'LANDED', 'SCHEDULED', 'BOARDING']).optional(),
  delayMinutes: z.number().nullable().optional(),
});

export const flightStatusResponseSchema = z.object({
  flights: z.array(flightStatusSchema),
  lastUpdated: z.string(),
  totalFlights: z.number().optional(),
  route: z.string().optional(),
  date: z.string().optional(),
});

export const alternativesResponseSchema = z.object({
  alternatives: z.array(alternativeFlightSchema),
  originalFlight: z.string().optional(),
  totalAlternatives: z.number().optional(),
});

// TypeScript types derived from schemas
export type FlightStatus = z.infer<typeof flightStatusSchema>;
export type AlternativeFlight = z.infer<typeof alternativeFlightSchema>;
export type FlightStatusResponse = z.infer<typeof flightStatusResponseSchema>;
export type AlternativesResponse = z.infer<typeof alternativesResponseSchema>;

// API base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// API client with error handling
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async getFlightStatus(params: {
    from: string;
    to: string;
    date: string;
  }): Promise<FlightStatusResponse> {
    const searchParams = new URLSearchParams(params);
    const data = await this.request<unknown>(
      `/flights/status?${searchParams}`
    );
    
    // Validate response with Zod
    return flightStatusResponseSchema.parse(data);
  }

  async getAlternatives(flightNumber: string): Promise<AlternativesResponse> {
    const data = await this.request<unknown>(
      `/flights/alternatives?flightNumber=${encodeURIComponent(flightNumber)}`
    );
    
    // Validate response with Zod
    return alternativesResponseSchema.parse(data);
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);

// React Query keys
export const queryKeys = {
  flightStatus: (from: string, to: string, date: string) => 
    ['flightStatus', from, to, date] as const,
  alternatives: (flightNumber: string) => 
    ['alternatives', flightNumber] as const,
} as const;
