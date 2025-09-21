import { format, parseISO, differenceInMinutes } from 'date-fns';
import { FlightStatus, AlternativeFlight } from '@/lib/api';

// Normalized types for UI consumption
export interface NormalizedFlight {
  flightNumber: string;
  airline: string;
  from: string;
  to: string;
  scheduledDeparture: Date;
  estimatedDeparture: Date | null;
  scheduledArrival: Date | null;
  estimatedArrival: Date | null;
  gate: string | null;
  status: 'ON_TIME' | 'DELAYED' | 'CANCELED' | 'LANDED' | 'SCHEDULED' | 'BOARDING';
  delayMinutes: number | null;
  // Delay risk information
  delayRisk?: 'LOW' | 'MEDIUM' | 'HIGH';
  delayRiskPercentage?: string;
  delayProbability?: number;
  // Derived fields
  isDelayed: boolean;
  delayText: string;
  departureTimeText: string;
  estimatedDepartureText: string;
  arrivalTimeText: string;
  estimatedArrivalText: string;
}

export interface NormalizedAlternative {
  flightNumber: string;
  airline: string;
  scheduledDeparture: Date;
  arrival: Date;
  from: string;
  to: string;
  seatsLeft: number;
  onTimeProbability: number;
  // Derived fields
  departureTimeText: string;
  arrivalTimeText: string;
  totalDuration: string;
  onTimePercentage: number;
  seatsStatus: 'available' | 'limited' | 'full';
}

// Status configuration
export const STATUS_CONFIG = {
  ON_TIME: {
    label: 'ON TIME',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
  },
  DELAYED: {
    label: 'DELAYED',
    color: 'amber',
    bgColor: 'bg-amber-400/20',
    textColor: 'text-amber-200',
    borderColor: 'border-amber-300/30',
  },
  CANCELED: {
    label: 'CANCELED',
    color: 'rose',
    bgColor: 'bg-rose-400/20',
    textColor: 'text-rose-200',
    borderColor: 'border-rose-300/30',
  },
  LANDED: {
    label: 'LANDED',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
  },
  SCHEDULED: {
    label: 'SCHEDULED',
    color: 'blue',
    bgColor: 'bg-blue-400/20',
    textColor: 'text-blue-200',
    borderColor: 'border-blue-300/30',
  },
  BOARDING: {
    label: 'BOARDING',
    color: 'purple',
    bgColor: 'bg-purple-400/20',
    textColor: 'text-purple-200',
    borderColor: 'border-purple-300/30',
  },
} as const;

// Helper function to get status config with fallback
export function getStatusConfig(status: string) {
  return STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] || {
    label: status || 'UNKNOWN',
    color: 'gray',
    bgColor: 'bg-gray-400/20',
    textColor: 'text-gray-200',
    borderColor: 'border-gray-300/30',
  };
}

// Normalize flight status from API to UI format
export function normalizeFlight(flight: FlightStatus): NormalizedFlight {
  const scheduledDeparture = parseISO(flight.schedDep);
  const estimatedDeparture = flight.estDep ? parseISO(flight.estDep) : null;
  const scheduledArrival = flight.schedArr ? parseISO(flight.schedArr) : null;
  const estimatedArrival = flight.estArr ? parseISO(flight.estArr) : null;
  
  const delayMinutes = flight.delayMinutes || 
    (estimatedDeparture ? differenceInMinutes(estimatedDeparture, scheduledDeparture) : null);
  
  const isDelayed = flight.status === 'DELAYED' && delayMinutes && delayMinutes > 0;
  
  return {
    flightNumber: flight.flightNumber,
    airline: flight.airline,
    from: flight.from,
    to: flight.to,
    scheduledDeparture,
    estimatedDeparture,
    scheduledArrival,
    estimatedArrival,
    gate: flight.gate,
    status: flight.status,
    delayMinutes,
    delayRisk: flight.delayRisk,
    delayRiskPercentage: flight.delayRiskPercentage,
    delayProbability: flight.delayProbability,
    isDelayed,
    delayText: getDelayText(delayMinutes),
    departureTimeText: format(scheduledDeparture, 'HH:mm'),
    estimatedDepartureText: estimatedDeparture ? format(estimatedDeparture, 'HH:mm') : '',
    arrivalTimeText: scheduledArrival ? format(scheduledArrival, 'HH:mm') : '',
    estimatedArrivalText: estimatedArrival ? format(estimatedArrival, 'HH:mm') : '',
  };
}

// Normalize alternative flight from API to UI format
export function normalizeAlternative(alternative: AlternativeFlight): NormalizedAlternative {
  const scheduledDeparture = parseISO(alternative.schedDep);
  const arrival = parseISO(alternative.schedArr);
  
  const totalDurationMinutes = differenceInMinutes(arrival, scheduledDeparture);
  const totalDuration = formatDuration(totalDurationMinutes);
  
  const seatsStatus = getSeatsStatus(alternative.seatsLeft);
  
  return {
    flightNumber: alternative.flightNumber,
    airline: alternative.airline,
    scheduledDeparture,
    arrival,
    from: alternative.from,
    to: alternative.to,
    seatsLeft: alternative.seatsLeft,
    onTimeProbability: alternative.onTimeProbability,
    departureTimeText: format(scheduledDeparture, 'HH:mm'),
    arrivalTimeText: format(arrival, 'HH:mm'),
    totalDuration,
    onTimePercentage: Math.round(alternative.onTimeProbability * 100),
    seatsStatus,
  };
}

// Helper functions
function getDelayText(delayMinutes: number | null): string {
  if (!delayMinutes || delayMinutes <= 0) return '';
  
  if (delayMinutes < 60) {
    return `+${delayMinutes}m`;
  }
  
  const hours = Math.floor(delayMinutes / 60);
  const minutes = delayMinutes % 60;
  
  if (minutes === 0) {
    return `+${hours}h`;
  }
  
  return `+${hours}h ${minutes}m`;
}

function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `${hours}h`;
  }
  
  return `${hours}h ${remainingMinutes}m`;
}

function getSeatsStatus(seatsLeft: number): 'available' | 'limited' | 'full' {
  if (seatsLeft === 0) return 'full';
  if (seatsLeft <= 3) return 'limited';
  return 'available';
}

// Batch normalization functions
export function normalizeFlights(flights: FlightStatus[]): NormalizedFlight[] {
  return flights.map(normalizeFlight);
}

export function normalizeAlternatives(alternatives: AlternativeFlight[]): NormalizedAlternative[] {
  return alternatives.map(normalizeAlternative);
}
