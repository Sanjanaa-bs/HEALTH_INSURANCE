import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { Document, SearchResultItem } from '../types';
import { fetchDocuments, searchDocuments } from '../api/client';

interface DocumentLibraryProps {
  onAskAboutClause?: (query: string) => void;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({ onAskAboutClause }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [selectedType, setSelectedType] = useState('');
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const documentTypes = [
    { id: '', label: 'All Documents' },
    { id: 'policy', label: 'Policy Terms & Conditions' },
    { id: 'cis', label: 'Customer Information Sheet (CIS)' },
    { id: 'claim_guidance', label: 'Claims Guidance' },
    { id: 'faq', label: 'IRDAI Regulatory Guidelines' },
  ];

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments({ page: 1, pageSize: 20 });
      setDocuments(data.items || []);
    } catch (e: any) {
      setError(e.message || 'Failed to load document catalog');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    setError(null);
    try {
      const data = await searchDocuments(searchQuery.trim(), selectedType || undefined);
      setSearchResults(data.results || []);
    } catch (e: any) {
      setError(e.message || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const filteredDocs = selectedType
    ? documents.filter((d) => d.document_type === selectedType)
    : documents;

  return (
    <div className="space-y-8 pb-12">
      {/* 1. PAGE HEADER */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-500/30 text-cyan-300 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
          <span>Official Legal Sources & Guidance Documents</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Document Library & Policy Search
        </h1>
        <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
          Browse and search indexed policy contracts, Customer Information Sheets (CIS), operational claim guides, and IRDAI health insurance regulatory FAQs.
        </p>
      </div>

      {/* 2. SEARCH & FILTER BAR */}
      <div className="bg-navy-850 border border-navy-800 rounded-2xl p-6 shadow-xl space-y-4">
        <form onSubmit={handleSearch} className="space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
            <div className="relative flex-1">
              <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search policy wording and clauses (e.g. room rent, waiting period, cataract, exclusions)..."
                className="w-full bg-white border border-slate-300 hover:border-slate-400 rounded-xl pl-11 pr-4 py-3 text-sm text-[#0C162E] font-medium placeholder:text-[#64748B] caret-[#0C162E] focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition"
                aria-label="Search policy wording"
              />
            </div>

            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="bg-white border border-slate-300 hover:border-slate-400 rounded-xl px-3.5 py-3 text-xs sm:text-sm text-[#0C162E] font-medium focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition cursor-pointer"
              aria-label="Filter document type"
            >
              {documentTypes.map((t) => (
                <option key={t.id} value={t.id} className="text-[#0C162E] bg-white">
                  {t.label}
                </option>
              ))}
            </select>

            <button
              type="submit"
              disabled={searching}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs sm:text-sm font-semibold transition shadow-md shadow-blue-600/30 disabled:opacity-50 flex items-center justify-center gap-2 whitespace-nowrap"
            >
              {searching ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <span>Search Documents</span>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-950/40 border border-red-500/30 text-red-200 rounded-xl text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => loadDocuments()} className="underline font-semibold ml-4">
            Retry
          </button>
        </div>
      )}

      {/* 3. SEARCH RESULTS (IF SEARCHING) */}
      {searchResults.length > 0 && (
        <div className="bg-navy-850 border border-navy-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-navy-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Search className="w-4 h-4 text-cyan-400" />
              Search Results ({searchResults.length} matching clauses)
            </h2>
            <button
              onClick={() => {
                setSearchQuery('');
                setSearchResults([]);
              }}
              className="text-xs text-slate-400 hover:text-white underline"
            >
              Clear Search
            </button>
          </div>

          <div className="space-y-3">
            {searchResults.map((item, idx) => (
              <div
                key={item.chunk_id || idx}
                className="bg-navy-900 border border-navy-800 hover:border-navy-700 rounded-xl p-4 text-xs transition space-y-2.5"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-white text-xs sm:text-sm">
                      {item.document_title}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-950 text-cyan-300 border border-blue-500/30 uppercase">
                      {item.document_type.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="font-mono text-[11px] text-slate-400">
                    {item.page_label ? (
                      <span className="bg-navy-950 px-2 py-0.5 rounded border border-navy-800 text-cyan-300">
                        {item.page_label}
                      </span>
                    ) : item.page_number ? (
                      <span>Page {item.page_number}</span>
                    ) : null}
                  </div>
                </div>

                {item.section_heading && (
                  <p className="text-[11px] text-slate-400">
                    Section: <span className="text-slate-200 font-medium">{item.section_heading}</span>
                  </p>
                )}

                <div
                  className="p-3 bg-navy-950 rounded-lg border border-navy-800 text-slate-300 leading-relaxed font-sans"
                  dangerouslySetInnerHTML={{ __html: item.excerpt }}
                />

                {onAskAboutClause && (
                  <div className="pt-1 flex justify-end">
                    <button
                      onClick={() => onAskAboutClause(item.section_heading || searchQuery)}
                      className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                    >
                      Ask about this clause in Policy Information &rarr;
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. ACTIVE DOCUMENT CATALOGUE */}
      <div className="bg-navy-850 border border-navy-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-navy-800">
          <div>
            <h2 className="text-base font-bold text-white">
              Indexed Documents Catalogue
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Source files extracted and verified in local SQLite database.
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-2.5 py-1 rounded-full">
            {filteredDocs.length} Active Documents
          </span>
        </div>

        {loading ? (
          <div className="space-y-3 animate-pulse">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-navy-900 rounded-xl border border-navy-800" />
            ))}
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="py-12 text-center text-slate-400">
            <BookOpen className="w-8 h-8 mx-auto text-slate-600 mb-2" />
            <p className="font-semibold text-white">No documents found matching this filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredDocs.map((doc) => (
              <div
                key={doc.id}
                className="bg-navy-900 border border-navy-800 hover:border-navy-700 rounded-xl p-5 text-xs flex flex-col justify-between space-y-3 shadow-md transition"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-bold text-white text-sm leading-snug">
                      {doc.title}
                    </h3>
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-blue-950 text-cyan-300 border border-blue-500/30 flex-shrink-0">
                      {doc.document_type.replace('_', ' ')}
                    </span>
                  </div>

                  <p className="text-[11px] font-mono text-slate-400">
                    {doc.version ? `Identifier: ${doc.version}` : 'Version: Standard'}
                  </p>
                </div>

                <div className="pt-3 border-t border-navy-800 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    Verified & Indexed
                  </span>
                  <span>{doc.chunk_count} search passages</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
