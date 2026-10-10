import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Cpu,
  X,
} from 'lucide-react';
import { HealthResponse, DashboardSummary as DashboardSummaryType } from './types';
import { fetchHealth, fetchDashboardSummary } from './api/client';
import { Header, MainNavTab } from './components/Header';
import { HomePage } from './components/HomePage';
import { HospitalExplorer } from './components/HospitalExplorer';
import { PolicyQA } from './components/PolicyQA';
import { ClaimsGuidance } from './components/ClaimsGuidance';
import { DocumentLibrary } from './components/DocumentLibrary';

export const App: React.FC = () => {
  // Initial landing page is Home!
  const [activeTab, setActiveTab] = useState<MainNavTab>('home');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [summary, setSummary] = useState<DashboardSummaryType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdminDiagnostics, setShowAdminDiagnostics] = useState(false);

  // Cross-component routing state
  const [selectedQaQuestion, setSelectedQaQuestion] = useState<string>(
    'What is the waiting period for pre-existing diseases?'
  );

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthData, summaryData] = await Promise.all([
        fetchHealth(),
        fetchDashboardSummary(),
      ]);
      setHealth(healthData);
      setSummary(summaryData);
    } catch (err: any) {
      setError(
        'Unable to connect to the FastAPI backend at http://127.0.0.1:8000. Ensure the backend server is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleRouteToQA = (q: string) => {
    setSelectedQaQuestion(q);
    setActiveTab('policy');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleAskFromHome = (q: string) => {
    setSelectedQaQuestion(q);
    setActiveTab('policy');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-navy-900 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* 1. SINGLE, CLEAN PRIMARY NAVIGATION BAR */}
      <Header
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        health={health}
        loading={loading}
        onRefresh={loadInitialData}
      />

      {/* 2. MAIN CONTENT AREA */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Backend Connectivity Alert (if connection fails) */}
        {error && (
          <div className="mb-8 bg-amber-950/40 border border-amber-500/40 rounded-xl p-4 flex items-start justify-between gap-3 text-amber-200">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0 text-amber-400 mt-0.5" />
              <div className="text-xs space-y-1">
                <p className="font-bold text-amber-100">Backend Server Notice</p>
                <p className="text-amber-200/90">{error}</p>
                <p className="font-mono text-[11px] bg-navy-950 px-2.5 py-1.5 rounded-lg border border-amber-500/20 inline-block text-amber-300">
                  Run command: uvicorn backend.app.main:app --reload --port 8000
                </p>
              </div>
            </div>
            <button
              onClick={loadInitialData}
              className="bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 text-xs font-semibold px-3 py-1.5 rounded-lg transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* VIEW 1: HOME LANDING PAGE */}
        {activeTab === 'home' && (
          <HomePage
            onNavigate={setActiveTab}
            onAskQuestion={handleAskFromHome}
          />
        )}

        {/* VIEW 2: FIND HOSPITALS */}
        {activeTab === 'hospitals' && <HospitalExplorer />}

        {/* VIEW 3: POLICY INFORMATION */}
        {activeTab === 'policy' && (
          <PolicyQA
            initialQuestion={selectedQaQuestion}
            onNavigateToSearch={() => setActiveTab('documents')}
          />
        )}

        {/* VIEW 4: CLAIMS HELP */}
        {activeTab === 'claims' && (
          <ClaimsGuidance onAskClaimsQuestion={handleRouteToQA} />
        )}

        {/* VIEW 5: DOCUMENT LIBRARY */}
        {activeTab === 'documents' && (
          <DocumentLibrary onAskAboutClause={handleRouteToQA} />
        )}
      </main>

      {/* 3. OPTIONAL DEVELOPER / ADMIN DIAGNOSTICS MODAL */}
      {showAdminDiagnostics && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-navy-850 border border-navy-700 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-navy-800">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-white">System Diagnostics & Data Readiness</h3>
              </div>
              <button
                onClick={() => setShowAdminDiagnostics(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-navy-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Metrics */}
            {summary && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-navy-900 p-3 rounded-xl border border-navy-800">
                  <span className="text-slate-400 block text-[11px]">Hospitals Directory</span>
                  <span className="text-base font-bold text-white mt-1 block">
                    {summary.total_hospitals.toLocaleString()}
                  </span>
                </div>
                <div className="bg-navy-900 p-3 rounded-xl border border-navy-800">
                  <span className="text-slate-400 block text-[11px]">Network Records</span>
                  <span className="text-base font-bold text-cyan-300 mt-1 block">
                    {summary.total_insurer_records.toLocaleString()}
                  </span>
                </div>
                <div className="bg-navy-900 p-3 rounded-xl border border-navy-800">
                  <span className="text-slate-400 block text-[11px]">Indexed Documents</span>
                  <span className="text-base font-bold text-white mt-1 block">
                    {summary.total_documents.toLocaleString()}
                  </span>
                </div>
                <div className="bg-navy-900 p-3 rounded-xl border border-navy-800">
                  <span className="text-slate-400 block text-[11px]">Search Chunks</span>
                  <span className="text-base font-bold text-white mt-1 block">
                    {summary.total_document_chunks.toLocaleString()}
                  </span>
                </div>
              </div>
            )}

            {/* Tech Stack Specs */}
            <div className="bg-navy-900 p-4 rounded-xl border border-navy-800 text-xs space-y-2">
              <h4 className="font-bold text-white uppercase text-[11px] tracking-wider text-cyan-400">
                Verified System Foundation
              </h4>
              <ul className="text-slate-300 space-y-1.5 list-disc list-inside">
                <li>FastAPI 0.110+ backend with SQLAlchemy 2.0 ORM engine</li>
                <li>SQLite 3.38+ with FTS5 BM25 full-text indexing (porter unicode61)</li>
                <li>Star Comprehensive Policy (UIN: SHAHLIP26044V092526, POL / COMP / V.24 / 2025)</li>
                <li>27/27 automated backend tests passing</li>
              </ul>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowAdminDiagnostics(false)}
                className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-700 text-white text-xs font-semibold transition"
              >
                Close Diagnostics
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. FOOTER */}
      <footer className="border-t border-navy-800/80 bg-navy-950 py-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <p className="font-semibold text-slate-300">
              Star Health Comprehensive Insurance Information Platform
            </p>
            <p className="text-[11px] text-slate-500">
              Grounding Source: POL / COMP / V.24 / 2025 (UIN: SHAHLIP26044V092526) · CIS (Version: V.2 / 2025)
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <button
              onClick={() => setActiveTab('hospitals')}
              className="hover:text-white transition"
            >
              Hospitals
            </button>
            <button
              onClick={() => setActiveTab('policy')}
              className="hover:text-white transition"
            >
              Policy Terms
            </button>
            <button
              onClick={() => setActiveTab('claims')}
              className="hover:text-white transition"
            >
              Claims
            </button>
            <span className="text-navy-800">•</span>
            <button
              onClick={() => setShowAdminDiagnostics(true)}
              className="text-cyan-400/80 hover:text-cyan-300 transition"
              title="View platform statistics & specs"
            >
              System Specs
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
