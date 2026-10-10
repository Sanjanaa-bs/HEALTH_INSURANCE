import React, { useState, useEffect } from 'react';
import {
  Search,
  BookOpen,
  Filter,
  RefreshCw,
  MessageSquare,
} from 'lucide-react';
import { SearchResultItem, Document } from '../types';
import { searchDocuments, fetchDocuments } from '../api/client';

interface PolicySearchProps {
  initialQuery?: string;
  onAskQuestion?: (query: string) => void;
}

export const PolicySearch: React.FC<PolicySearchProps> = ({
  initialQuery = 'cataract',
  onAskQuestion,
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [selectedType, setSelectedType] = useState<string>('');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const documentTypes = [
    { id: '', label: 'All Documents' },
    { id: 'policy', label: 'Full Policy Terms' },
    { id: 'cis', label: 'Customer Info Sheet (CIS)' },
    { id: 'claim_guidance', label: 'Claims Guidance' },
    { id: 'faq', label: 'IRDAI Regulations' },
  ];

  const handleSearch = async (searchQuery = query) => {
    const q = searchQuery.trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    try {
      const data = await searchDocuments(q, selectedType || undefined);
      setResults(data.results || []);
      setTotalResults(data.total_results ?? data.results?.length ?? 0);
    } catch (err: any) {
      setError(err.message || 'Failed to search policy documents. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const loadDocumentCatalog = async () => {
    try {
      const data = await fetchDocuments({ page: 1, pageSize: 20 });
      setDocuments(data.items || []);
    } catch (e) {
      // Non-blocking catalogue fetch
    }
  };

  useEffect(() => {
    loadDocumentCatalog();
    handleSearch(initialQuery);
  }, [selectedType]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  return (
    <div className="space-y-6">
      {/* Search Header Card */}
      <div className="bg-surface border border-border-light rounded-xl p-6 shadow-card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-light">
          <div>
            <h2 className="text-base font-bold text-navy-primary">
              Search Policy Documents & Clauses
            </h2>
            <p className="text-xs text-ink-secondary mt-0.5">
              Full-text BM25 search across 263 indexed passages with exact page citations.
            </p>
          </div>
          <span className="text-xs font-medium px-2.5 py-1 rounded bg-subtle text-ink-main border border-border-light self-start sm:self-auto">
            {totalResults} matching clause{totalResults === 1 ? '' : 's'}
          </span>
        </div>

        {/* Search Input Form */}
        <form onSubmit={handleFormSubmit} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-secondary" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search keywords (e.g. cataract, waiting period, room rent, cashless, exclusions)..."
                disabled={loading}
                className="w-full bg-page border border-border-light rounded-lg pl-10 pr-4 py-2.5 text-xs text-ink-main focus:bg-surface focus:outline-none focus:border-teal-muted transition"
                aria-label="Search policy keywords"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-5 py-2.5 rounded-lg bg-navy-primary text-white text-xs font-semibold hover:bg-navy-secondary transition disabled:opacity-50 flex items-center justify-center gap-1.5"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <span>Search Passages</span>
              )}
            </button>
          </div>

          {/* Type Filter Chips */}
          <div className="flex items-center gap-1.5 flex-wrap pt-1">
            <span className="text-[11px] text-ink-secondary font-medium mr-1 flex items-center gap-1">
              <Filter className="w-3 h-3 text-ink-secondary" />
              Source Filter:
            </span>
            {documentTypes.map((type) => (
              <button
                key={type.id}
                type="button"
                onClick={() => setSelectedType(type.id)}
                className={`text-[11px] font-medium px-2.5 py-1 rounded-md transition border ${
                  selectedType === type.id
                    ? 'bg-navy-primary text-white border-navy-primary'
                    : 'bg-page border-border-light text-ink-secondary hover:text-navy-primary hover:bg-subtle'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* ERROR STATE */}
      {error && (
        <div className="p-4 bg-danger-bg border border-danger-border text-danger-text rounded-xl text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => handleSearch()} className="underline font-semibold ml-4">
            Retry
          </button>
        </div>
      )}

      {/* LOADING SKELETON */}
      {loading && (
        <div className="space-y-3 animate-pulse">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-surface border border-border-light rounded-xl p-5 space-y-2">
              <div className="h-4 bg-subtle rounded w-1/3" />
              <div className="h-3 bg-subtle rounded w-full" />
              <div className="h-3 bg-subtle rounded w-4/5" />
            </div>
          ))}
        </div>
      )}

      {/* RESULTS LIST */}
      {!loading && !error && (
        <div className="space-y-3">
          {results.length === 0 ? (
            <div className="bg-surface border border-border-light rounded-xl p-10 text-center space-y-2 shadow-card">
              <Search className="w-8 h-8 mx-auto text-ink-secondary/40 mb-1" />
              <h3 className="text-sm font-bold text-navy-primary">No Matching Passages Found</h3>
              <p className="text-xs text-ink-secondary max-w-md mx-auto leading-relaxed">
                No indexed policy chunks matched &ldquo;{query}&rdquo;. Note that absence of search matches does not mean the clause is excluded from general insurance.
              </p>
              {onAskQuestion && (
                <button
                  onClick={() => onAskQuestion(query)}
                  className="inline-flex items-center gap-1.5 text-xs text-teal-muted hover:text-navy-primary font-semibold mt-2"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  Ask this question in Grounded Policy Q&A &rarr;
                </button>
              )}
            </div>
          ) : (
            results.map((item, idx) => (
              <div
                key={item.chunk_id || idx}
                className="bg-surface border border-border-light rounded-xl p-5 text-xs transition space-y-3 shadow-card hover:border-teal-border"
              >
                {/* Top Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-border-subtle">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-navy-primary text-xs sm:text-sm">
                      {item.document_title}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded uppercase bg-teal-light text-teal-muted border border-teal-border">
                      {item.document_type.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 font-mono text-[11px] text-ink-secondary">
                    {item.version && (
                      <span className="bg-page px-2 py-0.5 rounded border border-border-light">
                        {item.version}
                      </span>
                    )}
                    {item.page_label ? (
                      <span className="bg-subtle text-navy-primary font-medium px-2 py-0.5 rounded border border-border-light">
                        {item.page_label}
                      </span>
                    ) : item.page_number ? (
                      <span className="bg-subtle text-navy-primary px-2 py-0.5 rounded">
                        Page {item.page_number}
                      </span>
                    ) : null}
                  </div>
                </div>

                {/* Section Heading */}
                {item.section_heading && (
                  <div className="text-[11px] text-ink-secondary font-medium">
                    Section: <span className="text-navy-primary font-semibold">{item.section_heading}</span>
                  </div>
                )}

                {/* Highlighted Passage Snippet */}
                <div
                  className="p-3.5 bg-page rounded-lg border border-border-light text-ink-main text-xs leading-relaxed font-sans [&>b]:bg-teal-light [&>b]:text-teal-muted [&>b]:font-bold [&>b]:px-1 [&>b]:rounded"
                  dangerouslySetInnerHTML={{ __html: item.excerpt }}
                />

                {/* Action Link to Q&A */}
                {onAskQuestion && (
                  <div className="pt-1 flex justify-end">
                    <button
                      onClick={() => onAskQuestion(item.section_heading || query)}
                      className="text-[11px] font-semibold text-teal-muted hover:text-navy-primary flex items-center gap-1 transition"
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      Ask question about this clause &rarr;
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Indexed Document Catalogue Summary */}
      {documents.length > 0 && (
        <div className="bg-surface border border-border-light rounded-xl p-5 space-y-3 shadow-card">
          <h3 className="text-xs font-bold uppercase tracking-wider text-navy-primary flex items-center gap-2">
            <BookOpen className="w-3.5 h-3.5 text-teal-muted" />
            Active Source Documents in Knowledge Base ({documents.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="bg-page border border-border-light rounded-lg p-3 text-xs flex items-start justify-between gap-2"
              >
                <div>
                  <p className="font-semibold text-navy-primary leading-snug">{doc.title}</p>
                  <p className="text-[10px] text-ink-secondary mt-1">
                    {doc.version || 'Standard'} · {doc.chunk_count} passages indexed
                  </p>
                </div>
                <span className="text-[10px] font-medium uppercase px-2 py-0.5 rounded bg-surface border border-border-light text-ink-secondary flex-shrink-0">
                  {doc.document_type.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
