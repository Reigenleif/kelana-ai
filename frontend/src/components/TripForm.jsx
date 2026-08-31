'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Send, MapPin, Calendar, DollarSign, Tag, Sparkles, AlertCircle } from 'lucide-react';
import { tripService, authService } from '@/service';

export default function TripForm({ onTripCreated }) {
  const router = useRouter();
  const [destination, setDestination] = useState('');
  const [days, setDays] = useState('');
  const [budget, setBudget] = useState('');
  const [category, setCategory] = useState('Standard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!destination || !days || !budget) {
      setError('Please fill in all required fields.');
      return;
    }

    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      destination: destination.trim(),
      days: parseInt(days, 10),
      budget: parseFloat(budget),
      category: category || 'Standard',
    };

    try {
      const newTrip = await tripService.createTrip(payload);
      if (onTripCreated) {
        onTripCreated(newTrip);
      } else {
        router.push(`/trips/${newTrip.id}/recommendation`);
        router.refresh();
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred while creating the trip.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-black/50 backdrop-blur-xl">
      {/* Header */}
      <div className="mb-6 pb-4 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-600/15 border border-rose-500/30 text-rose-300 text-xs font-semibold mb-2">
          <Sparkles className="w-3.5 h-3.5 text-rose-400" />
          <span>New AI Travel Itinerary</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight">Plan Your Journey</h2>
        <p className="text-xs text-slate-400 mt-1">
          Specify your destination and budget parameters to generate tailored AI schedules.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="destination" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-rose-400" />
            <span>Destination City / Country</span>
          </label>
          <input
            id="destination"
            type="text"
            placeholder="e.g. Tokyo & Kyoto, Japan"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            disabled={loading}
            required
            className="w-full px-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="days" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-rose-400" />
              <span>Duration (Days)</span>
            </label>
            <input
              id="days"
              type="number"
              min="1"
              max="90"
              placeholder="e.g. 7"
              value={days}
              onChange={(e) => setDays(e.target.value)}
              disabled={loading}
              required
              className="w-full px-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
            />
          </div>

          <div>
            <label htmlFor="budget" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <DollarSign className="w-3.5 h-3.5 text-rose-400" />
              <span>Total Budget (USD)</span>
            </label>
            <input
              id="budget"
              type="number"
              min="1"
              step="any"
              placeholder="e.g. 2500"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              disabled={loading}
              required
              className="w-full px-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
            />
          </div>
        </div>

        <div>
          <label htmlFor="category" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-rose-400" />
            <span>Travel Style & Category</span>
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            disabled={loading}
            className="w-full px-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
          >
            <option value="Culture & Food">Culture & Food (Temples, Cuisine, Markets)</option>
            <option value="Standard">Standard (Comfortable & Balanced)</option>
            <option value="Backpacker">Backpacker (Budget-conscious & Hostels)</option>
            <option value="Luxury">Luxury (5-Star Hotels & Premium Dining)</option>
            <option value="Adventure">Adventure (Hiking, Nature & Outdoor)</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold text-sm shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 hover:scale-[1.01]"
        >
          {loading ? (
            <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Create Trip & Generate Plan</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
