'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Compass, LogIn, UserPlus, Sparkles, Key, Mail, User as UserIcon, AlertCircle } from 'lucide-react';
import { authService } from '@/service';

export default function LoginPage() {
  const router = useRouter();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await authService.register({
          username: username.trim(),
          email: email.trim(),
          password: password,
          full_name: fullName.trim() || username.trim(),
        });
      } else {
        await authService.login(email.trim() || username.trim(), password);
      }
      router.push('/trips');
      router.refresh();
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Authentication failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = async (userEmail, userPass) => {
    setError(null);
    setLoading(true);
    try {
      await authService.login(userEmail, userPass);
      router.push('/trips');
      router.refresh();
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Quick login failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 bg-[#090d14]">
      {/* Background glow */}
      <div className="absolute w-[500px] h-[500px] bg-rose-600/10 blur-[140px] rounded-full pointer-events-none" />

      <div className="relative z-10 w-full max-w-md bg-slate-900/80 border border-slate-800 rounded-3xl p-8 shadow-2xl backdrop-blur-xl shadow-black/60">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-600 to-red-500 shadow-lg shadow-rose-600/30 mb-3">
            <Compass className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            {isRegister ? 'Create Your Account' : 'Welcome Back'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {isRegister
              ? 'Join Kelana AI to generate personalized itineraries'
              : 'Sign in to access your trips and travel chat'}
          </p>
        </div>

        {/* Tab switcher */}
        <div className="flex bg-slate-950/70 p-1 rounded-xl mb-6 border border-slate-800">
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(null); }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              !isRegister
                ? 'bg-rose-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(null); }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              isRegister
                ? 'bg-rose-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {/* Error notification */}
        {error && (
          <div className="mb-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-300">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
              <div className="relative">
                <UserIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="e.g. Good User"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
                />
              </div>
            </div>
          )}

          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Username</label>
              <div className="relative">
                <UserPlus className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="e.g. traveler99"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              {isRegister ? 'Email Address' : 'Email or Username'}
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type={isRegister ? 'email' : 'text'}
                required
                placeholder={isRegister ? 'name@example.com' : 'gooduser@kelana.ai'}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Key className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold text-sm shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : isRegister ? (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Create Account</span>
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </>
            )}
          </button>
        </form>

        {/* Quick-fill Demo Accounts */}
        <div className="mt-8 pt-6 border-t border-slate-800/80">
          <p className="text-[11px] uppercase font-bold text-slate-400 tracking-wider text-center mb-3">
            Quick Test Accounts (1-Click Login)
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => quickLogin('gooduser@kelana.ai', 'password123')}
              disabled={loading}
              className="p-2.5 rounded-xl bg-slate-950/80 hover:bg-rose-950/30 border border-slate-800 hover:border-rose-500/40 text-left transition-all group"
            >
              <div className="text-xs font-bold text-slate-200 group-hover:text-rose-400">
                Good User
              </div>
              <div className="text-[10px] text-slate-500 font-mono">gooduser@kelana.ai</div>
            </button>

            <button
              type="button"
              onClick={() => quickLogin('niceuser@kelana.ai', 'password123')}
              disabled={loading}
              className="p-2.5 rounded-xl bg-slate-950/80 hover:bg-rose-950/30 border border-slate-800 hover:border-rose-500/40 text-left transition-all group"
            >
              <div className="text-xs font-bold text-slate-200 group-hover:text-rose-400">
                Nice User
              </div>
              <div className="text-[10px] text-slate-500 font-mono">niceuser@kelana.ai</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
