'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { ArrowLeft, Sparkles, RefreshCw, MapPin, Calendar, DollarSign, AlertCircle, Trash2, Check, X } from 'lucide-react';
import { tripService } from '@/service';

export default function AIRecommendationView({ initialTrip }) {
  const router = useRouter();
  const [trip, setTrip] = useState(initialTrip);
  const [recommendation, setRecommendation] = useState(initialTrip?.ai_recommendation || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchRecommendation = async (forceRefresh = false) => {
    if (!trip?.id) return;
    setLoading(true);
    setError(null);

    try {
      const updatedTrip = await tripService.generateRecommendation(trip.id, forceRefresh);
      setTrip(updatedTrip);
      setRecommendation(updatedTrip.ai_recommendation);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during AI itinerary generation.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTrip = async () => {
    if (!trip?.id) return;
    setIsDeleting(true);

    try {
      await tripService.deleteTrip(trip.id);
      router.push('/trips');
      router.refresh();
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Failed to delete trip.');
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  useEffect(() => {
    if (!recommendation && trip?.id) {
      fetchRecommendation(false);
    }
  }, [trip?.id]);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top action bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/trips"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-rose-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to My Trips</span>
        </Link>

        <div className="flex items-center gap-2">
          {showDeleteConfirm ? (
            <div className="flex items-center gap-1.5 bg-slate-900 border border-rose-500/40 p-1 rounded-xl">
              <span className="text-xs text-rose-300 px-1">Delete trip?</span>
              <button
                type="button"
                onClick={handleDeleteTrip}
                disabled={isDeleting}
                className="p-1 rounded-lg bg-rose-600 text-white hover:bg-rose-500 transition-colors"
              >
                <Check className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="p-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors inline-flex items-center gap-1.5 text-xs"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Delete Trip</span>
            </button>
          )}
        </div>
      </div>

      {/* Destination Hero Header Card */}
      <div className="rounded-3xl bg-slate-900/80 border border-slate-800 p-6 sm:p-8 shadow-xl backdrop-blur-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="p-2 rounded-xl bg-rose-600/20 text-rose-400">
              <MapPin className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {trip?.destination}
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-2 mt-3 text-xs">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              <Calendar className="w-3.5 h-3.5 text-rose-400" />
              <span>{trip?.days} Days</span>
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              <DollarSign className="w-3.5 h-3.5 text-rose-400" />
              <span>${trip?.budget?.toLocaleString()} Total</span>
            </span>
          </div>
        </div>

        <button
          onClick={() => fetchRecommendation(true)}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold text-xs shadow-lg shadow-rose-600/30 transition-all disabled:opacity-50 hover:scale-[1.02]"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{recommendation ? 'Regenerate Itinerary' : 'Generate Itinerary'}</span>
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="p-12 rounded-3xl bg-slate-900/60 border border-slate-800 text-center">
          <div className="w-12 h-12 border-4 border-rose-500/20 border-t-rose-500 rounded-full animate-spin mx-auto mb-4" />
          <h3 className="text-base font-bold text-white mb-1">AWS Bedrock is Crafting Your Journey</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Structuring custom morning, afternoon, and evening itineraries, budget allocations, and cultural spots...
          </p>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="p-6 rounded-3xl bg-rose-950/20 border border-rose-900/40 text-center">
          <AlertCircle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
          <h3 className="text-sm font-bold text-white mb-1">Generation Error</h3>
          <p className="text-xs text-slate-400 mb-4">{error}</p>
          <button
            onClick={() => fetchRecommendation(true)}
            className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold"
          >
            Retry Generation
          </button>
        </div>
      )}

      {/* Markdown AI Itinerary Content */}
      {!loading && !error && recommendation && (
        <div className="rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl overflow-hidden backdrop-blur-xl">
          <div className="px-6 py-4 bg-gradient-to-r from-rose-950/40 via-red-950/20 to-slate-900/60 border-b border-slate-800 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-rose-400" />
            <span className="font-bold text-sm text-rose-200">AI Tailored Travel Itinerary & Guide</span>
          </div>
          <div className="p-6 sm:p-8 markdown-body text-slate-200">
            <ReactMarkdown>{recommendation}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
