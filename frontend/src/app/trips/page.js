'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { MapPin, Plus, Compass, AlertCircle } from 'lucide-react';
import { tripService, authService } from '@/service';
import TripCard from '@/components/TripCard';

export default function TripsDashboardPage() {
  const router = useRouter();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  const fetchTrips = async () => {
    setLoading(true);
    setError(null);
    try {
      if (!authService.isAuthenticated()) {
        router.push('/login');
        return;
      }
      const data = await tripService.getTrips();
      setTrips(data);
    } catch (err) {
      if (err.response?.status === 401) {
        router.push('/login');
        return;
      }
      setError(err.response?.data?.detail || err.message || 'Failed to load your trips.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentUser(authService.getCurrentUser());
    fetchTrips();
  }, []);

  const handleDeleteTrip = async (tripId) => {
    try {
      await tripService.deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Error deleting trip');
    }
  };

  return (
    <div className="min-h-screen bg-[#090d14] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Top Header & Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-rose-400 mb-1">
            <Compass className="w-3.5 h-3.5" />
            <span>Traveler Dashboard</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            {currentUser ? `${currentUser.full_name || currentUser.username}'s Trips` : 'My Trips'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage your personalized itineraries and AI-generated travel recommendations
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/trips/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold text-xs shadow-lg shadow-rose-600/30 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            <span>Plan New Trip</span>
          </Link>
        </div>
      </div>

      {/* Loading state */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-rose-500/30 border-t-rose-500 rounded-full animate-spin mb-4" />
          <p className="text-xs font-medium text-slate-400">Loading your itineraries...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-900/40 text-center max-w-md mx-auto my-12">
          <AlertCircle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
          <h3 className="font-bold text-white mb-1">Failed to Load Trips</h3>
          <p className="text-xs text-slate-400 mb-4">{error}</p>
          <button
            onClick={fetchTrips}
            className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold transition-colors"
          >
            Retry Connection
          </button>
        </div>
      ) : trips.length === 0 ? (
        <div className="text-center py-16 px-4 bg-slate-900/40 border border-slate-800/80 rounded-3xl max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-rose-600/15 border border-rose-500/30 flex items-center justify-center text-rose-400 mx-auto mb-4">
            <MapPin className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-white">No Trips Found</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
            You have not added any trips yet. Create your first destination to get AI recommendations!
          </p>
          <Link
            href="/trips/new"
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white text-xs font-semibold shadow-md shadow-rose-600/30 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Create Your First Trip</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip) => (
            <TripCard key={trip.id} trip={trip} onDeleteTrip={handleDeleteTrip} />
          ))}
        </div>
      )}
    </div>
  );
}
