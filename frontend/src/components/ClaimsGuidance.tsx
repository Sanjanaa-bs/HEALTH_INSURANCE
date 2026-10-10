import React, { useState, useEffect } from 'react';
import {
  FileText,
  Clock,
  AlertCircle,
  CheckCircle2,
  UploadCloud,
  Search,
  MessageSquare,
  FileCheck,
  Building2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { searchDocuments } from '../api/client';
import { SearchResultItem } from '../types';

interface ClaimsGuidanceProps {
  onAskClaimsQuestion?: (question: string) => void;
}

export const ClaimsGuidance: React.FC<ClaimsGuidanceProps> = ({ onAskClaimsQuestion }) => {
  const [activeWorkflow, setActiveWorkflow] = useState<'cashless' | 'reimbursement' | 'upload' | 'status'>('cashless');
  const [searchQuery, setSearchQuery] = useState('');
  const [guidancePassages, setGuidancePassages] = useState<SearchResultItem[]>([]);
  const [loadingPassages, setLoadingPassages] = useState(false);
  const [expandedPassage, setExpandedPassage] = useState<{ [key: number]: boolean }>({});

  const handleSearchPassages = async (term = searchQuery) => {
    if (!term.trim()) return;
    setLoadingPassages(true);
    try {
      const data = await searchDocuments(term.trim(), 'claim_guidance');
      setGuidancePassages(data.results || []);
    } catch (e) {
      // Non-blocking
    } finally {
      setLoadingPassages(false);
    }
  };

  useEffect(() => {
    const defaultQueries: { [key: string]: string } = {
      cashless: 'cashless claim pre-authorization network hospital',
      reimbursement: 'reimbursement claim discharge bills submission',
      upload: 'upload claim documents online',
      status: 'claim status tracking',
    };
    handleSearchPassages(defaultQueries[activeWorkflow] || 'claims');
  }, [activeWorkflow]);

  const togglePassage = (idx: number) => {
    setExpandedPassage((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="space-y-8 pb-12">
      {/* 1. INTRODUCTORY BANNER WITH CLAIMS DOCUMENTATION IMAGE */}
      <section className="bg-navy-850 border border-navy-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="grid grid-cols-1 md:grid-cols-12 items-center">
          <div className="p-6 sm:p-8 md:col-span-8 space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-3 py-1 rounded-full inline-block">
              Claims Procedure Guide
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Health Insurance Claims Help
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              Understand step-by-step procedures for Cashless Hospitalisation at network providers, Reimbursement submissions for non-network hospitals, and mandatory document checklists.
            </p>
            {onAskClaimsQuestion && (
              <div className="pt-2">
                <button
                  onClick={() => onAskClaimsQuestion('What documents are required for reimbursement claims?')}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/30 transition"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Ask a Claim Question</span>
                </button>
              </div>
            )}
          </div>

          <div className="md:col-span-4 h-36 md:h-full relative overflow-hidden bg-navy-950">
            <img
              src="/images/claims_documentation.jpg"
              alt="Healthcare claims specialist reviewing medical insurance documents"
              className="w-full h-full object-cover object-center"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-navy-850 via-transparent to-transparent hidden md:block" />
          </div>
        </div>
      </section>

      {/* 2. MAIN CLAIMS GUIDANCE CONTAINER */}
      <div className="bg-navy-850 border border-navy-800 rounded-2xl shadow-xl p-6 sm:p-8 space-y-6">
        {/* Safety & Non-Guarantee Notice */}
        <div className="p-4 rounded-xl bg-navy-950/80 border border-navy-800 text-xs text-slate-300 space-y-1 leading-relaxed">
          <div className="flex items-center gap-2 text-cyan-300 font-semibold">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>Informational Guidance Notice — No Claim Decision Guarantee</span>
          </div>
          <p>
            The guidance presented below is compiled strictly from official Star Health procedure documentation and IRDAI regulations. This portal does not submit live claims or guarantee pre-authorization or reimbursement. Final approvals remain subject to insurer assessment and policy conditions.
          </p>
        </div>

        {/* Workflow Tabs: Two clearly separated primary options + checklist + tracking */}
        <div className="flex items-center gap-2 pb-2 border-b border-navy-800 overflow-x-auto">
          {[
            { id: 'cashless', label: '1. Cashless Claims (Network)', icon: Building2 },
            { id: 'reimbursement', label: '2. Reimbursement Claims (Paid)', icon: FileCheck },
            { id: 'upload', label: '3. Required Documents Checklist', icon: UploadCloud },
            { id: 'status', label: '4. Claim Status Tracking', icon: Clock },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeWorkflow === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveWorkflow(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'bg-navy-900 text-slate-300 border border-navy-800 hover:text-white hover:bg-navy-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Workflow Details & Search Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          {/* Left 2 Columns: Selected Procedure Steps */}
          <div className="lg:col-span-2 space-y-4">
            {/* Cashless Workflow */}
            {activeWorkflow === 'cashless' && (
              <div className="border border-navy-800 rounded-xl p-6 bg-navy-900/60 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-navy-800">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-emerald-400" />
                    Cashless Hospitalisation Procedure
                  </h3>
                  <span className="text-[10px] font-bold uppercase bg-emerald-950 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded">
                    Network Hospitals Only
                  </span>
                </div>

                <div className="space-y-4 text-xs text-slate-200">
                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      1
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Intimate Insurer & Approach TPA Desk</p>
                      <p className="text-slate-400 leading-relaxed">
                        For <strong>Planned Hospitalisation</strong>: Intimate Star Health and visit the hospital's TPA / insurance helpdesk at least 48 to 72 hours prior to admission. For <strong>Emergency Hospitalisation</strong>: Intimate within 24 hours of hospital admission.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      2
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Submit Pre-Authorization Request</p>
                      <p className="text-slate-400 leading-relaxed">
                        Present your Star Health ID card or policy copy, government photo ID, doctor's consultation note, and initial test reports to the hospital desk. The hospital transmits the pre-authorization form directly to Star Health.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      3
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Initial Approval & Treatment</p>
                      <p className="text-slate-400 leading-relaxed">
                        The insurer evaluates medical necessity and issues an initial sanction letter. The hospital initiates cashless treatment without demanding advance payment for covered items.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      4
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Discharge & Final Claim Settlement</p>
                      <p className="text-slate-400 leading-relaxed">
                        Upon discharge, the hospital sends final itemized bills. The insurer completes authorization. The policyholder pays only non-payable items, co-payments, or expenses exceeding policy sub-limits.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Reimbursement Workflow */}
            {activeWorkflow === 'reimbursement' && (
              <div className="border border-navy-800 rounded-xl p-6 bg-navy-900/60 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-navy-800">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <FileCheck className="w-5 h-5 text-cyan-400" />
                    Reimbursement Claim Procedure
                  </h3>
                  <span className="text-[10px] font-bold uppercase bg-navy-950 text-slate-300 border border-navy-800 px-2 py-0.5 rounded">
                    Any Registered Hospital
                  </span>
                </div>

                <div className="space-y-4 text-xs text-slate-200">
                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      1
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Settle Bills Directly Upon Discharge</p>
                      <p className="text-slate-400 leading-relaxed">
                        Settle all hospitalization expenses with the hospital. Collect all original payment receipts with revenue stamps, detailed final bills with breakup, and the physician's discharge summary.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      2
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Submit Claim Within 15 Days of Discharge</p>
                      <p className="text-slate-400 leading-relaxed">
                        Fill out the Star Health Claim Form (Part A filled by policyholder, Part B by treating physician). Submit all original invoices, prescriptions, diagnostic films, and proof of payment within 15 days of discharge.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 bg-navy-950 p-4 rounded-xl border border-navy-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                      3
                    </div>
                    <div className="space-y-1">
                      <p className="font-bold text-white">Post-Hospitalisation Submission (Within 30 Days)</p>
                      <p className="text-slate-400 leading-relaxed">
                        Submit medical expenses incurred after hospital discharge (e.g. follow-up consults, diagnostic tests) within 30 days following the end of the policy's post-hospitalization window (up to 90 days).
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Document Checklist */}
            {activeWorkflow === 'upload' && (
              <div className="border border-navy-800 rounded-xl p-6 bg-navy-900/60 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-navy-800">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <UploadCloud className="w-5 h-5 text-cyan-400" />
                    Required Claim Documents Checklist
                  </h3>
                  <span className="text-[10px] font-bold uppercase bg-cyan-950 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded">
                    Verification Checklist
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="bg-navy-950 p-4 rounded-xl border border-navy-800 space-y-2">
                    <p className="font-bold text-white flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      Hospital Records
                    </p>
                    <ul className="space-y-1.5 text-slate-400 list-disc list-inside">
                      <li>Original detailed Discharge Summary</li>
                      <li>Attending doctor's first consultation paper</li>
                      <li>Final hospital bill with itemized breakup</li>
                      <li>Original paid receipts with revenue stamp</li>
                    </ul>
                  </div>

                  <div className="bg-navy-950 p-4 rounded-xl border border-navy-800 space-y-2">
                    <p className="font-bold text-white flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      Pharmacy & Diagnostics
                    </p>
                    <ul className="space-y-1.5 text-slate-400 list-disc list-inside">
                      <li>Doctor's prescription for all medicines claimed</li>
                      <li>Itemized pharmacy cash memos</li>
                      <li>Diagnostic reports with imaging films (X-ray, MRI, CT)</li>
                      <li>Implant stickers and invoices (if applicable)</li>
                    </ul>
                  </div>

                  <div className="bg-navy-950 p-4 rounded-xl border border-navy-800 space-y-2 sm:col-span-2">
                    <p className="font-bold text-white flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      KYC & Settlement Proofs
                    </p>
                    <ul className="space-y-1.5 text-slate-400 list-disc list-inside">
                      <li>Cancelled cheque with printed account holder name and IFSC code</li>
                      <li>Government photo ID of the primary policyholder (Aadhaar/PAN/Passport)</li>
                      <li>Duly completed and signed Star Health Claim Form (Part A & B)</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Status Tracking */}
            {activeWorkflow === 'status' && (
              <div className="border border-navy-800 rounded-xl p-6 bg-navy-900/60 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-navy-800">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Clock className="w-5 h-5 text-amber-400" />
                    Official Claim Tracking Channels
                  </h3>
                  <span className="text-[10px] font-bold uppercase bg-navy-950 text-slate-300 border border-navy-800 px-2 py-0.5 rounded">
                    Official Reference
                  </span>
                </div>

                <div className="space-y-4 text-xs text-slate-200">
                  <p className="text-slate-300 leading-relaxed">
                    To check the current adjudication stage on an ongoing claim, use Star Health's verified customer channels:
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="bg-navy-950 p-4 rounded-xl border border-navy-800 space-y-1.5">
                      <p className="font-bold text-white">1. Claim Number</p>
                      <p className="text-slate-400 text-[11px]">
                        Locate the 16-digit claim registration number received via SMS.
                      </p>
                    </div>
                    <div className="bg-navy-950 p-4 rounded-xl border border-navy-800 space-y-1.5">
                      <p className="font-bold text-white">2. Insurer Web Portal</p>
                      <p className="text-slate-400 text-[11px]">
                        Visit the Star Health official claim tracking portal with Policy No. + Health ID.
                      </p>
                    </div>
                    <div className="bg-navy-950 p-4 rounded-xl border border-navy-800 space-y-1.5">
                      <p className="font-bold text-white">3. Toll-Free Helpline</p>
                      <p className="text-slate-400 text-[11px]">
                        Star Health Claims Desk: 1800 425 2255 / 1800 102 4477.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Searchable Indexed Passages */}
          <div className="space-y-4">
            <div className="border border-navy-800 rounded-xl p-5 bg-navy-900/60 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-navy-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  Indexed Procedure Passages
                </h4>
                <span className="text-[11px] text-slate-400 font-mono">
                  {guidancePassages.length} matched
                </span>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearchPassages();
                }}
                className="relative"
              >
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search claims guidance..."
                  className="w-full bg-navy-950 border border-navy-700 text-xs text-white rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-cyan-400 transition"
                  aria-label="Search claims guidance"
                />
              </form>

              {loadingPassages ? (
                <div className="space-y-2 animate-pulse">
                  <div className="h-16 bg-navy-950 rounded-lg border border-navy-800" />
                  <div className="h-16 bg-navy-950 rounded-lg border border-navy-800" />
                </div>
              ) : guidancePassages.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">
                  No matching claim guidance passages found.
                </p>
              ) : (
                <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
                  {guidancePassages.map((p, idx) => {
                    const isExp = !!expandedPassage[idx];
                    return (
                      <div
                        key={p.chunk_id || idx}
                        className="bg-navy-950 border border-navy-800 rounded-lg p-3 text-xs space-y-2"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="font-semibold text-white text-[11px] leading-snug">
                            {p.document_title}
                          </span>
                          <span className="text-[10px] font-mono bg-navy-900 text-cyan-300 border border-navy-800 px-1.5 py-0.5 rounded flex-shrink-0">
                            {p.page_label || `Chunk ${p.chunk_id}`}
                          </span>
                        </div>

                        {p.section_heading && (
                          <p className="text-[11px] text-slate-400">
                            Section: <span className="text-slate-200">{p.section_heading}</span>
                          </p>
                        )}

                        <button
                          onClick={() => togglePassage(idx)}
                          className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                        >
                          {isExp ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          {isExp ? 'Collapse snippet' : 'View excerpt'}
                        </button>

                        {isExp && (
                          <div
                            className="p-2.5 bg-navy-900 rounded border border-navy-800 text-[11px] text-slate-300 leading-relaxed font-sans"
                            dangerouslySetInnerHTML={{ __html: p.excerpt }}
                          />
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
