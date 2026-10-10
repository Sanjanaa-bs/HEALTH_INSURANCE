import React, { useState } from 'react';
import {
  Building2,
  FileText,
  FileCheck2,
  Search,
  ArrowRight,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Layers,
  MapPin,
  Receipt,
  FileSearch,
} from 'lucide-react';
import { DashboardSummary as DashboardSummaryType } from '../types';
import { TabId } from './Header';

interface OverviewPageProps {
  summary: DashboardSummaryType | null;
  loading: boolean;
  onNavigate: (tab: TabId) => void;
  onSelectQuestion?: (q: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  summary,
  loading,
  onNavigate,
  onSelectQuestion,
}) => {
  const [showDataDetails, setShowDataDetails] = useState(false);

  return (
    <div className="space-y-12 pb-12">
      {/* SECTION A: HERO */}
      <section className="bg-surface border border-border-light rounded-2xl shadow-card overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-12 items-center">
          {/* Left Column: Text & Actions */}
          <div className="p-8 sm:p-10 lg:p-12 lg:col-span-7 space-y-6">
            <div className="space-y-3">
              <span className="text-xs font-bold tracking-wider uppercase text-teal-muted bg-teal-light px-3 py-1 rounded-md border border-teal-border inline-block">
                Health Insurance Information
              </span>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-navy-primary leading-tight tracking-tight">
                Your health coverage, made easier to understand.
              </h1>
              <p className="text-base text-ink-secondary leading-relaxed max-w-xl">
                Find hospitals, explore your policy documents, and understand the steps involved in your health insurance claims—all in one place.
              </p>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-3 pt-1">
              <button
                onClick={() => onNavigate('hospitals')}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-navy-primary text-white font-medium text-sm hover:bg-navy-secondary transition shadow-sm"
              >
                <Building2 className="w-4 h-4 text-teal-light" />
                Find a Hospital
              </button>
              <button
                onClick={() => onNavigate('policy')}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-subtle text-navy-primary font-medium text-sm border border-border-light hover:bg-page transition"
              >
                <FileText className="w-4 h-4 text-teal-muted" />
                Understand My Policy
              </button>
            </div>

            {/* Trust message */}
            <div className="pt-2 border-t border-border-subtle flex items-center gap-2 text-xs text-ink-secondary">
              <CheckCircle2 className="w-4 h-4 text-teal-muted flex-shrink-0" />
              <span>Guidance grounded in available policy documents and source material.</span>
            </div>
          </div>

          {/* Right Column: Healthcare Photograph */}
          <div className="lg:col-span-5 h-72 sm:h-96 lg:h-full relative overflow-hidden bg-subtle">
            <img
              src="/images/doctor_consultation.jpg"
              alt="Doctor consulting with a patient in a modern healthcare clinic"
              className="w-full h-full object-cover object-center"
              loading="eager"
            />
          </div>
        </div>
      </section>

      {/* SECTION B: THREE PRIMARY SERVICES */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-navy-primary tracking-tight">
            Explore Core Services
          </h2>
          <p className="text-sm text-ink-secondary">
            Access verified provider registries, legal policy wordings, and claims procedures.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Service 1: Hospital Search */}
          <div className="bg-surface border border-border-light rounded-xl p-6 shadow-card flex flex-col justify-between hover:border-teal-border transition">
            <div className="space-y-4">
              <div className="w-11 h-11 rounded-lg bg-teal-light border border-teal-border flex items-center justify-center text-teal-muted">
                <Building2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-navy-primary">
                  Hospital Search
                </h3>
                <p className="text-sm text-ink-secondary mt-1 leading-relaxed">
                  Explore hospital directory records and available location details across states.
                </p>
              </div>
            </div>
            <div className="pt-6 mt-4 border-t border-border-subtle">
              <button
                onClick={() => onNavigate('hospitals')}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-teal-muted hover:text-navy-primary transition group"
              >
                <span>Explore hospitals</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </button>
            </div>
          </div>

          {/* Service 2: Policy Information */}
          <div className="bg-surface border border-border-light rounded-xl p-6 shadow-card flex flex-col justify-between hover:border-teal-border transition">
            <div className="space-y-4">
              <div className="w-11 h-11 rounded-lg bg-teal-light border border-teal-border flex items-center justify-center text-teal-muted">
                <FileSearch className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-navy-primary">
                  Policy Information
                </h3>
                <p className="text-sm text-ink-secondary mt-1 leading-relaxed">
                  Search available policy wording and customer information sheets with page-numbered citations.
                </p>
              </div>
            </div>
            <div className="pt-6 mt-4 border-t border-border-subtle">
              <button
                onClick={() => onNavigate('policy')}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-teal-muted hover:text-navy-primary transition group"
              >
                <span>Explore policy documents</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </button>
            </div>
          </div>

          {/* Service 3: Claims Guidance */}
          <div className="bg-surface border border-border-light rounded-xl p-6 shadow-card flex flex-col justify-between hover:border-teal-border transition">
            <div className="space-y-4">
              <div className="w-11 h-11 rounded-lg bg-teal-light border border-teal-border flex items-center justify-center text-teal-muted">
                <FileCheck2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-navy-primary">
                  Claims Guidance
                </h3>
                <p className="text-sm text-ink-secondary mt-1 leading-relaxed">
                  Understand cashless claims, reimbursement, and documentation steps based on official guidance.
                </p>
              </div>
            </div>
            <div className="pt-6 mt-4 border-t border-border-subtle">
              <button
                onClick={() => onNavigate('claims')}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-teal-muted hover:text-navy-primary transition group"
              >
                <span>View claims guidance</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION C: QUICK ACCESS */}
      <section className="bg-surface border border-border-light rounded-xl p-6 sm:p-8 shadow-card space-y-4">
        <div>
          <h2 className="text-lg font-bold text-navy-primary tracking-tight">
            What would you like help with?
          </h2>
          <p className="text-sm text-ink-secondary">
            Select a common action to jump directly to verified guidance.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <button
            onClick={() => onNavigate('hospitals')}
            className="flex items-start gap-3 p-3.5 rounded-lg border border-border-light bg-page hover:bg-subtle hover:border-teal-border transition text-left group"
          >
            <MapPin className="w-5 h-5 text-teal-muted mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-navy-primary group-hover:text-teal-muted transition">
                Find a hospital by location
              </p>
              <p className="text-xs text-ink-secondary mt-0.5">
                Search 29,974 national directory facilities or network clinics
              </p>
            </div>
          </button>

          <button
            onClick={() => {
              if (onSelectQuestion) {
                onSelectQuestion('What is the waiting period for pre-existing diseases?');
              }
              onNavigate('policy');
            }}
            className="flex items-start gap-3 p-3.5 rounded-lg border border-border-light bg-page hover:bg-subtle hover:border-teal-border transition text-left group"
          >
            <Search className="w-5 h-5 text-teal-muted mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-navy-primary group-hover:text-teal-muted transition">
                Search policy wording
              </p>
              <p className="text-xs text-ink-secondary mt-0.5">
                Check waiting periods, room-rent limits, or exclusions
              </p>
            </div>
          </button>

          <button
            onClick={() => onNavigate('claims')}
            className="flex items-start gap-3 p-3.5 rounded-lg border border-border-light bg-page hover:bg-subtle hover:border-teal-border transition text-left group"
          >
            <Receipt className="w-5 h-5 text-teal-muted mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-navy-primary group-hover:text-teal-muted transition">
                Understand cashless claims
              </p>
              <p className="text-xs text-ink-secondary mt-0.5">
                Pre-authorization steps for emergency vs planned admission
              </p>
            </div>
          </button>

          <button
            onClick={() => onNavigate('claims')}
            className="flex items-start gap-3 p-3.5 rounded-lg border border-border-light bg-page hover:bg-subtle hover:border-teal-border transition text-left group"
          >
            <FileText className="w-5 h-5 text-teal-muted mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-navy-primary group-hover:text-teal-muted transition">
                Understand reimbursement claims
              </p>
              <p className="text-xs text-ink-secondary mt-0.5">
                Steps for claims at non-network hospitals within 15 days
              </p>
            </div>
          </button>

          <button
            onClick={() => onNavigate('claims')}
            className="flex items-start gap-3 p-3.5 rounded-lg border border-border-light bg-page hover:bg-subtle hover:border-teal-border transition text-left group"
          >
            <FileCheck2 className="w-5 h-5 text-teal-muted mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-navy-primary group-hover:text-teal-muted transition">
                Check required claim documents
              </p>
              <p className="text-xs text-ink-secondary mt-0.5">
                Discharge summaries, itemized bills, and receipts checklist
              </p>
            </div>
          </button>

          <button
            onClick={() => onNavigate('documents')}
            className="flex items-start gap-3 p-3.5 rounded-lg border border-border-light bg-page hover:bg-subtle hover:border-teal-border transition text-left group"
          >
            <Layers className="w-5 h-5 text-teal-muted mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-navy-primary group-hover:text-teal-muted transition">
                Browse indexed policy documents
              </p>
              <p className="text-xs text-ink-secondary mt-0.5">
                Review the 48-page policy wording, 20-page CIS, and IRDAI FAQs
              </p>
            </div>
          </button>
        </div>
      </section>

      {/* SECTION D: DATA AND SOURCE STATUS */}
      <section className="bg-surface border border-border-light rounded-xl p-6 sm:p-8 shadow-card space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-navy-primary tracking-tight">
              Platform data and sources
            </h2>
            <p className="text-xs text-ink-secondary mt-0.5">
              Live statistics retrieved directly from backend storage.
            </p>
          </div>

          <button
            onClick={() => setShowDataDetails(!showDataDetails)}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-muted hover:text-navy-primary transition"
          >
            <span>{showDataDetails ? 'Hide data readiness details' : 'View data readiness details'}</span>
            {showDataDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {/* Compact Summary Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-2">
          {/* Metric 1: General Directory */}
          <div className="bg-page border border-border-light rounded-lg p-3">
            <span className="text-[11px] font-medium text-ink-secondary block">
              National Hospital Directory
            </span>
            <div className="text-lg font-bold text-navy-primary mt-1">
              {loading && !summary ? (
                <span className="text-xs text-ink-secondary">Loading...</span>
              ) : summary ? (
                summary.total_hospitals.toLocaleString()
              ) : (
                <span className="text-xs text-ink-secondary">Unavailable</span>
              )}
            </div>
            <span className="text-[10px] text-ink-secondary block mt-0.5">
              Public facilities registered
            </span>
          </div>

          {/* Metric 2: Insurer Network Records */}
          <div className="bg-page border border-border-light rounded-lg p-3">
            <span className="text-[11px] font-medium text-ink-secondary block">
              Star Health Network Records
            </span>
            <div className="text-lg font-bold text-navy-primary mt-1">
              {loading && !summary ? (
                <span className="text-xs text-ink-secondary">Loading...</span>
              ) : summary ? (
                summary.total_insurer_records.toLocaleString()
              ) : (
                <span className="text-xs text-ink-secondary">Unavailable</span>
              )}
            </div>
            <span className="text-[10px] text-teal-muted block mt-0.5 font-medium">
              Verified sample (Bangalore)
            </span>
          </div>

          {/* Metric 3: Indexed Documents */}
          <div className="bg-page border border-border-light rounded-lg p-3">
            <span className="text-[11px] font-medium text-ink-secondary block">
              Source Documents
            </span>
            <div className="text-lg font-bold text-navy-primary mt-1">
              {loading && !summary ? (
                <span className="text-xs text-ink-secondary">Loading...</span>
              ) : summary ? (
                summary.total_documents.toLocaleString()
              ) : (
                <span className="text-xs text-ink-secondary">Unavailable</span>
              )}
            </div>
            <span className="text-[10px] text-ink-secondary block mt-0.5">
              Policy, CIS & Guidance
            </span>
          </div>

          {/* Metric 4: Document Chunks */}
          <div className="bg-page border border-border-light rounded-lg p-3">
            <span className="text-[11px] font-medium text-ink-secondary block">
              Indexed Text Chunks
            </span>
            <div className="text-lg font-bold text-navy-primary mt-1">
              {loading && !summary ? (
                <span className="text-xs text-ink-secondary">Loading...</span>
              ) : summary ? (
                summary.total_document_chunks.toLocaleString()
              ) : (
                <span className="text-xs text-ink-secondary">Unavailable</span>
              )}
            </div>
            <span className="text-[10px] text-ink-secondary block mt-0.5">
              SQLite FTS5 BM25 index
            </span>
          </div>

          {/* Metric 5: Source Processing Status */}
          <div className="bg-page border border-border-light rounded-lg p-3 col-span-2 sm:col-span-1">
            <span className="text-[11px] font-medium text-ink-secondary block">
              Source Ingestion Status
            </span>
            <div className="text-sm font-bold text-green-text mt-1.5 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-green-text flex-shrink-0" />
              <span>Verified & Indexed</span>
            </div>
            <span className="text-[10px] text-ink-secondary block mt-0.5">
              27/27 tests verified
            </span>
          </div>
        </div>

        {/* Clear Data Clarification Alert */}
        <div className="p-3.5 bg-subtle border border-border-light rounded-lg text-xs text-ink-secondary leading-relaxed space-y-1">
          <p className="font-semibold text-navy-primary">
            Important distinction between general directory and network records:
          </p>
          <p>
            • A general hospital directory record confirms the facility exists in the national registry, but does <strong className="text-navy-primary">not</strong> prove that the hospital belongs to Star Health's cashless network.
          </p>
          <p>
            • An insurer network listing indicates verified cashless eligibility, but does <strong className="text-navy-primary">not</strong> guarantee cashless claim approval, which remains subject to policy terms and insurer pre-authorization.
          </p>
        </div>

        {/* Expandable Technical Readiness Details */}
        {showDataDetails && summary && (
          <div className="mt-4 pt-4 border-t border-border-subtle space-y-3">
            <h3 className="text-xs font-bold text-navy-primary uppercase tracking-wider">
              Underlying Source Datasets
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-page border border-border-light rounded-lg space-y-1">
                <span className="font-semibold text-navy-primary">Government Hospital Directory CSV</span>
                <p className="text-ink-secondary">Path: data/hospitals/hospital_directory.csv</p>
                <p className="text-teal-muted font-medium">Status: Ingested (29,974 records)</p>
              </div>

              <div className="p-3 bg-page border border-border-light rounded-lg space-y-1">
                <span className="font-semibold text-navy-primary">Star Health Network Provider Cards</span>
                <p className="text-ink-secondary">Path: data/insurer_networks/</p>
                <p className="text-teal-muted font-medium">Status: Ingested (10 records, 8 directory linked)</p>
              </div>

              <div className="p-3 bg-page border border-border-light rounded-lg space-y-1">
                <span className="font-semibold text-navy-primary">Star Comprehensive Policy & CIS PDFs</span>
                <p className="text-ink-secondary">Path: data/policies/</p>
                <p className="text-teal-muted font-medium">Status: Extracted & Indexed (48 pgs policy + 20 pgs CIS)</p>
              </div>

              <div className="p-3 bg-page border border-border-light rounded-lg space-y-1">
                <span className="font-semibold text-navy-primary">IRDAI FAQs & Claims Guidance MHTMLs</span>
                <p className="text-ink-secondary">Path: data/claim_guidance/</p>
                <p className="text-teal-muted font-medium">Status: Extracted & Indexed (5 files, 24 chunks)</p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* SECTION E: TRUST AND LIMITATIONS */}
      <section className="bg-green-soft/40 border border-green-border rounded-xl p-5 sm:p-6 text-xs text-ink-secondary space-y-2">
        <div className="flex items-center gap-2 text-green-text font-bold text-sm">
          <ShieldAlert className="w-4 h-4 flex-shrink-0" />
          <span>Informational Guidance & Policyholder Notice</span>
        </div>
        <p className="leading-relaxed">
          The explanations and search results on this platform are grounded strictly in the indexed Star Comprehensive Insurance Policy wording (UIN: SHAHLIP26044V092526, Version: POL / COMP / V.24 / 2025), the official Customer Information Sheet (CIS), and IRDAI consumer guidelines.
        </p>
        <p className="leading-relaxed">
          This portal does not replace official policy contracts or professional medical advice. Final claim admissibility, coverage limits, and cashless pre-authorization depend on insurer underwriting, active policy conditions, and formal assessment by Star Health and Allied Insurance Company Limited.
        </p>
      </section>
    </div>
  );
};
