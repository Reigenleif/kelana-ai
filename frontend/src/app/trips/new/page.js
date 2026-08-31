'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import TripForm from '@/components/TripForm';

export default function NewTripPage() {
  return (
    <div className="min-h-screen bg-[#090d14] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="max-w-xl mx-auto mb-6">
        <Link
          href="/trips"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-rose-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Trips</span>
        </Link>
      </div>

      <TripForm />
    </div>
  );
}
