import React, { useState, useEffect } from 'react';
import {
  Search,
  ShieldCheck,
  AlertCircle,
  BookOpen,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Copy,
  Check,
  FileText,
  HelpCircle,
  Sparkles,
  Layers,
} from 'lucide-react';
import { QuestionResponse } from '../types';
import { askQuestion } from '../api/client';
import { MarkdownView } from './MarkdownView';

interface PolicyQAProps {
  initialQuestion?: string;
  onNavigateToSearch?: (query: string) => void;
}

export const PolicyQA: React.FC<PolicyQAProps> = ({
  initialQuestion = 'What is the waiting period for pre-existing diseases?',
  onNavigateToSearch,
}) => {
  const [question, setQuestion] = useState(initialQuestion);
  const [documentTypeFilter, setDocumentTypeFilter] = useState<string>('');
  const [response, setResponse] = useState<QuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedCitations, setExpandedCitations] = useState<{ [key: number]: boolean }>({});
  const [copiedAnswer, setCopiedAnswer] = useState(false);

  const sampleQuestions = [
    {
      label: 'Pre-existing Disease Waiting Period',
      text: 'What is the waiting period for pre-existing diseases?',
    },
    {
      label: 'Room-Rent & ICU Limits',
      text: 'What does the policy say about room rent?',
    },
    {
      label: 'Pre-Hospitalization Expenses',
      text: 'What does the policy say about pre-hospitalisation expenses?',
    },
    {
      label: 'Cataract Treatment Conditions',
      text: 'Are cataract treatments subject to specific conditions?',
    },
    {
      label: 'Standard Policy Exclusions',
      text: "What are the policy's exclusions?",
    },
    {
      label: 'Safety Abstention Test',
      text: 'What is the policy for orbital space flight and planetary excursion?',
    },
  ];

  const handleAsk = async (qToAsk?: string) => {
    const q = (qToAsk ?? question).trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    try {
      const data = await askQuestion({
        question: q,
        document_type: documentTypeFilter || undefined,
        max_citations: 5,
      });
      setResponse(data);
      // Auto-collapse citations by default as requested:
      // "Allow users to expand source details instead of showing lengthy raw retrieval excerpts by default"
      setExpandedCitations({});
    } catch (err: any) {
      setError(
        err.message || 'Unable to retrieve grounded policy response. Please check backend connection.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuestion) {
      handleAsk(initialQuestion);
    }
  }, [initialQuestion]);

  const toggleCitation = (idx: number) => {
    setExpandedCitations((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleCopyAnswer = () => {
    if (!response?.answer) return;
    navigator.clipboard.writeText(response.answer);
    setCopiedAnswer(true);
    setTimeout(() => setCopiedAnswer(false), 2000);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* 1. PAGE HEADER */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-500/30 text-cyan-300 text-xs font-semibold">
          <FileText className="w-3.5 h-3.5 text-cyan-400" />
          <span>Evidence-Grounded Policy Verification</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Policy Information & Verification
        </h1>
        <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
          Ask specific questions regarding coverage, waiting periods, room-rent categories, or exclusions. Answers are synthesized strictly from indexed Star Comprehensive policy wording (POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526) and Customer Information Sheets.
        </p>
      </div>

      {/* 2. QUESTION INPUT FORM */}
      <div className="bg-navy-850 border border-navy-800 rounded-2xl p-6 shadow-xl space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="space-y-3"
        >
          <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
            <div className="relative flex-1">
              <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about your policy, coverage, waiting periods, or exclusions..."
                className="w-full bg-white border border-slate-300 hover:border-slate-400 rounded-xl pl-11 pr-4 py-3 text-sm text-[#0C162E] font-medium placeholder:text-[#64748B] caret-[#0C162E] focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition"
                aria-label="Ask policy question"
              />
            </div>

            <select
              value={documentTypeFilter}
              onChange={(e) => setDocumentTypeFilter(e.target.value)}
              className="bg-white border border-slate-300 hover:border-slate-400 rounded-xl px-3.5 py-3 text-xs sm:text-sm text-[#0C162E] font-medium focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition cursor-pointer"
              aria-label="Filter source document"
            >
              <option value="" className="text-[#0C162E] bg-white">All Source Documents</option>
              <option value="policy" className="text-[#0C162E] bg-white">Full Policy Terms & Conditions</option>
              <option value="cis" className="text-[#0C162E] bg-white">Customer Information Sheet (CIS)</option>
              <option value="claim_guidance" className="text-[#0C162E] bg-white">Official Claims Guidance</option>
              <option value="faq" className="text-[#0C162E] bg-white">IRDAI Regulations FAQs</option>
            </select>

            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs sm:text-sm font-semibold transition shadow-md shadow-blue-600/30 disabled:opacity-50 flex items-center justify-center gap-2 whitespace-nowrap"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <span>Ask Question</span>
              )}
            </button>
          </div>

          {/* Example Questions */}
          <div className="pt-2">
            <span className="text-xs font-medium text-slate-400 block mb-2">
              Common questions you can ask:
            </span>
            <div className="flex flex-wrap gap-2">
              {sampleQuestions.map((sq, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setQuestion(sq.text);
                    handleAsk(sq.text);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium bg-navy-900 text-slate-300 border border-navy-800 hover:border-cyan-500/50 hover:text-white hover:bg-navy-800 transition text-left"
                >
                  {sq.label}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* 3. ERROR STATE */}
      {error && (
        <div className="p-4 bg-red-950/40 border border-red-500/30 text-red-200 rounded-xl text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => handleAsk()} className="underline font-semibold ml-4">
            Retry
          </button>
        </div>
      )}

      {/* 4. LOADING STATE */}
      {loading && (
        <div className="bg-navy-850 border border-navy-800 rounded-2xl p-8 space-y-4 animate-pulse">
          <div className="h-5 bg-navy-800 rounded w-1/4" />
          <div className="h-4 bg-navy-800 rounded w-full" />
          <div className="h-4 bg-navy-800 rounded w-5/6" />
          <div className="h-4 bg-navy-800 rounded w-2/3" />
        </div>
      )}

      {/* 5. ANSWER AREA */}
      {!loading && response && (
        <div className="space-y-6">
          <div className="bg-navy-850 border border-navy-800 rounded-2xl shadow-xl overflow-hidden">
            {/* Answer Header Bar */}
            <div className="px-6 py-4 border-b border-navy-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-navy-900/60">
              <div className="flex items-center gap-3">
                {response.is_sufficient_evidence ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-500/40">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    Verified Evidence Grounded
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-950/60 text-amber-300 border border-amber-500/40">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                    Insufficient Policy Evidence
                  </span>
                )}

                {/* Subtle Response-Mode Indicator */}
                {response.generation_mode === 'RAG + LLM' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-950/90 text-cyan-300 border border-cyan-500/40" title="Retrieved via semantic hybrid search and synthesized with LLM">
                    <Sparkles className="w-3 h-3 text-cyan-400" />
                    RAG + LLM
                  </span>
                )}
                {response.generation_mode === 'Hybrid Retrieval' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-950/90 text-blue-300 border border-blue-500/40" title="Retrieved via BM25 + dense vector hybrid search with grounded synthesis">
                    <Layers className="w-3 h-3 text-blue-400" />
                    Hybrid Retrieval
                  </span>
                )}
                {response.generation_mode === 'Keyword Retrieval Fallback' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-900/90 text-slate-300 border border-slate-700/60" title="Retrieved via BM25 keyword index">
                    <Search className="w-3 h-3 text-slate-400" />
                    Keyword Retrieval Fallback
                  </span>
                )}

                <span className="text-xs text-slate-400">
                  {response.citations?.length || 0} source citation{response.citations?.length === 1 ? '' : 's'}
                </span>
              </div>

              <div className="flex items-center gap-2">
                {onNavigateToSearch && (
                  <button
                    onClick={() => onNavigateToSearch(response.question)}
                    className="inline-flex items-center gap-1 text-xs text-cyan-300 hover:text-white px-3 py-1.5 rounded-lg border border-navy-700 bg-navy-900 hover:bg-navy-800 transition"
                  >
                    <span>Browse Sources &rarr;</span>
                  </button>
                )}
                <button
                  onClick={handleCopyAnswer}
                  className="inline-flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-navy-700 bg-navy-900 hover:bg-navy-800 transition"
                  title="Copy response to clipboard"
                >
                  {copiedAnswer ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-300 font-medium">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-slate-400" />
                      <span>Copy Answer</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Answer Body (Correctly Formatted with MarkdownView!) */}
            <div className="p-6 sm:p-8 space-y-4">
              <div className="text-xs uppercase tracking-wider font-semibold text-cyan-400">
                Question: &ldquo;{response.question}&rdquo;
              </div>

              {/* Formatted Markdown without literal asterisks */}
              <div className="bg-navy-950/70 p-5 rounded-xl border border-navy-800/80">
                <MarkdownView content={response.answer} />
              </div>

              {/* Insufficient Evidence Notice */}
              {!response.is_sufficient_evidence && (
                <div className="p-4 bg-amber-950/30 border border-amber-500/30 rounded-xl text-xs text-amber-200/90 space-y-1">
                  <p className="font-bold text-amber-200">Abstention Rule & Absence Principle:</p>
                  <p>
                    The absence of a search match in the indexed policy files does not prove that a condition or treatment is excluded or denied. Please verify with official Star Health policy documentation or contact customer support for binding coverage determinations.
                  </p>
                </div>
              )}
            </div>

            {/* Disclaimer Footer */}
            <div className="px-6 py-3 border-t border-navy-800/80 bg-navy-900/40 text-xs text-slate-400 flex items-start gap-2">
              <HelpCircle className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
              <span>{response.disclaimer}</span>
            </div>
          </div>

          {/* 6. EXPANDABLE SOURCE CITATIONS */}
          {response.citations && response.citations.length > 0 && (
            <div className="bg-navy-850 border border-navy-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-cyan-400" />
                  Verified Source Citations ({response.citations.length})
                </h2>
                <span className="text-xs text-slate-400">
                  Click to inspect exact supporting clauses
                </span>
              </div>

              <div className="space-y-3">
                {response.citations.map((c, idx) => {
                  const isExpanded = !!expandedCitations[idx];
                  return (
                    <div
                      key={c.chunk_id || idx}
                      className="border border-navy-800 rounded-xl bg-navy-900 overflow-hidden transition"
                    >
                      <button
                        onClick={() => toggleCitation(idx)}
                        className="w-full px-5 py-3.5 text-left flex items-center justify-between gap-3 hover:bg-navy-850 transition"
                      >
                        <div className="flex flex-wrap items-center gap-2.5">
                          <span className="text-xs font-bold text-white">
                            {c.document_title}
                          </span>
                          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-950 text-cyan-300 border border-blue-500/30">
                            {c.page_label || `Page ${c.page_number}`}
                          </span>
                          {c.section_heading && (
                            <span className="text-xs text-slate-400">
                              Section: {c.section_heading}
                            </span>
                          )}
                        </div>
                        <div className="text-slate-400 flex items-center gap-1.5 text-xs">
                          <span className="hidden sm:inline">{isExpanded ? 'Hide' : 'Inspect'}</span>
                          {isExpanded ? <ChevronUp className="w-4 h-4 text-cyan-400" /> : <ChevronDown className="w-4 h-4" />}
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="px-5 pb-5 pt-2 border-t border-navy-800 bg-navy-950/60 space-y-2.5 text-xs">
                          <div className="p-3.5 bg-navy-900 rounded-lg border border-navy-800 text-slate-200 leading-relaxed font-sans">
                            &ldquo;{c.supporting_text}&rdquo;
                          </div>
                          <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400 pt-1 font-mono">
                            <span>Document Version: {c.version || 'Standard'}</span>
                            {c.content_hash && (
                              <span>SHA-256 Hash: {c.content_hash.slice(0, 20)}...</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
