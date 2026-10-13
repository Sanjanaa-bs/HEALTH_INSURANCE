import React, { useState } from 'react';
import { BookOpen, MessageSquare } from 'lucide-react';
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

  const showSearch = (query: string) => {
    setSearchQuery(query);
    setActiveSubTab('search');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const showQuestion = (question: string) => {
    setQaQuestion(question);
    setActiveSubTab('qa');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-7 pb-12">
      <header className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-[11px] font-semibold tracking-wide">
          <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
          <span>POLICY DESK · STAR COMPREHENSIVE</span>
        </div>
        <h1 className="page-title text-4xl sm:text-[2.75rem] font-semibold text-white tracking-tight">
          Your policy, in plain language
        </h1>
        <p className="text-base text-slate-300 max-w-3xl leading-relaxed">
          Ask about your cover or search the wording. Every passage links back to its source and page.
        </p>
      </header>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div role="tablist" aria-label="Policy tools" className="inline-flex self-start p-1 rounded-xl bg-navy-900 border border-navy-800">
          <button
            type="button"
            role="tab"
            aria-selected={activeSubTab === 'qa'}
            onClick={() => setActiveSubTab('qa')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition ${
              activeSubTab === 'qa'
                ? 'bg-white text-[#1C3437] shadow-sm border border-[#DCE5DF]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Ask a question
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeSubTab === 'search'}
            onClick={() => setActiveSubTab('search')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition ${
              activeSubTab === 'search'
                ? 'bg-white text-[#1C3437] shadow-sm border border-[#DCE5DF]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Search policy wording
          </button>
        </div>
        <p className="text-xs text-slate-400 sm:text-right">
          Star Comprehensive · Policy wording and customer information sheet
        </p>
      </div>

      {activeSubTab === 'qa' ? (
        <PolicyQA
          initialQuestion={qaQuestion}
          onNavigateToSearch={showSearch}
          showPageHeading={false}
        />
      ) : (
        <PolicySearch initialQuery={searchQuery} onAskQuestion={showQuestion} />
      )}
    </div>
  );
};
