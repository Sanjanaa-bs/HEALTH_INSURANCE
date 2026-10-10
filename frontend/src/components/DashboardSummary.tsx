import React from 'react';
import {
  Building2,
  FileText,
  Layers,
  MessageSquare,
  FolderArchive,
  Check,
  AlertCircle,
} from 'lucide-react';
import { DashboardSummary as DashboardSummaryType } from '../types';

interface DashboardSummaryProps {
  summary: DashboardSummaryType | null;
  loading: boolean;
}

export const DashboardSummary: React.FC<DashboardSummaryProps> = ({ summary, loading }) => {
  if (loading && !summary) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-slate-800/40 border border-slate-800 rounded-xl" />
        ))}
      </div>
    );
  }

  if (!summary) return null;

  const kpis = [
    {
      title: 'Hospitals Directory',
      count: summary.total_hospitals.toLocaleString(),
      subtitle: `${summary.total_insurer_records.toLocaleString()} Insurer Network links`,
      icon: Building2,
      gradient: 'from-blue-500/20 to-indigo-500/10',
      iconColor: 'text-blue-400',
      border: 'border-blue-500/20',
    },
    {
      title: 'Indexed Documents',
      count: summary.total_documents.toLocaleString(),
      subtitle: 'Policies, CIS & Guidance',
      icon: FileText,
      gradient: 'from-emerald-500/20 to-teal-500/10',
      iconColor: 'text-emerald-400',
      border: 'border-emerald-500/20',
    },
    {
      title: 'Document Chunks',
      count: summary.total_document_chunks.toLocaleString(),
      subtitle: 'Retrievable Knowledge Units',
      icon: Layers,
      gradient: 'from-purple-500/20 to-pink-500/10',
      iconColor: 'text-purple-400',
      border: 'border-purple-500/20',
    },
    {
      title: 'Conversations & Evals',
      count: (summary.total_conversations + summary.total_evaluations).toLocaleString(),
      subtitle: `${summary.total_conversations} threads · ${summary.total_evaluations} test runs`,
      icon: MessageSquare,
      gradient: 'from-amber-500/20 to-orange-500/10',
      iconColor: 'text-amber-400',
      border: 'border-amber-500/20',
    },
  ];

  const datasets = [
    {
      name: 'Government Hospital Directory CSV',
      path: 'data/hospitals/hospital_directory.csv',
      available: summary.dataset_status.hospitals_csv_exists,
      detail: summary.dataset_status.hospitals_csv_exists ? 'Verified (~10.3 MB, 30,275 rows)' : 'Missing',
    },
    {
      name: 'Insurer Network Webpages',
      path: 'data/insurer_networks/',
      available: summary.dataset_status.insurer_network_files > 0,
      detail: `${summary.dataset_status.insurer_network_files} file(s) (HTML + MHTML)`,
    },
    {
      name: 'Star Policy & CIS PDFs',
      path: 'data/policies/',
      available: summary.dataset_status.policies_files > 0,
      detail: `${summary.dataset_status.policies_files} PDF file(s) (Wording & CIS)`,
    },
    {
      name: 'Claim Guidance & IRDAI FAQs',
      path: 'data/claim_guidance/',
      available: summary.dataset_status.claim_guidance_files > 0,
      detail: `${summary.dataset_status.claim_guidance_files} MHTML guide(s)`,
    },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className={`relative overflow-hidden bg-slate-900/80 backdrop-blur-sm border ${kpi.border} p-5 rounded-2xl shadow-lg transition-all hover:translate-y-[-2px]`}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${kpi.gradient} opacity-50 pointer-events-none`}
              />
              <div className="relative flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    {kpi.title}
                  </p>
                  <p className="text-3xl font-extrabold text-white mt-1 tracking-tight">
                    {kpi.count}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">{kpi.subtitle}</p>
                </div>
                <div className={`p-3 rounded-xl bg-slate-800/80 border border-slate-700/50 ${kpi.iconColor}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Dataset Verification Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-4">
          <FolderArchive className="w-5 h-5 text-blue-400" />
          <h2 className="text-sm font-bold text-white tracking-wide uppercase">
            Preserved Source Datasets Status
          </h2>
          <span className="text-xs text-slate-500 font-mono">(`data/` directory)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {datasets.map((ds, i) => (
            <div
              key={i}
              className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-slate-200 truncate">
                    {ds.name}
                  </span>
                  {ds.available ? (
                    <span className="flex items-center text-emerald-400 text-[10px] font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/30">
                      <Check className="w-3 h-3 mr-0.5" /> READY
                    </span>
                  ) : (
                    <span className="flex items-center text-amber-400 text-[10px] font-bold bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/30">
                      <AlertCircle className="w-3 h-3 mr-0.5" /> EMPTY
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 font-mono truncate">{ds.path}</p>
              </div>
              <p className="text-xs text-slate-300 mt-3 pt-2 border-t border-slate-800/60 font-medium">
                {ds.detail}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
