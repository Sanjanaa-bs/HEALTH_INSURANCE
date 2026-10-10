import React, { useState, useEffect } from 'react';
import {
  FileText,
  Layers,
  CheckCircle2,
  Search,
  BookOpen,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Info,
} from 'lucide-react';
import { Document, PaginationMeta, SearchResultItem, QuestionResponse } from '../types';
import { fetchDocuments, searchDocuments, askQuestion } from '../api/client';

export const DocumentExplorer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'qa' | 'search' | 'catalogue'>('qa');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
  });
  const [typeFilter, setTypeFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('cataract');
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Grounded QA state
  const [qaQuestion, setQaQuestion] = useState('What is the waiting period for pre-existing diseases?');
  const [qaResponse, setQaResponse] = useState<QuestionResponse | null>(null);
  const [asking, setAsking] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState<{ [key: number]: boolean }>({});

  const handleAskQuestion = async (q = qaQuestion) => {
    if (!q.trim()) return;
    setAsking(true);
    setError(null);
    try {
      const data = await askQuestion({
        question: q.trim(),
        document_type: typeFilter || undefined,
        max_citations: 5,
      });
      setQaResponse(data);
    } catch (err: any) {
      setError(err.message || 'Failed to answer question');
    } finally {
      setAsking(false);
    }
  };

  const toggleCitation = (idx: number) => {
    setExpandedCitations((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const loadDocuments = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments({
        page,
        pageSize: 10,
        documentType: typeFilter || undefined,
      });
      setDocuments(data.items);
      setPagination(data.pagination);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query = searchQuery) => {
    if (!query.trim()) return;
    setSearching(true);
    setError(null);
    try {
      const data = await searchDocuments(query.trim(), typeFilter || undefined);
      setSearchResults(data.results);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    loadDocuments(1);
    handleSearch('cataract');
    handleAskQuestion('What is the waiting period for pre-existing diseases?');
  }, [typeFilter]);

  const handleSearchFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(searchQuery);
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Policy & Guidance Knowledge Base
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Indexed Star Comprehensive policies, customer information sheets, and IRDAI regulations
          </p>
        </div>

        {/* View mode toggle */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('qa')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'qa'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Grounded Q&A</span>
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'search'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Passage Search</span>
          </button>
          <button
            onClick={() => setActiveTab('catalogue')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'catalogue'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Document Catalogue</span>
          </button>
        </div>
      </div>

      {/* Type Filter Buttons */}
      <div className="flex items-center gap-2">
        {['', 'policy', 'cis', 'claim_guidance', 'faq'].map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`px-3 py-1 rounded-lg text-[11px] font-semibold capitalize transition border ${
              typeFilter === t
                ? 'bg-slate-800 border-blue-500 text-blue-400'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            {t === '' ? 'All Types' : t.replace('_', ' ')}
          </button>
        ))}
      </div>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs">
          {error}
        </div>
      )}

      {/* GROUNDED Q&A TAB */}
      {activeTab === 'qa' && (
        <div className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAskQuestion(qaQuestion);
            }}
            className="flex items-center gap-2"
          >
            <div className="relative flex-1">
              <MessageSquare className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Ask an insurance question (e.g. What is the waiting period for pre-existing diseases?)..."
                value={qaQuestion}
                onChange={(e) => setQaQuestion(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-xl pl-9 pr-3 py-2.5 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
            <button
              type="submit"
              disabled={asking}
              className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition disabled:opacity-50"
            >
              {asking ? 'Answering...' : 'Ask Question'}
            </button>
          </form>

          {/* Quick sample chips */}
          <div className="flex items-center gap-1.5 flex-wrap text-xs text-slate-400">
            <span className="text-[11px] text-slate-500">Sample Questions:</span>
            {[
              'What is the waiting period for pre-existing diseases?',
              'What does the policy say about room rent?',
              'Are cataract treatments subject to specific conditions?',
              'What does the policy say about pre-hospitalisation expenses?',
              "What are the policy's exclusions?",
              'What is the policy for orbital space flight and planetary excursion?',
            ].map((q) => (
              <button
                key={q}
                onClick={() => {
                  setQaQuestion(q);
                  handleAskQuestion(q);
                }}
                className="bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 text-[11px] px-2 py-0.5 rounded-md transition truncate max-w-[200px]"
                title={q}
              >
                {q}
              </button>
            ))}
          </div>

          {/* QA Response Card */}
          {asking ? (
            <div className="p-6 bg-slate-950/70 border border-slate-800 rounded-xl animate-pulse space-y-3">
              <div className="h-4 bg-slate-800 rounded w-1/4" />
              <div className="h-16 bg-slate-800/60 rounded" />
            </div>
          ) : qaResponse ? (
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
                <span className="font-bold text-white text-xs">
                  Q: {qaResponse.question}
                </span>
                <div className="flex items-center gap-2">
                  {qaResponse.is_sufficient_evidence ? (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                      <ShieldCheck className="w-3 h-3" /> Grounded Evidence Answered
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                      <AlertTriangle className="w-3 h-3" /> Insufficient Evidence (Abstained)
                    </span>
                  )}
                  <span className="text-[10px] text-slate-400 font-mono bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                    {qaResponse.provider}
                  </span>
                </div>
              </div>

              <div className="text-xs text-slate-200 leading-relaxed bg-slate-900/50 p-4 rounded-xl border border-slate-800/60 whitespace-pre-line font-sans">
                {qaResponse.answer}
              </div>

              {qaResponse.citations.length > 0 && (
                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                    Verified Document Citations ({qaResponse.citations.length})
                  </h4>
                  <div className="space-y-2">
                    {qaResponse.citations.map((cite, idx) => (
                      <div
                        key={cite.chunk_id || idx}
                        className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <span className="font-semibold text-blue-300">
                            {cite.document_title}
                          </span>
                          <div className="flex items-center gap-2 font-mono text-[10px]">
                            {cite.version && (
                              <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-1.5 py-0.5 rounded">
                                {cite.version}
                              </span>
                            )}
                            <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1.5 py-0.5 rounded uppercase">
                              {cite.document_type}
                            </span>
                            {cite.page_label && (
                              <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                                {cite.page_label}
                              </span>
                            )}
                          </div>
                        </div>

                        {cite.section_heading && (
                          <p className="text-[11px] text-slate-400 font-medium">
                            Section: <span className="text-slate-300">{cite.section_heading}</span>
                          </p>
                        )}

                        <button
                          onClick={() => toggleCitation(idx)}
                          className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 transition pt-1"
                        >
                          {expandedCitations[idx] ? (
                            <>
                              <ChevronUp className="w-3 h-3" /> Hide Supporting Passage
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-3 h-3" /> Show Supporting Passage
                            </>
                          )}
                        </button>

                        {expandedCitations[idx] && (
                          <div className="p-2.5 bg-slate-950/80 rounded border border-slate-800 text-[11px] text-slate-300 mt-1.5 leading-relaxed font-sans">
                            {cite.supporting_text}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-start gap-2 p-3 bg-slate-900/40 border border-slate-800/60 rounded-lg text-[11px] text-slate-400">
                <Info className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                <p>{qaResponse.disclaimer}</p>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* PASSAGE SEARCH TAB */}
      {activeTab === 'search' && (
        <div className="space-y-4">
          <form onSubmit={handleSearchFormSubmit} className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search policy terms (e.g. cataract, waiting period, reimbursement, IRDAI)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-xl pl-9 pr-3 py-2.5 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
            <button
              type="submit"
              disabled={searching}
              className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition disabled:opacity-50"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {/* Quick sample chips */}
          <div className="flex items-center gap-1.5 flex-wrap text-xs text-slate-400">
            <span className="text-[11px] text-slate-500">Quick Queries:</span>
            {['cataract', 'cashless claim', 'waiting period', 'reimbursement', 'IRDAI'].map((q) => (
              <button
                key={q}
                onClick={() => {
                  setSearchQuery(q);
                  handleSearch(q);
                }}
                className="bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 text-[11px] px-2 py-0.5 rounded-md transition"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Search Results List */}
          <div className="space-y-3 pt-2">
            {searching ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-24 bg-slate-800/40 border border-slate-800 rounded-xl" />
                ))}
              </div>
            ) : searchResults.length === 0 ? (
              <div className="py-8 text-center text-slate-500 border border-slate-800 rounded-xl bg-slate-950/40 text-xs">
                No indexed passages matched query "{searchQuery}".
              </div>
            ) : (
              searchResults.map((res) => (
                <div
                  key={res.chunk_id}
                  className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition"
                >
                  <div className="flex items-center justify-between gap-2 flex-wrap text-xs">
                    <span className="font-bold text-blue-300 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-blue-400" />
                      {res.document_title}
                    </span>
                    <div className="flex items-center gap-2 font-mono text-[11px]">
                      {res.page_number && (
                        <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                          Page {res.page_number}
                        </span>
                      )}
                      <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded uppercase">
                        {res.document_type}
                      </span>
                    </div>
                  </div>

                  {res.section_heading && (
                    <p className="text-xs font-semibold text-slate-300">
                      Section: <span className="text-slate-200">{res.section_heading}</span>
                    </p>
                  )}

                  <p
                    className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800/60 font-sans"
                    dangerouslySetInnerHTML={{ __html: res.excerpt }}
                  />
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* DOCUMENT CATALOGUE TAB */}
      {activeTab === 'catalogue' && (
        <div className="space-y-4">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-28 bg-slate-800/40 border border-slate-800 rounded-xl" />
              ))}
            </div>
          ) : documents.length === 0 ? (
            <div className="py-10 text-center text-slate-500 border border-slate-800 rounded-xl bg-slate-950/40">
              No database document records found.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition space-y-3"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-bold text-white tracking-tight truncate">
                        {doc.title}
                      </span>
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {doc.file_format}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-mono truncate">{doc.source_path}</p>
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-800/60">
                    <div className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-purple-400" />
                      <span>{doc.chunk_count} chunks</span>
                    </div>

                    <div>
                      {doc.is_processed ? (
                        <span className="flex items-center gap-1 text-emerald-400 text-[11px] font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Text Extracted
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-amber-400 text-[11px] font-semibold" title="PDF stream decompression error / raster image pages">
                          <AlertTriangle className="w-3.5 h-3.5" /> Failed Stream Decompression
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {pagination.total_pages > 1 && (
            <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
              <span>
                Page <strong className="text-white">{pagination.page}</strong> of{' '}
                <strong className="text-white">{pagination.total_pages}</strong>
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => loadDocuments(pagination.page - 1)}
                  disabled={pagination.page <= 1 || loading}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 transition border border-slate-700 text-slate-200"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => loadDocuments(pagination.page + 1)}
                  disabled={pagination.page >= pagination.total_pages || loading}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 transition border border-slate-700 text-slate-200"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
