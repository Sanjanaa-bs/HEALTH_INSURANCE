import React, { useState } from 'react';
import { Shield, Menu, X, RefreshCw } from 'lucide-react';
import { HealthResponse } from '../types';

export type MainNavTab = 'home' | 'hospitals' | 'policy' | 'claims' | 'documents';
export type TabId = MainNavTab;

interface HeaderProps {
  activeTab: MainNavTab;
  onSelectTab: (tab: MainNavTab) => void;
  health: HealthResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onSelectTab,
  health,
  loading,
  onRefresh,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems: { id: MainNavTab; label: string }[] = [
    { id: 'home', label: 'Home' },
    { id: 'hospitals', label: 'Find Hospitals' },
    { id: 'policy', label: 'Policy Information' },
    { id: 'claims', label: 'Claims Help' },
    { id: 'documents', label: 'Document Library' },
  ];

  const handleNavClick = (tab: MainNavTab) => {
    onSelectTab(tab);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header className="sticky top-0 z-50 bg-navy-950/95 border-b border-navy-800/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleNavClick('home')}
            className="flex items-center gap-3 group text-left focus:outline-none"
            aria-label="Health Insurance Portal Home"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:from-blue-500 group-hover:to-cyan-500 transition">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-white tracking-tight">
                  Star Health
                </span>
                <span className="text-[11px] font-semibold text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 rounded-full">
                  Policy Portal
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Comprehensive Insurance & Verified Provider Information
              </p>
            </div>
          </button>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1" aria-label="Primary Navigation">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition ${
                  isActive
                    ? 'text-white bg-navy-800 font-semibold shadow-xs border border-navy-700'
                    : 'text-slate-300 hover:text-white hover:bg-navy-900'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right Section: System Status & Refresh */}
        <div className="hidden sm:flex items-center gap-3">
          {health ? (
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${
                health.database_connected
                  ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
                  : 'bg-amber-950/40 text-amber-300 border-amber-500/30'
              }`}
              title={`Database status: ${health.database_connected ? 'Connected' : 'Degraded'}`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  health.database_connected ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              />
              <span>{health.database_connected ? 'Verified Sources' : 'Connection Issue'}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-navy-900 text-slate-400 border border-navy-800">
              <span className="w-2 h-2 rounded-full bg-slate-500 animate-pulse" />
              <span>Connecting...</span>
            </div>
          )}

          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 text-slate-400 hover:text-white hover:bg-navy-900 rounded-lg border border-navy-800 transition disabled:opacity-50"
            title="Refresh source information"
            aria-label="Refresh source information"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Mobile Menu Button */}
        <div className="flex md:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-navy-900 border border-navy-800"
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-navy-800 bg-navy-950 px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full text-left px-3.5 py-2.5 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? 'bg-navy-800 text-white font-semibold'
                    : 'text-slate-300 hover:bg-navy-900 hover:text-white'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
