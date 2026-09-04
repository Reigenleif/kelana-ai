'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { MapPin, Calendar, DollarSign, Tag, Sparkles, Trash2, ArrowRight, Check, X } from 'lucide-react';

export default function TripCard({ trip, onDeleteTrip }) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);


  const handleConfirmDelete = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!onDeleteTrip) return;
    setIsDeleting(true);
    try {
      await onDeleteTrip(trip.id);
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  return (
    <div className="group relative rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-rose-500/40 p-5 shadow-lg transition-all duration-300 hover:shadow-xl hover:shadow-rose-950/20 flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className="flex items-center gap-2 mb-3">
          <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 group-hover:bg-rose-500 group-hover:text-white transition-colors">
            <MapPin className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-base text-white group-hover:text-rose-300 transition-colors">
            {trip.destination}
          </h3>
        </div>

        {/* Details stats */}
        <div className="grid grid-cols-3 gap-2 my-4 p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
          <div>
            <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Duration</span>
            <div className="flex items-center gap-1 font-semibold text-slate-200 mt-0.5">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>{trip.days} {trip.days === 1 ? 'Day' : 'Days'}</span>
            </div>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Total</span>
            <div className="flex items-center gap-1 font-semibold text-slate-200 mt-0.5">
              <DollarSign className="w-3.5 h-3.5 text-slate-400" />
              <span>${trip.budget.toLocaleString()}</span>
            </div>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Daily</span>
            <div className="flex items-center gap-1 font-semibold text-rose-400 mt-0.5">
              <Tag className="w-3.5 h-3.5" />
              <span>${(trip.daily_budget || (trip.budget / trip.days)).toFixed(0)}/d</span>
            </div>
          </div>
        </div>
      </div>

      {/* Card Actions */}
      <div className="flex items-center justify-between gap-2 pt-3 border-t border-slate-800">
        <Link
          href={`/trips/${trip.id}/recommendation`}
          className="flex-1 inline-flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white text-xs font-semibold shadow-md shadow-rose-600/20 transition-all hover:scale-[1.01]"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{trip.ai_recommendation ? 'View Itinerary' : 'Generate AI Plan'}</span>
          <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
        </Link>

        {onDeleteTrip && (
          <div className="relative">
            {showConfirm ? (
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-rose-500/50">
                <button
                  type="button"
                  onClick={handleConfirmDelete}
                  disabled={isDeleting}
                  className="p-1.5 rounded-lg bg-rose-600 text-white hover:bg-rose-500 transition-colors"
                  title="Confirm delete"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowConfirm(false)}
                  disabled={isDeleting}
                  className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
                  title="Cancel"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowConfirm(true)}
                className="p-2 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                title="Delete Trip"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
