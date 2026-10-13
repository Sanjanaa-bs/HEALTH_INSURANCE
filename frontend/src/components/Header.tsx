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
    { id: 'hospitals', label: 'Hospitals' },
    { id: 'policy', label: 'Policy' },
    { id: 'claims', label: 'Claims' },
    { id: 'documents', label: 'Documents' },
  ];

  const handleNavClick = (tab: MainNavTab) => {
    onSelectTab(tab);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header className="site-header sticky top-0 z-50 bg-[#102D2D]/95 border-b border-[#2F4D49] backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-[4.5rem] flex items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleNavClick('home')}
            className="flex items-center gap-3 group text-left focus:outline-none rounded-lg"
            aria-label="Star Health home"
          >
            <div className="w-10 h-10 rounded-xl bg-[#28675E] flex items-center justify-center text-white group-hover:bg-[#397B70] transition-colors">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                  <span className="text-[15px] font-semibold text-[#F7F6EE] tracking-tight">
                  Star Health
                </span>
                  <span className="text-[10px] font-medium text-[#D2E5DC] bg-[#1E3E39] border border-[#45675A] px-2 py-0.5 rounded-full">
                  Coverage Guide
                </span>
              </div>
              <p className="text-[11px] text-[#B7C7C3] hidden lg:block">
                Coverage, hospitals and claims
              </p>
            </div>
          </button>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden xl:flex items-center gap-1" aria-label="Primary Navigation">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`px-3.5 py-2 text-[13px] font-medium rounded-lg transition ${
                  isActive
                    ? 'text-[#F7F6EE] bg-[#1B403D] font-semibold border border-[#42645B]'
                    : 'text-[#CCD8D3] hover:text-white hover:bg-[#173936]'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right Section: System Status & Refresh */}
        <div className="hidden sm:flex items-center gap-2.5">
          {health ? (
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${
                health.database_connected
                  ? 'bg-[#1C3D36] text-[#BBDCCB] border-[#42675B]'
                  : 'bg-[#4A3828] text-[#F0D3A0] border-[#806443]'
              }`}
              title={`Database status: ${health.database_connected ? 'Connected' : 'Degraded'}`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  health.database_connected ? 'bg-[#8FCAA7]' : 'bg-[#D8A45A]'
                }`}
              />
              <span>{health.database_connected ? 'Data service online' : 'Connection issue'}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-[#1C3D36] text-[#BBDCCB] border border-[#42675B]">
              <span className="w-2 h-2 rounded-full bg-[#8FCAA7] animate-pulse" />
              <span>Connecting to data service</span>
            </div>
          )}

          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 text-[#B7C7C3] hover:text-white hover:bg-[#173936] rounded-lg border border-[#35534D] transition disabled:opacity-50"
            title="Refresh source information"
            aria-label="Refresh source information"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Mobile Menu Button */}
        <div className="flex xl:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-[#D1DDD8] hover:text-white hover:bg-[#173936] border border-[#35534D]"
            aria-expanded={mobileMenuOpen}
            aria-controls="primary-menu"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <nav id="primary-menu" aria-label="Primary Navigation" className="xl:hidden border-t border-[#2F4D49] bg-[#102D2D] px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                aria-current={isActive ? 'page' : undefined}
                className={`w-full text-left px-3.5 py-2.5 rounded-lg text-sm font-medium transition ${
                  isActive
                  ? 'bg-[#1B403D] text-white font-semibold'
                    : 'text-[#CCD8D3] hover:bg-[#173936] hover:text-white'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      )}
    </header>
  );
};
