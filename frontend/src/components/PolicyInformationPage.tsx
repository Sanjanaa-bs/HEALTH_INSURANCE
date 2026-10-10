import React, { useState } from 'react';
import { MessageSquare, Search } from 'lucide-react';
import { PolicyQA } from './PolicyQA';
import { PolicySearch } from './PolicySearch';

interface PolicyInformationPageProps {
  initialQuestion?: string;
  initialSearchQuery?: string;
}

export const PolicyInformationPage: React.FC<PolicyInformationPageProps> = ({
  initialQuestion = 'What is the waiting period for pre-existing diseases?',
  initialSearchQuery = 'cataract',
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'qa' | 'search'>('qa');
  const [qaQuestion, setQaQuestion] = useState(initialQuestion);
  const [searchQuery, setSearchQuery] = useState(initialSearchQuery);

  const handleRouteToSearch = (query: string) => {
    setSearchQuery(query);
    setActiveSubTab('search');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRouteToQA = (question: string) => {
    setQaQuestion(question);
    setActiveSubTab('qa');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Page Header */}
      <section className="bg-surface border border-border-light rounded-2xl shadow-card p-8 sm:p-10 space-y-4">
        <div className="max-w-3xl space-y-3">
          <span className="text-xs font-bold tracking-wider uppercase text-teal-muted bg-teal-light px-3 py-1 rounded-md border border-teal-border inline-block">
            Policy Terms & Wording
          </span>
          <h1 className="text-3xl font-extrabold text-navy-primary tracking-tight">
            Policy Information & Guidance
          </h1>
          <p className="text-sm text-ink-secondary leading-relaxed">
            Search official policy wording and verify coverage clauses directly from indexed documents: the 48-page Star Comprehensive Insurance Policy wording (POL / COMP / V.24 / 2025, UIN: SHAHLIP26044V092526), Customer Information Sheet (CIS), and IRDAI consumer guidelines.
          </p>
        </div>

        {/* Sub-Navigation Tabs */}
        <div className="flex items-center gap-2 pt-4 border-t border-border-light">
          <button
            onClick={() => setActiveSubTab('qa')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition ${
              activeSubTab === 'qa'
                ? 'bg-navy-primary text-white shadow-xs'
                : 'bg-page text-ink-secondary border border-border-light hover:bg-subtle hover:text-navy-primary'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Ask a Policy Question</span>
          </button>

          <button
            onClick={() => setActiveSubTab('search')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition ${
              activeSubTab === 'search'
                ? 'bg-navy-primary text-white shadow-xs'
                : 'bg-page text-ink-secondary border border-border-light hover:bg-subtle hover:text-navy-primary'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Search Policy Passages (BM25)</span>
          </button>
        </div>
      </section>

      {/* Main View Area */}
      {activeSubTab === 'qa' ? (
        <PolicyQA
          initialQuestion={qaQuestion}
          onNavigateToSearch={handleRouteToSearch}
        />
      ) : (
        <PolicySearch
          initialQuery={searchQuery}
          onAskQuestion={handleRouteToQA}
        />
      )}
    </div>
  );
};
