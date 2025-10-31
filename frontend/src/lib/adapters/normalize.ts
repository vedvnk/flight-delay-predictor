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
  gate: string | null;
  status: 'ON_TIME' | 'DELAYED' | 'CANCELED';
  delayMinutes: number | null;
  // Derived fields
  isDelayed: boolean;
  delayText: string;
  departureTimeText: string;
  estimatedTimeText: string;
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
} as const;

// Normalize flight status from API to UI format
export function normalizeFlight(flight: FlightStatus): NormalizedFlight {
  const scheduledDeparture = parseISO(flight.schedDep);
  const estimatedDeparture = flight.estDep ? parseISO(flight.estDep) : null;
  
  const delayMinutes = flight.delayMinutes || 
    (estimatedDeparture ? differenceInMinutes(estimatedDeparture, scheduledDeparture) : null);
  
  const isDelayed = flight.status === 'DELAYED' && delayMinutes && delayMinutes > 0;
  
  return {
    flightNumber: flight.flightNumber,
    airline: typeof flight.airline === 'string'
      ? flight.airline
      : (flight.airline?.name || flight.airline?.code || 'Unknown Airline'),
    from: flight.from,
    to: flight.to,
    scheduledDeparture,
    estimatedDeparture,
    gate: flight.gate,
    status: flight.status,
    delayMinutes,
    isDelayed,
    delayText: getDelayText(delayMinutes),
    departureTimeText: format(scheduledDeparture, 'HH:mm'),
    estimatedTimeText: estimatedDeparture ? format(estimatedDeparture, 'HH:mm') : '',
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
