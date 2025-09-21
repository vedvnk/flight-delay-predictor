// Flight status configuration and utilities

export type FlightStatus = 'ON_TIME' | 'DELAYED' | 'CANCELED' | 'LANDED' | 'SCHEDULED' | 'BOARDING';
export type DelayRisk = 'LOW' | 'MEDIUM' | 'HIGH';

export interface StatusConfig {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
  icon: string;
  description: string;
}

export const STATUS_CONFIG: Record<FlightStatus, StatusConfig> = {
  ON_TIME: {
    label: 'ON TIME',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
    icon: 'CheckCircle',
    description: 'Flight is on schedule',
  },
  DELAYED: {
    label: 'DELAYED',
    color: 'amber',
    bgColor: 'bg-amber-400/20',
    textColor: 'text-amber-200',
    borderColor: 'border-amber-300/30',
    icon: 'Clock',
    description: 'Flight is delayed',
  },
  CANCELED: {
    label: 'CANCELED',
    color: 'rose',
    bgColor: 'bg-rose-400/20',
    textColor: 'text-rose-200',
    borderColor: 'border-rose-300/30',
    icon: 'XCircle',
    description: 'Flight has been canceled',
  },
  LANDED: {
    label: 'LANDED',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
    icon: 'CheckCircle',
    description: 'Flight has landed',
  },
  SCHEDULED: {
    label: 'SCHEDULED',
    color: 'blue',
    bgColor: 'bg-blue-400/20',
    textColor: 'text-blue-200',
    borderColor: 'border-blue-300/30',
    icon: 'Clock',
    description: 'Flight is scheduled',
  },
  BOARDING: {
    label: 'BOARDING',
    color: 'purple',
    bgColor: 'bg-purple-400/20',
    textColor: 'text-purple-200',
    borderColor: 'border-purple-300/30',
    icon: 'Users',
    description: 'Flight is boarding',
  },
};

// Delay risk configuration
export const DELAY_RISK_CONFIG: Record<DelayRisk, StatusConfig> = {
  LOW: {
    label: 'LOW RISK',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
    icon: 'CheckCircle',
    description: 'Low chance of delay',
  },
  MEDIUM: {
    label: 'MEDIUM RISK',
    color: 'amber',
    bgColor: 'bg-amber-400/20',
    textColor: 'text-amber-200',
    borderColor: 'border-amber-300/30',
    icon: 'Clock',
    description: 'Medium chance of delay',
  },
  HIGH: {
    label: 'HIGH RISK',
    color: 'rose',
    bgColor: 'bg-rose-400/20',
    textColor: 'text-rose-200',
    borderColor: 'border-rose-300/30',
    icon: 'AlertTriangle',
    description: 'High chance of delay',
  },
};

// Get status configuration
export function getStatusConfig(status: string): StatusConfig {
  return STATUS_CONFIG[status as FlightStatus] || {
    label: status || 'UNKNOWN',
    color: 'gray',
    bgColor: 'bg-gray-400/20',
    textColor: 'text-gray-200',
    borderColor: 'border-gray-300/30',
    icon: 'HelpCircle',
    description: 'Unknown status',
  };
}

// Get delay risk configuration
export function getDelayRiskConfig(risk: string): StatusConfig {
  return DELAY_RISK_CONFIG[risk as DelayRisk] || {
    label: 'UNKNOWN',
    color: 'gray',
    bgColor: 'bg-gray-400/20',
    textColor: 'text-gray-200',
    borderColor: 'border-gray-300/30',
    icon: 'HelpCircle',
    description: 'Unknown delay risk',
  };
}

// Get status pill classes
export function getStatusPillClasses(status: FlightStatus): string {
  const config = getStatusConfig(status);
  return `inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor}`;
}

// Get delay severity
export type DelaySeverity = 'none' | 'minor' | 'moderate' | 'severe';

export function getDelaySeverity(delayMinutes: number | null): DelaySeverity {
  if (!delayMinutes || delayMinutes <= 0) return 'none';
  if (delayMinutes <= 30) return 'minor';
  if (delayMinutes <= 120) return 'moderate';
  return 'severe';
}

export const DELAY_SEVERITY_CONFIG: Record<DelaySeverity, {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
  icon: string;
}> = {
  none: {
    label: 'On Time',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
    icon: 'CheckCircle',
  },
  minor: {
    label: 'Minor Delay',
    color: 'blue',
    bgColor: 'bg-blue-400/20',
    textColor: 'text-blue-200',
    borderColor: 'border-blue-300/30',
    icon: 'Clock',
  },
  moderate: {
    label: 'Moderate Delay',
    color: 'amber',
    bgColor: 'bg-amber-400/20',
    textColor: 'text-amber-200',
    borderColor: 'border-amber-300/30',
    icon: 'AlertTriangle',
  },
  severe: {
    label: 'Severe Delay',
    color: 'rose',
    bgColor: 'bg-rose-400/20',
    textColor: 'text-rose-200',
    borderColor: 'border-rose-300/30',
    icon: 'AlertCircle',
  },
};

// Get delay severity configuration
export function getDelaySeverityConfig(severity: DelaySeverity) {
  return DELAY_SEVERITY_CONFIG[severity];
}

// Get delay severity classes
export function getDelaySeverityClasses(severity: DelaySeverity): string {
  const config = getDelaySeverityConfig(severity);
  return `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor}`;
}

// Seat availability status
export type SeatAvailability = 'available' | 'limited' | 'full';

export function getSeatAvailability(seatsLeft: number): SeatAvailability {
  if (seatsLeft === 0) return 'full';
  if (seatsLeft <= 3) return 'limited';
  return 'available';
}

export const SEAT_AVAILABILITY_CONFIG: Record<SeatAvailability, {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
  icon: string;
}> = {
  available: {
    label: 'Available',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
    icon: 'Users',
  },
  limited: {
    label: 'Limited',
    color: 'amber',
    bgColor: 'bg-amber-400/20',
    textColor: 'text-amber-200',
    borderColor: 'border-amber-300/30',
    icon: 'UserMinus',
  },
  full: {
    label: 'Full',
    color: 'rose',
    bgColor: 'bg-rose-400/20',
    textColor: 'text-rose-200',
    borderColor: 'border-rose-300/30',
    icon: 'UserX',
  },
};

// Get seat availability configuration
export function getSeatAvailabilityConfig(availability: SeatAvailability) {
  return SEAT_AVAILABILITY_CONFIG[availability];
}

// Get seat availability classes
export function getSeatAvailabilityClasses(availability: SeatAvailability): string {
  const config = getSeatAvailabilityConfig(availability);
  return `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor}`;
}

// On-time probability status
export type OnTimeProbabilityStatus = 'excellent' | 'good' | 'fair' | 'poor';

export function getOnTimeProbabilityStatus(probability: number): OnTimeProbabilityStatus {
  if (probability >= 0.9) return 'excellent';
  if (probability >= 0.75) return 'good';
  if (probability >= 0.6) return 'fair';
  return 'poor';
}

export const ON_TIME_PROBABILITY_CONFIG: Record<OnTimeProbabilityStatus, {
  label: string;
  color: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
  icon: string;
  percentage: string;
}> = {
  excellent: {
    label: 'Excellent',
    color: 'emerald',
    bgColor: 'bg-emerald-400/20',
    textColor: 'text-emerald-200',
    borderColor: 'border-emerald-300/30',
    icon: 'TrendingUp',
    percentage: '≥90%',
  },
  good: {
    label: 'Good',
    color: 'blue',
    bgColor: 'bg-blue-400/20',
    textColor: 'text-blue-200',
    borderColor: 'border-blue-300/30',
    icon: 'TrendingUp',
    percentage: '75-89%',
  },
  fair: {
    label: 'Fair',
    color: 'amber',
    bgColor: 'bg-amber-400/20',
    textColor: 'text-amber-200',
    borderColor: 'border-amber-300/30',
    icon: 'TrendingDown',
    percentage: '60-74%',
  },
  poor: {
    label: 'Poor',
    color: 'rose',
    bgColor: 'bg-rose-400/20',
    textColor: 'text-rose-200',
    borderColor: 'border-rose-300/30',
    icon: 'TrendingDown',
    percentage: '<60%',
  },
};

// Get on-time probability configuration
export function getOnTimeProbabilityConfig(status: OnTimeProbabilityStatus) {
  return ON_TIME_PROBABILITY_CONFIG[status];
}

// Get on-time probability classes
export function getOnTimeProbabilityClasses(status: OnTimeProbabilityStatus): string {
  const config = getOnTimeProbabilityConfig(status);
  return `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor}`;
}
