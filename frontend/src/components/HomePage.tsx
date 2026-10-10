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
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-navy-900 via-navy-850 to-navy-950 border border-navy-800 shadow-xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 items-center">
          {/* Left Column: Heading, Text & Main Input */}
          <div className="p-8 sm:p-12 lg:p-14 lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-500/30 text-cyan-300 text-xs font-semibold">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              <span>Official Star Health Policy & Provider Intelligence</span>
            </div>

            <div className="space-y-3">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
                Understand Your Health Insurance with Confidence
              </h1>
              <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-xl">
                Explore your policy documents, find network hospitals, and understand the steps involved in your health insurance claims—all in one place.
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
                    placeholder="Ask about your policy, coverage, or waiting periods..."
                    className="w-full bg-white border border-slate-300 hover:border-slate-400 rounded-xl pl-12 pr-4 py-3.5 text-sm text-[#0C162E] font-medium placeholder:text-[#64748B] caret-[#0C162E] focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition"
                    aria-label="Ask about health insurance policy"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-sm font-semibold transition shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 whitespace-nowrap"
                >
                  <span>Ask a Question</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              {/* Secondary Action */}
              <div className="flex items-center gap-4 pt-1">
                <span className="text-xs text-slate-400">Or explore directories:</span>
                <button
                  type="button"
                  onClick={() => onNavigate('hospitals')}
                  className="text-xs font-semibold text-cyan-300 hover:text-cyan-200 underline underline-offset-4 flex items-center gap-1"
                >
                  <Building2 className="w-3.5 h-3.5" />
                  Find a Hospital &rarr;
                </button>
              </div>
            </form>

            {/* Trust-oriented tagline */}
            <div className="pt-4 border-t border-navy-800/80 flex items-center gap-2 text-xs text-slate-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Guidance grounded in available policy documents and source material.</span>
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
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            How can we help you today?
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Access verified hospital directories, legal policy terms, and step-by-step claims procedures.
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
                  Search across national hospital directory facilities and explore verified Star Health cashless network hospitals in your location.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => onNavigate('hospitals')}
                  className="w-full py-2.5 px-4 rounded-xl bg-navy-800 hover:bg-blue-600 hover:text-white text-slate-200 text-sm font-semibold border border-navy-700 transition flex items-center justify-center gap-2"
                >
                  <span>Explore Hospitals</span>
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
                  Ask evidence-grounded questions about pre-existing disease waiting periods, room-rent limits, cataract terms, and exclusions.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => onNavigate('policy')}
                  className="w-full py-2.5 px-4 rounded-xl bg-navy-800 hover:bg-blue-600 hover:text-white text-slate-200 text-sm font-semibold border border-navy-700 transition flex items-center justify-center gap-2"
                >
                  <span>Explore Policy</span>
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
                  Learn about cashless hospitalization intimation, reimbursement timelines, required medical documents, and official tracking.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => onNavigate('claims')}
                  className="w-full py-2.5 px-4 rounded-xl bg-navy-800 hover:bg-blue-600 hover:text-white text-slate-200 text-sm font-semibold border border-navy-700 transition flex items-center justify-center gap-2"
                >
                  <span>View Claims Guide</span>
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
          <span>Policyholder Notice & Informational Scope</span>
        </div>
        <p>
          Guidance and policy answers on this platform are grounded strictly in indexed source documents from Star Health and Allied Insurance Company Limited (UIN: SHAHLIP26044V092526) and IRDAI regulations.
        </p>
        <p>
          This portal provides educational assistance and does not substitute for binding policy contracts or insurer pre-authorization. Final claim decisions and coverage applicability depend upon formal assessment by Star Health.
        </p>
      </section>
    </div>
  );
};
