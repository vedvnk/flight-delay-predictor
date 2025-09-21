'use client';

import { motion } from 'framer-motion';

// Skeleton for flight cards
export function FlightCardSkeleton() {
  return (
    <div className="relative overflow-hidden rounded-2xl glass-morphism-advanced">
      <div className="p-6">
        {/* Header skeleton */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl loading-shimmer" />
            <div>
              <div className="h-5 w-20 loading-shimmer rounded mb-2" />
              <div className="h-4 w-24 loading-shimmer rounded" />
            </div>
          </div>
          <div className="h-6 w-16 loading-shimmer rounded-full" />
        </div>

        {/* Route skeleton */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-center">
                <div className="h-8 w-16 loading-shimmer rounded mb-2" />
                <div className="h-3 w-8 loading-shimmer rounded" />
              </div>
              <div className="w-5 h-5 loading-shimmer rounded" />
              <div className="text-center">
                <div className="h-8 w-16 loading-shimmer rounded mb-2" />
                <div className="h-3 w-8 loading-shimmer rounded" />
              </div>
            </div>
          </div>

          {/* Additional info skeleton */}
          <div className="flex items-center space-x-4">
            <div className="h-4 w-20 loading-shimmer rounded" />
            <div className="h-4 w-24 loading-shimmer rounded" />
          </div>
        </div>

        {/* Button skeleton */}
        <div className="mt-6 pt-4 border-t border-white/10">
          <div className="h-10 w-full loading-shimmer rounded-xl" />
        </div>
      </div>
    </div>
  );
}

// Skeleton for alternatives sheet
export function AlternativesSheetSkeleton() {
  return (
    <div className="fixed right-0 top-0 h-full w-full max-w-md glass-morphism-advanced border-l border-white/15 shadow-[0_0_50px_rgba(2,6,23,0.5)] z-50 overflow-hidden">
      <div className="flex flex-col h-full">
        {/* Header skeleton */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <div className="h-6 w-32 loading-shimmer rounded mb-2" />
            <div className="h-4 w-24 loading-shimmer rounded" />
          </div>
          <div className="w-8 h-8 loading-shimmer rounded-xl" />
        </div>

        {/* Original flight skeleton */}
        <div className="p-6 border-b border-white/10">
          <div className="h-4 w-24 loading-shimmer rounded mb-3" />
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="h-5 w-16 loading-shimmer rounded" />
              <div className="h-4 w-12 loading-shimmer rounded" />
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-4 w-12 loading-shimmer rounded" />
              <div className="w-4 h-4 loading-shimmer rounded" />
              <div className="h-4 w-12 loading-shimmer rounded" />
            </div>
          </div>
        </div>

        {/* Alternatives list skeleton */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="glass-morphism-advanced rounded-xl p-4">
              {/* Flight header */}
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="h-5 w-16 loading-shimmer rounded mb-2" />
                  <div className="h-4 w-24 loading-shimmer rounded" />
                </div>
                <div className="text-right">
                  <div className="h-6 w-12 loading-shimmer rounded mb-1" />
                  <div className="h-3 w-16 loading-shimmer rounded" />
                </div>
              </div>

              {/* Times */}
              <div className="flex items-center space-x-2 mb-4">
                <div className="h-6 w-12 loading-shimmer rounded" />
                <div className="w-4 h-4 loading-shimmer rounded" />
                <div className="h-6 w-12 loading-shimmer rounded" />
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                  <div className="h-4 w-16 loading-shimmer rounded mb-2" />
                  <div className="flex items-center justify-between">
                    <div className="h-4 w-8 loading-shimmer rounded" />
                    <div className="h-5 w-12 loading-shimmer rounded-full" />
                  </div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                  <div className="h-4 w-16 loading-shimmer rounded mb-2" />
                  <div className="flex items-center justify-between">
                    <div className="h-4 w-8 loading-shimmer rounded" />
                    <div className="h-5 w-12 loading-shimmer rounded-full" />
                  </div>
                </div>
              </div>

              {/* Buttons */}
              <div className="flex space-x-2">
                <div className="flex-1 h-8 loading-shimmer rounded-lg" />
                <div className="flex-1 h-8 loading-shimmer rounded-lg" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Skeleton for search form
export function SearchFormSkeleton() {
  return (
    <div className="glass-morphism-advanced rounded-2xl p-6">
      <div className="space-y-6">
        {/* Title */}
        <div className="h-8 w-48 loading-shimmer rounded" />
        
        {/* Form fields */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <div className="h-4 w-16 loading-shimmer rounded" />
            <div className="h-12 w-full loading-shimmer rounded-xl" />
          </div>
          <div className="space-y-2">
            <div className="h-4 w-16 loading-shimmer rounded" />
            <div className="h-12 w-full loading-shimmer rounded-xl" />
          </div>
          <div className="space-y-2">
            <div className="h-4 w-16 loading-shimmer rounded" />
            <div className="h-12 w-full loading-shimmer rounded-xl" />
          </div>
          <div className="space-y-2">
            <div className="h-4 w-16 loading-shimmer rounded" />
            <div className="h-12 w-full loading-shimmer rounded-xl" />
          </div>
        </div>
      </div>
    </div>
  );
}

// Skeleton for compare tray
export function CompareTraySkeleton() {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="glass-morphism-advanced rounded-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div className="h-6 w-32 loading-shimmer rounded" />
            <div className="h-8 w-16 loading-shimmer rounded-lg" />
          </div>

          {/* Table skeleton */}
          <div className="p-4">
            <div className="space-y-4">
              {Array.from({ length: 2 }).map((_, index) => (
                <div key={index} className="grid grid-cols-12 gap-4 p-4 border border-white/10 rounded-lg">
                  <div className="col-span-2">
                    <div className="h-5 w-16 loading-shimmer rounded mb-2" />
                    <div className="h-3 w-20 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-2">
                    <div className="h-4 w-20 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-2">
                    <div className="h-5 w-12 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-2">
                    <div className="h-5 w-12 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-1">
                    <div className="h-4 w-8 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-1">
                    <div className="h-4 w-8 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-1">
                    <div className="h-4 w-8 loading-shimmer rounded" />
                  </div>
                  <div className="col-span-1">
                    <div className="h-8 w-8 loading-shimmer rounded-lg" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
