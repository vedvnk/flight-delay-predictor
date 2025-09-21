// IATA code validation and utilities

// Common IATA airport codes for reference
export const COMMON_AIRPORTS = {
  // US Major Hubs
  'ATL': 'Atlanta',
  'LAX': 'Los Angeles',
  'ORD': 'Chicago O\'Hare',
  'DFW': 'Dallas/Fort Worth',
  'DEN': 'Denver',
  'JFK': 'New York JFK',
  'SFO': 'San Francisco',
  'SEA': 'Seattle',
  'LAS': 'Las Vegas',
  'MIA': 'Miami',
  'BOS': 'Boston',
  'PHX': 'Phoenix',
  'EWR': 'Newark',
  'DTW': 'Detroit',
  'MSP': 'Minneapolis',
  'CLT': 'Charlotte',
  'PHL': 'Philadelphia',
  'LGA': 'New York LaGuardia',
  'BWI': 'Baltimore',
  'DCA': 'Washington Reagan',
  'IAH': 'Houston Intercontinental',
  'MCO': 'Orlando',
  'FLL': 'Fort Lauderdale',
  'TPA': 'Tampa',
  'PDX': 'Portland',
  'SAN': 'San Diego',
  'STL': 'St. Louis',
  'BNA': 'Nashville',
  'AUS': 'Austin',
  'SLC': 'Salt Lake City',
  // International
  'LHR': 'London Heathrow',
  'CDG': 'Paris Charles de Gaulle',
  'FRA': 'Frankfurt',
  'AMS': 'Amsterdam',
  'MAD': 'Madrid',
  'FCO': 'Rome',
  'BCN': 'Barcelona',
  'VIE': 'Vienna',
  'ZUR': 'Zurich',
  'DUB': 'Dublin',
  'YYZ': 'Toronto',
  'YVR': 'Vancouver',
  'NRT': 'Tokyo Narita',
  'ICN': 'Seoul Incheon',
  'PEK': 'Beijing',
  'PVG': 'Shanghai Pudong',
  'HKG': 'Hong Kong',
  'SIN': 'Singapore',
  'DXB': 'Dubai',
  'IST': 'Istanbul',
  'DOH': 'Doha',
  'SYD': 'Sydney',
  'MEL': 'Melbourne',
  'GRU': 'São Paulo',
  'EZE': 'Buenos Aires',
  'LIM': 'Lima',
  'SCL': 'Santiago',
} as const;

export type AirportCode = keyof typeof COMMON_AIRPORTS;

// IATA code validation regex
const IATA_REGEX = /^[A-Z]{3}$/;

// Validate IATA code format
export function isValidIATACode(code: string): boolean {
  return IATA_REGEX.test(code);
}

// Get airport name from IATA code
export function getAirportName(code: string): string {
  return COMMON_AIRPORTS[code as AirportCode] || code;
}

// Format IATA code for display
export function formatIATACode(code: string): string {
  if (!isValidIATACode(code)) return code;
  return code.toUpperCase();
}

// Get airport suggestions based on partial input
export function getAirportSuggestions(input: string, limit: number = 10): Array<{
  code: string;
  name: string;
  fullText: string;
}> {
  if (input.length < 1) return [];
  
  const query = input.toUpperCase();
  const suggestions: Array<{
    code: string;
    name: string;
    fullText: string;
  }> = [];
  
  // Search by code first
  for (const [code, name] of Object.entries(COMMON_AIRPORTS)) {
    if (code.includes(query)) {
      suggestions.push({
        code,
        name,
        fullText: `${code} - ${name}`,
      });
    }
  }
  
  // Then search by name
  for (const [code, name] of Object.entries(COMMON_AIRPORTS)) {
    if (name.toLowerCase().includes(input.toLowerCase()) && 
        !suggestions.some(s => s.code === code)) {
      suggestions.push({
        code,
        name,
        fullText: `${code} - ${name}`,
      });
    }
  }
  
  return suggestions.slice(0, limit);
}

// Validate flight route (from and to should be different)
export function isValidRoute(from: string, to: string): boolean {
  return isValidIATACode(from) && 
         isValidIATACode(to) && 
         from !== to;
}

// Get route display text
export function getRouteDisplay(from: string, to: string): string {
  const fromName = getAirportName(from);
  const toName = getAirportName(to);
  return `${from} → ${to}`;
}

// Get route subtitle with airport names
export function getRouteSubtitle(from: string, to: string): string {
  const fromName = getAirportName(from);
  const toName = getAirportName(to);
  return `${fromName} to ${toName}`;
}
