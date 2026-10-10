import React from 'react';

interface StatusBadgeProps {
  status: 'healthy' | 'degraded' | 'active' | 'inactive' | 'ready' | 'pending';
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  const displayLabel = label || status;

  const styles = {
    healthy: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    ready: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    active: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    degraded: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    pending: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
    inactive: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  }[status];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {displayLabel.toUpperCase()}
    </span>
  );
};
