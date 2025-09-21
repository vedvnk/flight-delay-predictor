# Flight Delay Predictor - Glassmorphic Web App

A production-ready, glassmorphic web application built with Next.js 14 that provides real-time flight delay predictions and alternative flight options. Features a modern glassmorphic design with smooth animations and comprehensive flight comparison tools.

## 🚀 Features

- **Real-time Flight Search**: Search flights by origin, destination, and date
- **Delay Predictions**: Get detailed delay information with risk assessments
- **Alternative Flights**: View and compare alternative flight options
- **Glassmorphic Design**: Modern, frosted glass aesthetic with smooth animations
- **Responsive Design**: Mobile-first approach with perfect responsiveness
- **Auto-refresh**: Optional automatic data refresh every 60 seconds
- **Flight Comparison**: Compare up to 3 alternative flights side-by-side
- **Accessibility**: WCAG AA compliant with keyboard navigation support
- **Performance**: Optimized with React Query caching and code splitting

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router) + TypeScript
- **Styling**: Tailwind CSS with custom glassmorphic utilities
- **Animations**: Framer Motion for smooth micro-interactions
- **State Management**: TanStack Query (React Query) for server state
- **Validation**: Zod for runtime schema validation
- **Icons**: Lucide React for consistent iconography
- **Testing**: Vitest + React Testing Library
- **Linting**: ESLint + Prettier

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flight-delay-glassmorphic
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env.local
   ```
   
   Edit `.env.local` and set your API base URL:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles and glassmorphic utilities
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Main application page
├── components/            # Reusable UI components
│   ├── AlternativesSheet.tsx
│   ├── CompareTray.tsx
│   ├── EmptyState.tsx
│   ├── ErrorState.tsx
│   ├── FlightCard.tsx
│   ├── LastUpdated.tsx
│   ├── SearchForm.tsx
│   └── Skeletons.tsx
├── hooks/                 # Custom React hooks
│   ├── useAlternatives.ts
│   └── useFlightStatus.ts
├── lib/                   # Utility libraries
│   ├── adapters/          # Data normalization
│   │   └── normalize.ts
│   ├── api.ts            # API client and schemas
│   ├── iata.ts           # IATA code utilities
│   ├── status.ts         # Status configuration
│   ├── time.ts           # Time formatting utilities
│   └── utils.ts          # General utilities
└── test/                 # Test setup
    └── setup.ts
```

## 🔌 API Integration

### Backend API Requirements

The application expects your backend to provide the following endpoints:

#### 1. Flight Status Endpoint
```
GET /flights/status?from=SEA&to=SFO&date=2025-09-21
```

**Expected Response:**
```json
{
  "flights": [
    {
      "flightNumber": "AA123",
      "airline": "American Airlines",
      "from": "SEA",
      "to": "SFO",
      "schedDep": "2025-09-21T09:30:00Z",
      "estDep": "2025-09-21T10:15:00Z",
      "gate": "B12",
      "status": "DELAYED",
      "delayMinutes": 45
    }
  ],
  "lastUpdated": "2025-09-21T08:55:00Z"
}
```

#### 2. Alternatives Endpoint
```
GET /flights/alternatives?flightNumber=AA123
```

**Expected Response:**
```json
{
  "alternatives": [
    {
      "flightNumber": "DL456",
      "airline": "Delta",
      "schedDep": "2025-09-21T09:55:00Z",
      "arrival": "2025-09-21T11:58:00Z",
      "from": "SEA",
      "to": "SFO",
      "seatsLeft": 4,
      "onTimeProbability": 0.82
    }
  ]
}
```

### Adapting to Your Backend

If your API response format differs, you can easily adapt it by modifying the following files:

#### 1. Update Zod Schemas (`src/lib/api.ts`)
```typescript
// Modify the schemas to match your API response
export const flightStatusSchema = z.object({
  // Update field names and types to match your API
  flightNumber: z.string(),
  // ... other fields
});
```

#### 2. Update Data Normalization (`src/lib/adapters/normalize.ts`)
```typescript
// Modify the normalization functions to map your API fields
export function normalizeFlight(flight: YourApiFlightType): NormalizedFlight {
  return {
    flightNumber: flight.your_flight_number_field,
    // ... map other fields
  };
}
```

#### 3. Update API Client (`src/lib/api.ts`)
```typescript
// Modify the API client methods if your endpoints differ
async getFlightStatus(params: YourParams): Promise<YourResponse> {
  // Update endpoint URL and parameters
  const data = await this.request<unknown>('/your/endpoint');
  return yourResponseSchema.parse(data);
}
```

## 🎨 Customization

### Glassmorphic Design

The app uses a custom glassmorphic design system. Key CSS classes:

- `.glass`: Basic glassmorphic container
- `.glass-card`: Elevated card with enhanced blur
- `.glass-input`: Styled form inputs

### Color Scheme

The app uses a dark theme with blue accents. To customize:

1. **Update Tailwind config** (`tailwind.config.ts`)
2. **Modify CSS variables** (`src/app/globals.css`)
3. **Update component styles** in individual component files

### Status Colors

Status colors are centralized in `src/lib/status.ts`:

- **ON TIME**: Emerald (green)
- **DELAYED**: Amber (yellow/orange)  
- **CANCELED**: Rose (red)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

### Writing Tests

Tests are located alongside components with `.test.tsx` or `.spec.tsx` extensions:

```typescript
// Example test file: src/components/FlightCard.test.tsx
import { render, screen } from '@testing-library/react';
import { FlightCard } from './FlightCard';

describe('FlightCard', () => {
  it('renders flight information correctly', () => {
    const mockFlight = {
      flightNumber: 'AA123',
      airline: 'American Airlines',
      // ... other required fields
    };
    
    render(<FlightCard flight={mockFlight} onViewAlternatives={jest.fn()} />);
    
    expect(screen.getByText('AA123')).toBeInTheDocument();
    expect(screen.getByText('American Airlines')).toBeInTheDocument();
  });
});
```

## 📱 Performance Optimization

### Lighthouse Scores Target
- **Performance**: ≥ 85
- **Accessibility**: ≥ 90  
- **Best Practices**: ≥ 90
- **SEO**: ≥ 90

### Optimization Features
- **Code Splitting**: Automatic route-based code splitting
- **Image Optimization**: Next.js Image component with lazy loading
- **Caching**: React Query with intelligent cache management
- **Bundle Analysis**: Use `npm run analyze` to inspect bundle size

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production
```env
NEXT_PUBLIC_API_BASE_URL=https://your-production-api.com
NODE_ENV=production
```

## 🔧 Development Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run format       # Format code with Prettier
npm run format:check # Check code formatting
npm run type-check   # Run TypeScript type checking

# Testing
npm test             # Run tests
npm run test:ui      # Run tests with UI
npm run test:coverage # Run tests with coverage
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
   - Check CORS settings on your backend
   - Ensure API endpoints match expected format

2. **Build Errors**
   - Run `npm run type-check` to identify TypeScript errors
   - Check for missing dependencies with `npm install`
   - Clear Next.js cache: `rm -rf .next`

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS classes
   - Verify glassmorphic utilities are imported

### Debug Mode

Enable debug mode by setting:
```env
NODE_ENV=development
```

This enables React Query DevTools and additional logging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style (Prettier + ESLint)
- Write tests for new features
- Update documentation for API changes
- Ensure accessibility compliance
- Test on multiple devices and browsers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Next.js Team** for the amazing framework
- **Tailwind CSS** for the utility-first CSS framework
- **Framer Motion** for smooth animations
- **TanStack Query** for excellent state management
- **Lucide** for beautiful icons

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the API integration guide

---

Built with ❤️ using Next.js 14 and modern web technologies.