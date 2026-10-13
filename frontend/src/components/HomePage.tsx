import React, { useState } from 'react';
import {
  Search,
  Building2,
  FileText,
  FileCheck2,
  ArrowRight,
  CheckCircle2,
  Shield,
  HelpCircle,
} from 'lucide-react';
import { MainNavTab } from './Header';

interface HomePageProps {
  onNavigate: (tab: MainNavTab) => void;
  onAskQuestion: (question: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate, onAskQuestion }) => {
  const [heroQuery, setHeroQuery] = useState('');

  const handleHeroSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (heroQuery.trim()) {
      onAskQuestion(heroQuery.trim());
      onNavigate('policy');
    } else {
      onNavigate('policy');
    }
  };

  return (
    <div className="space-y-16 pb-16">
      {/* 1. POLISHED TWO-COLUMN HERO */}
      <section className="relative overflow-hidden rounded-[1.5rem] bg-gradient-to-br from-navy-900 via-navy-850 to-navy-950 border border-navy-800 shadow-card">
        <div className="grid grid-cols-1 lg:grid-cols-12 items-center">
          {/* Left Column: Heading, Text & Main Input */}
          <div className="p-8 sm:p-12 lg:p-14 lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-500/30 text-cyan-300 text-xs font-semibold">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              <span>Policy & provider guide</span>
            </div>

            <div className="space-y-3">
              <h1 className="page-title text-4xl sm:text-5xl lg:text-[3.5rem] font-semibold text-white tracking-tight leading-[1.08]">
                Health cover, made easier to understand.
              </h1>
              <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-xl">
                Find a hospital, make sense of your policy, or see what to do next with a claim.
              </p>
            </div>

            {/* Prominent Search/Question Input */}
            <form onSubmit={handleHeroSubmit} className="space-y-3 pt-2">
              <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
                <div className="relative flex-1">
                  <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
                  <input
                    type="text"
                    value={heroQuery}
                    onChange={(e) => setHeroQuery(e.target.value)}
                    placeholder="Ask a question about your cover…"
                    className="w-full bg-white border border-slate-300 hover:border-slate-400 rounded-xl pl-12 pr-4 py-3.5 text-sm text-[#1C3437] font-medium placeholder:text-[#718383] caret-[#1C3437] focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-brand-cyan shadow-sm transition"
                    aria-label="Ask about health insurance policy"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-3.5 rounded-xl bg-brand-cyan hover:bg-cyan-600 active:scale-[.98] text-white text-sm font-semibold transition shadow-sm flex items-center justify-center gap-2 whitespace-nowrap"
                >
                  <span>Ask about my cover</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              {/* Secondary Action */}
              <div className="flex items-center gap-4 pt-1">
                <span className="text-xs text-slate-400">Looking for care?</span>
                <button
                  type="button"
                  onClick={() => onNavigate('hospitals')}
                  className="text-xs font-semibold text-cyan-300 hover:text-cyan-200 underline underline-offset-4 flex items-center gap-1"
                >
                  <Building2 className="w-3.5 h-3.5" />
                  Find a hospital
                </button>
              </div>
            </form>

            {/* Trust-oriented tagline */}
            <div className="pt-4 border-t border-navy-800/80 flex items-center gap-2 text-xs text-slate-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Answers link back to the policy wording they use.</span>
            </div>
          </div>

          {/* Right Column: Doctor-Patient Consultation Photo */}
          <div className="lg:col-span-5 h-72 sm:h-96 lg:h-full relative overflow-hidden bg-navy-950">
            <img
              src="/images/doctor_consultation.jpg"
              alt="Doctor consulting with a patient in a bright, modern healthcare clinic"
              className="w-full h-full object-cover object-center"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-navy-950/60 via-transparent to-transparent lg:hidden" />
          </div>
        </div>
      </section>

      {/* 2. THREE ATTRACTIVE FEATURE CARDS */}
      <section className="space-y-6">
        <div>
          <h2 className="page-title text-2xl sm:text-3xl font-semibold text-white tracking-tight">
            Start with what you need
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Go directly to hospitals, policy wording, or practical claims guidance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card A: Find a Hospital */}
          <div className="bg-navy-850 border border-navy-800 hover:border-navy-700 rounded-2xl overflow-hidden shadow-lg flex flex-col justify-between transition group">
            <div className="h-44 overflow-hidden relative bg-navy-900">
              <img
                src="/images/hospital_reception.jpg"
                alt="Modern hospital reception and healthcare facility entrance"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                loading="lazy"
              />
              <div className="absolute top-3 left-3">
                <span className="px-2.5 py-1 rounded-md bg-navy-950/80 backdrop-blur-md text-cyan-300 border border-navy-700 text-xs font-semibold flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5" />
                  Provider Directory
                </span>
              </div>
            </div>

            <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-white group-hover:text-cyan-200 transition">
                  Find a Hospital
                </h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Search the national facility directory or explore the available Star Health network sample.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => onNavigate('hospitals')}
                  className="w-full py-2.5 px-4 rounded-xl bg-navy-800 hover:bg-blue-600 hover:text-white text-slate-200 text-sm font-semibold border border-navy-700 transition flex items-center justify-center gap-2"
                >
                  <span>Search hospitals</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Card B: Understand My Policy */}
          <div className="bg-navy-850 border border-navy-800 hover:border-navy-700 rounded-2xl overflow-hidden shadow-lg flex flex-col justify-between transition group">
            <div className="h-44 overflow-hidden relative bg-navy-900">
              <img
                src="/images/policy_advisor.jpg"
                alt="Health insurance advisor explaining policy coverage document to customer"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                loading="lazy"
              />
              <div className="absolute top-3 left-3">
                <span className="px-2.5 py-1 rounded-md bg-navy-950/80 backdrop-blur-md text-cyan-300 border border-navy-700 text-xs font-semibold flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5" />
                  Policy Terms
                </span>
              </div>
            </div>

            <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-white group-hover:text-cyan-200 transition">
                  Understand My Policy
                </h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Ask about waiting periods, room limits, exclusions, and more—with source passages to check.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => onNavigate('policy')}
                  className="w-full py-2.5 px-4 rounded-xl bg-navy-800 hover:bg-blue-600 hover:text-white text-slate-200 text-sm font-semibold border border-navy-700 transition flex items-center justify-center gap-2"
                >
                  <span>Ask about my policy</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Card C: Get Claims Help */}
          <div className="bg-navy-850 border border-navy-800 hover:border-navy-700 rounded-2xl overflow-hidden shadow-lg flex flex-col justify-between transition group">
            <div className="h-44 overflow-hidden relative bg-navy-900">
              <img
                src="/images/claims_documentation.jpg"
                alt="Healthcare claims specialist reviewing medical insurance documents"
                className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                loading="lazy"
              />
              <div className="absolute top-3 left-3">
                <span className="px-2.5 py-1 rounded-md bg-navy-950/80 backdrop-blur-md text-cyan-300 border border-navy-700 text-xs font-semibold flex items-center gap-1.5">
                  <FileCheck2 className="w-3.5 h-3.5" />
                  Claims Guide
                </span>
              </div>
            </div>

            <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-white group-hover:text-cyan-200 transition">
                  Get Claims Help
                </h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  See the steps, time limits, and documents commonly needed for a claim.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => onNavigate('claims')}
                  className="w-full py-2.5 px-4 rounded-xl bg-navy-800 hover:bg-blue-600 hover:text-white text-slate-200 text-sm font-semibold border border-navy-700 transition flex items-center justify-center gap-2"
                >
                  <span>View claims steps</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. SMALL, UNOBTRUSIVE TRUST & LIMITATIONS NOTE */}
      <section className="bg-navy-900/60 border border-navy-800 rounded-xl p-5 text-xs text-slate-400 space-y-1.5 leading-relaxed">
        <div className="flex items-center gap-2 text-cyan-300 font-semibold text-xs">
          <HelpCircle className="w-4 h-4 flex-shrink-0" />
          <span>About this guide</span>
        </div>
        <p>
          Policy answers are drawn from the Star Comprehensive policy wording, Customer Information Sheet, and indexed guidance shown in the portal.
        </p>
        <p>
          This guide is for information only. Your policy documents and Star Health’s formal decision determine the cover and claim outcome for your situation.
        </p>
      </section>
    </div>
  );
};
