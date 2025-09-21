'use client';

import { useState } from 'react';

export function DebugApiTest() {
  const [result, setResult] = useState<string>('Not tested');
  const [loading, setLoading] = useState(false);

  const testApi = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/flights/status?from=LAX&to=ORD&date=2025-09-21');
      if (response.ok) {
        const data = await response.json();
        setResult(`Success: Found ${data.flights?.length || 0} flights`);
      } else {
        setResult(`Error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      setResult(`Network Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white/10 border border-white/20 rounded-xl p-4 mb-4">
      <h3 className="text-white font-semibold mb-2">API Debug Test</h3>
      <button
        onClick={testApi}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API'}
      </button>
      <p className="text-white/70 mt-2">Result: {result}</p>
    </div>
  );
}
