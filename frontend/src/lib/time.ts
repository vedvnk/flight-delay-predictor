import { format, parseISO, differenceInMinutes, formatDistanceToNow, isToday, isTomorrow, isYesterday } from 'date-fns';

// Time zone utilities
export function formatLocalTime(date: Date | string, timeZone?: string): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  
  if (timeZone) {
    return new Intl.DateTimeFormat('en-US', {
      timeZone,
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(dateObj);
  }
  
  return format(dateObj, 'HH:mm');
}

export function formatLocalDateTime(date: Date | string, timeZone?: string): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  
  if (timeZone) {
    return new Intl.DateTimeFormat('en-US', {
      timeZone,
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(dateObj);
  }
  
  return format(dateObj, 'MMM dd, HH:mm');
}

// Duration formatting
export function formatDuration(minutes: number): string {
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

export function formatDurationLong(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  }
  
  return `${hours} hour${hours !== 1 ? 's' : ''} ${remainingMinutes} minute${remainingMinutes !== 1 ? 's' : ''}`;
}

// Delay formatting
export function formatDelay(minutes: number | null): string {
  if (!minutes || minutes <= 0) return '';
  
  if (minutes < 60) {
    return `+${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `+${hours}h`;
  }
  
  return `+${hours}h ${remainingMinutes}m`;
}

export function formatDelayLong(minutes: number | null): string {
  if (!minutes || minutes <= 0) return 'No delay';
  
  return `${formatDurationLong(minutes)} late`;
}

// Relative time formatting
export function formatRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistanceToNow(dateObj, { addSuffix: true });
}

export function formatRelativeTimeShort(date: Date | string): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  
  if (isToday(dateObj)) {
    return 'Today';
  }
  
  if (isTomorrow(dateObj)) {
    return 'Tomorrow';
  }
  
  if (isYesterday(dateObj)) {
    return 'Yesterday';
  }
  
  return formatRelativeTime(dateObj);
}

// Time comparison utilities
export function getTimeDifference(start: Date | string, end: Date | string): number {
  const startDate = typeof start === 'string' ? parseISO(start) : start;
  const endDate = typeof end === 'string' ? parseISO(end) : end;
  
  return differenceInMinutes(endDate, startDate);
}

export function isDelayed(scheduled: Date | string, estimated: Date | string | null): boolean {
  if (!estimated) return false;
  
  const scheduledDate = typeof scheduled === 'string' ? parseISO(scheduled) : scheduled;
  const estimatedDate = typeof estimated === 'string' ? parseISO(estimated) : estimated;
  
  return estimatedDate > scheduledDate;
}

export function getDelayMinutes(scheduled: Date | string, estimated: Date | string | null): number | null {
  if (!estimated) return null;
  
  const scheduledDate = typeof scheduled === 'string' ? parseISO(scheduled) : scheduled;
  const estimatedDate = typeof estimated === 'string' ? parseISO(estimated) : estimated;
  
  const delayMinutes = differenceInMinutes(estimatedDate, scheduledDate);
  return delayMinutes > 0 ? delayMinutes : null;
}

// Date formatting for forms
export function formatDateForInput(date: Date): string {
  return format(date, 'yyyy-MM-dd');
}

export function formatDateTimeForInput(date: Date): string {
  return format(date, "yyyy-MM-dd'T'HH:mm");
}

// Time zone abbreviations (common ones)
export const TIME_ZONE_ABBREVIATIONS = {
  'America/New_York': 'EST/EDT',
  'America/Chicago': 'CST/CDT',
  'America/Denver': 'MST/MDT',
  'America/Los_Angeles': 'PST/PDT',
  'America/Phoenix': 'MST',
  'America/Anchorage': 'AKST/AKDT',
  'Pacific/Honolulu': 'HST',
  'Europe/London': 'GMT/BST',
  'Europe/Paris': 'CET/CEST',
  'Europe/Berlin': 'CET/CEST',
  'Europe/Rome': 'CET/CEST',
  'Europe/Madrid': 'CET/CEST',
  'Asia/Tokyo': 'JST',
  'Asia/Shanghai': 'CST',
  'Asia/Hong_Kong': 'HKT',
  'Asia/Singapore': 'SGT',
  'Asia/Dubai': 'GST',
  'Australia/Sydney': 'AEST/AEDT',
  'Australia/Melbourne': 'AEST/AEDT',
} as const;

export function getTimeZoneAbbreviation(timeZone: string): string {
  return TIME_ZONE_ABBREVIATIONS[timeZone as keyof typeof TIME_ZONE_ABBREVIATIONS] || timeZone;
}
