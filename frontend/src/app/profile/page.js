'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Mail, Calendar, MapPin, LogOut, ArrowRight, ShieldCheck, RefreshCw, MessageSquare, Compass, User as UserIcon } from 'lucide-react';
import { authService, tripService } from '@/service';

export default function ProfilePage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState(null);
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    const loadData = async () => {
      setLoading(true);
      try {
        const user = await authService.getMe();
        setCurrentUser(user);

        const userTrips = await tripService.getTrips().catch(() => []);
        setTrips(userTrips);
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  const handleLogout = () => {
    authService.logout();
    router.push('/login');
    router.refresh();
  };

  const handleQuickSwitch = async (email, pass) => {
    setLoading(true);
    try {
      await authService.login(email, pass);
      window.location.reload();
    } catch {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090d14] flex flex-col items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-rose-500/20 border-t-rose-500 rounded-full animate-spin mb-4" />
        <p className="text-xs text-slate-400">Loading your profile...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090d14] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      {/* Header Profile Card */}
      <div className="rounded-3xl bg-slate-900/80 border border-slate-800 p-6 sm:p-8 shadow-xl backdrop-blur-xl mb-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-rose-600/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="relative z-10 flex flex-col sm:flex-row items-center sm:items-start justify-between gap-6 text-center sm:text-left">
          <div className="flex-1">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-600/15 border border-rose-500/30 text-rose-300 text-xs font-semibold mb-3">
              <Compass className="w-3.5 h-3.5 text-rose-400" />
              <span>Verified Traveler • {trips.length} {trips.length === 1 ? 'Trip' : 'Trips'}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              {currentUser?.full_name || currentUser?.username}
            </h1>
            <p className="text-xs text-rose-400/90 font-mono mt-0.5">@{currentUser?.username}</p>
            <p className="text-xs text-slate-300 mt-2 max-w-lg leading-relaxed">
              {currentUser?.bio || 'Traveler exploring the world with AI assistance.'}
            </p>

            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-4 mt-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-500" />
                {currentUser?.email}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                Joined 2026
              </span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-rose-950/40 border border-slate-700 hover:border-rose-500/40 text-slate-300 hover:text-rose-400 text-xs font-semibold flex items-center gap-2 transition-all"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Account Switcher */}
      <div className="rounded-3xl bg-slate-900/60 border border-slate-800 p-6 shadow-lg mb-8">
        <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-rose-400" />
          <span>Switch Account (Testing Utility)</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Quickly toggle between different test travelers to evaluate trip data isolation and AI chat.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={() => handleQuickSwitch('gooduser@kelana.ai', 'password123')}
            className={`p-3 rounded-2xl border text-left flex items-center justify-between transition-all ${
              currentUser?.username === 'gooduser'
                ? 'bg-rose-950/30 border-rose-500/50 text-rose-300'
                : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
            }`}
          >
            <div>
              <div className="text-xs font-bold">Good User</div>
              <div className="text-[10px] text-slate-500 font-mono">gooduser@kelana.ai</div>
            </div>
            {currentUser?.username === 'gooduser' && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-600 text-white">
                Current
              </span>
            )}
          </button>

          <button
            onClick={() => handleQuickSwitch('niceuser@kelana.ai', 'password123')}
            className={`p-3 rounded-2xl border text-left flex items-center justify-between transition-all ${
              currentUser?.username === 'niceuser'
                ? 'bg-rose-950/30 border-rose-500/50 text-rose-300'
                : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
            }`}
          >
            <div>
              <div className="text-xs font-bold">Nice User</div>
              <div className="text-[10px] text-slate-500 font-mono">niceuser@kelana.ai</div>
            </div>
            {currentUser?.username === 'niceuser' && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-600 text-white">
                Current
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/trips"
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/40 flex items-center justify-between transition-all group"
        >
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-600/15 text-rose-400">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-white group-hover:text-rose-400 transition-colors">
                My Trips
              </div>
              <div className="text-xs text-slate-400">View and create personalized itineraries</div>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-rose-400 group-hover:translate-x-0.5 transition-all" />
        </Link>

        <Link
          href="/chat"
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/40 flex items-center justify-between transition-all group"
        >
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-600/15 text-rose-400">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-white group-hover:text-rose-400 transition-colors">
                AI Travel Assistant Chat
              </div>
              <div className="text-xs text-slate-400">Ask questions and plan travel details</div>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-rose-400 group-hover:translate-x-0.5 transition-all" />
        </Link>
      </div>
    </div>
  );
}
