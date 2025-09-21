import { FlightStatusResponse, AlternativesResponse } from './api';

// Mock flight data generator
const airlines = ['American Airlines', 'Delta', 'United', 'Southwest', 'JetBlue', 'Alaska Airlines'];
const airports = ['SEA', 'SFO', 'LAX', 'JFK', 'ORD', 'DFW', 'ATL', 'DEN', 'LAS', 'PHX'];
const statuses = ['ON_TIME', 'DELAYED', 'CANCELED'] as const;

// Generate random flight number
const generateFlightNumber = (airline: string): string => {
  const airlineCodes: Record<string, string> = {
    'American Airlines': 'AA',
    'Delta': 'DL',
    'United': 'UA',
    'Southwest': 'WN',
    'JetBlue': 'B6',
    'Alaska Airlines': 'AS'
  };
  
  const code = airlineCodes[airline] || 'XX';
  const number = Math.floor(Math.random() * 9000) + 1000;
  return `${code}${number}`;
};

// Generate random time
const generateTime = (baseHour: number = 6): string => {
  const hour = baseHour + Math.floor(Math.random() * 16); // 6 AM to 10 PM
  const minute = Math.floor(Math.random() * 4) * 15; // 0, 15, 30, 45
  return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
};

// Generate estimated time with potential delay
const generateEstimatedTime = (scheduledTime: string, status: string): string | null => {
  if (status === 'CANCELED') return null;
  if (status === 'ON_TIME') return scheduledTime;
  
  // Add delay
  const [hour, minute] = scheduledTime.split(':').map(Number);
  const delayMinutes = Math.floor(Math.random() * 120) + 15; // 15-135 minutes delay
  const totalMinutes = hour * 60 + minute + delayMinutes;
  const newHour = Math.floor(totalMinutes / 60) % 24;
  const newMinute = totalMinutes % 60;
  
  return `${newHour.toString().padStart(2, '0')}:${newMinute.toString().padStart(2, '0')}`;
};

// Generate gate number
const generateGate = (): string | null => {
  if (Math.random() < 0.1) return null; // 10% chance of no gate
  const terminal = String.fromCharCode(65 + Math.floor(Math.random() * 4)); // A-D
  const gate = Math.floor(Math.random() * 50) + 1;
  return `${terminal}${gate}`;
};

// Mock API client
class MockApiClient {
  async getFlightStatus(params: {
    from: string;
    to: string;
    date: string;
  }): Promise<FlightStatusResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));
    
    const numFlights = Math.floor(Math.random() * 8) + 3; // 3-10 flights
    const flights = [];
    
    for (let i = 0; i < numFlights; i++) {
      const airline = airlines[Math.floor(Math.random() * airlines.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      const scheduledTime = generateTime(6 + i * 2); // Spread flights throughout day
      const estimatedTime = generateEstimatedTime(scheduledTime, status);
      const delayMinutes = status === 'DELAYED' ? Math.floor(Math.random() * 120) + 15 : null;
      
      flights.push({
        flightNumber: generateFlightNumber(airline),
        airline,
        from: params.from,
        to: params.to,
        schedDep: scheduledTime,
        estDep: estimatedTime,
        gate: generateGate(),
        status,
        delayMinutes,
      });
    }
    
    // Sort flights by scheduled departure time
    flights.sort((a, b) => a.schedDep.localeCompare(b.schedDep));
    
    return {
      flights,
      lastUpdated: new Date().toISOString(),
    };
  }
  
  async getAlternatives(flightNumber: string): Promise<AlternativesResponse> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 600 + Math.random() * 800));
    
    const numAlternatives = Math.floor(Math.random() * 5) + 2; // 2-6 alternatives
    const alternatives = [];
    
    for (let i = 0; i < numAlternatives; i++) {
      const airline = airlines[Math.floor(Math.random() * airlines.length)];
      const scheduledTime = generateTime(6 + i * 3);
      const arrivalTime = generateTime(8 + i * 3);
      const seatsLeft = Math.floor(Math.random() * 20);
      const onTimeProbability = Math.random() * 0.4 + 0.6; // 60-100%
      
      alternatives.push({
        flightNumber: generateFlightNumber(airline),
        airline,
        schedDep: scheduledTime,
        schedArr: arrivalTime,
        from: 'SEA', // Default for demo
        to: 'SFO', // Default for demo
        seatsLeft,
        onTimeProbability,
      });
    }
    
    return {
      alternatives,
    };
  }
}

export const mockApiClient = new MockApiClient();
