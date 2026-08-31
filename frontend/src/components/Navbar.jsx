'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Compass, MapPin, MessageSquare, User as UserIcon, LogIn, LogOut, Plus } from 'lucide-react';
import { authService } from '@/service';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const user = authService.getCurrentUser();
    setCurrentUser(user);

    // Listen to storage events for cross-tab or logout sync
    const handleStorage = () => {
      setCurrentUser(authService.getCurrentUser());
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, [pathname]);

  const handleLogout = () => {
    authService.logout();
    setCurrentUser(null);
    router.push('/login');
    router.refresh();
  };

  const navLinks = [
    { href: '/', label: 'Home', icon: Compass },
    { href: '/trips', label: 'My Trips', icon: MapPin },
    { href: '/chat', label: 'Chat', icon: MessageSquare },
    { href: '/profile', label: 'Profile', icon: UserIcon },
  ];

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-[#090d14]/80 border-b border-rose-900/20 shadow-lg shadow-black/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center shadow-lg shadow-rose-600/30 group-hover:scale-105 transition-transform duration-200">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-rose-100 to-rose-400 bg-clip-text text-transparent">
              Kelana AI
            </span>
            <span className="text-[10px] uppercase font-semibold tracking-wider text-rose-400/80 -mt-1">
              Travel Companion
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-full border border-slate-800/80">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-rose-600 to-red-600 text-white shadow-md shadow-rose-600/25'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User / Action Buttons */}
        <div className="flex items-center gap-3">
          {mounted && currentUser ? (
            <div className="flex items-center gap-3">
              <Link
                href="/trips/new"
                className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-rose-600/15 border border-rose-500/30 text-rose-300 hover:bg-rose-600 hover:text-white text-xs font-semibold transition-all duration-200"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Trip</span>
              </Link>

              <Link
                href="/profile"
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 hover:border-rose-500/40 transition-colors"
              >
                <UserIcon className="w-4 h-4 text-rose-400" />
                <span className="text-xs font-medium text-slate-200 hidden sm:inline">
                  {currentUser.username}
                </span>
              </Link>

              <button
                onClick={handleLogout}
                title="Log out"
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white text-xs font-semibold shadow-md shadow-rose-600/25 transition-all duration-200 hover:scale-[1.02]"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Nav Bar */}
      <div className="md:hidden flex items-center justify-around py-2 border-t border-slate-800/80 bg-[#090d14]">
        {navLinks.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-1 text-[11px] font-medium transition-colors ${
                isActive ? 'text-rose-400 font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
}
