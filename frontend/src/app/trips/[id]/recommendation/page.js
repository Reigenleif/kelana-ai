'use client';

import React, { useState, useEffect, use } from 'react';
import { useParams, useRouter } from 'next/navigation';
import AIRecommendationView from '@/components/AIRecommendationView';
import { tripService, authService } from '@/service';
import { AlertCircle } from 'lucide-react';

export default function RecommendationPage({ params }) {
  const router = useRouter();
  const resolvedParams = use ? use(params) : useParams();
  const tripId = resolvedParams?.id;

  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    if (!tripId) return;

    const fetchTrip = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await tripService.getTrip(tripId);
        setTrip(data);
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/login');
          return;
        }
        setError(err.response?.data?.detail || err.message || 'Error loading trip details.');
      } finally {
        setLoading(false);
      }
    };

    fetchTrip();
  }, [tripId, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090d14] flex flex-col items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-rose-500/20 border-t-rose-500 rounded-full animate-spin mb-4" />
        <p className="text-xs text-slate-400">Loading trip information...</p>
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="min-h-screen bg-[#090d14] flex items-center justify-center p-4">
        <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center max-w-md">
          <AlertCircle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">Trip Not Found</h3>
          <p className="text-xs text-slate-400 mb-6">{error || 'This itinerary does not exist or belongs to another user.'}</p>
          <button
            onClick={() => router.push('/trips')}
            className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold"
          >
            Return to My Trips
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090d14] text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <AIRecommendationView initialTrip={trip} />
    </div>
  );
}
