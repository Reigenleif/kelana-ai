'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, MapPin, MessageSquare } from 'lucide-react';

export default function LandingHomePage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-[#090d14] text-slate-100 flex flex-col justify-center">
      {/* Hero Section */}
      <section className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden">
        {/* Background Image with Gradient Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1800&auto=format&fit=crop&q=85"
            alt="Travel Adventure Hero"
            className="w-full h-full object-cover object-center scale-105 transform filter brightness-40"
          />
          {/* Crimson & Dark Gradient overlays */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#090d14] via-[#090d14]/70 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-rose-950/50 via-transparent to-red-950/40" />
          <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-rose-600/20 blur-[130px] rounded-full pointer-events-none" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center py-16">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-600/20 border border-rose-500/30 backdrop-blur-md text-rose-300 text-xs font-semibold mb-6">
            <Sparkles className="w-3.5 h-3.5 text-rose-400" />
            <span>Next-Gen Travel Assistant powered by AWS Bedrock</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight sm:leading-tight">
            Craft Your Dream Journey with{' '}
            <span className="bg-gradient-to-r from-rose-400 via-red-500 to-rose-600 bg-clip-text text-transparent">
              AI Precision
            </span>
          </h1>

          {/* Subheading */}
          <p className="mt-6 max-w-2xl mx-auto text-base sm:text-lg text-slate-300 font-normal leading-relaxed">
            Generate bespoke day-by-day itineraries, budget breakdowns, and hidden gems tailored to your travel style. Chat with our intelligent AI travel assistant.
          </p>

          {/* CTAs */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/trips/new"
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold text-sm shadow-lg shadow-rose-600/30 flex items-center gap-2 hover:scale-[1.02] transition-all duration-200"
            >
              <Sparkles className="w-4 h-4" />
              <span>Generate New Trip</span>
            </Link>

            <Link
              href="/trips"
              className="px-6 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-700 hover:border-rose-500/50 text-slate-200 font-semibold text-sm backdrop-blur-md flex items-center gap-2 transition-all duration-200"
            >
              <MapPin className="w-4 h-4 text-rose-400" />
              <span>Explore My Trips</span>
            </Link>

            <Link
              href="/chat"
              className="px-5 py-3.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/40 border border-rose-800/40 text-rose-300 font-semibold text-sm backdrop-blur-md flex items-center gap-2 transition-all duration-200"
            >
              <MessageSquare className="w-4 h-4 text-rose-400" />
              <span>AI Travel Chat</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
