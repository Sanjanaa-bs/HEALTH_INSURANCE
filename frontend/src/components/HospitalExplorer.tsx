import React, { useState, useEffect } from 'react';
import {
  Search,
  MapPin,
  Bed,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Building,
  RotateCcw,
  AlertCircle,
} from 'lucide-react';
import { Hospital, InsurerHospitalRecord, PaginationMeta } from '../types';
import { fetchHospitals, fetchInsurerHospitals } from '../api/client';

export const HospitalExplorer: React.FC = () => {
  const [sourceTab, setSourceTab] = useState<'govt' | 'insurer'>('govt');
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [insurerRecords, setInsurerRecords] = useState<InsurerHospitalRecord[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
  });
  const [search, setSearch] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      if (sourceTab === 'govt') {
        const data = await fetchHospitals({
          page,
          pageSize: 10,
          search: search.trim() || undefined,
          state: stateFilter.trim() || undefined,
        });
        setHospitals(data.items);
        setPagination(data.pagination);
      } else {
        const data = await fetchInsurerHospitals({
          page,
          pageSize: 10,
          search: search.trim() || undefined,
        });
        setInsurerRecords(data.items);
        setPagination(data.pagination);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load hospital records. Please check the backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(1);
  }, [sourceTab]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData(1);
  };

  const handleClearFilters = () => {
    setSearch('');
    setStateFilter('');
    setTimeout(() => {
      loadData(1);
    }, 0);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* 1. COMPACT INTRODUCTORY BANNER (Does not push search below the fold) */}
      <section className="bg-navy-850 border border-navy-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="grid grid-cols-1 md:grid-cols-12 items-center">
          <div className="p-6 sm:p-8 md:col-span-8 space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-3 py-1 rounded-full inline-block">
              Provider Directory & Network Search
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Find a Hospital
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              Search 29,974 registered government hospital facilities across Indian states or explore verified Star Health network hospitals eligible for cashless hospitalization pre-authorization.
            </p>
          </div>

          <div className="md:col-span-4 h-36 md:h-full relative overflow-hidden bg-navy-950">
            <img
              src="/images/hospital_reception.jpg"
              alt="Modern hospital reception and healthcare facility entrance"
              className="w-full h-full object-cover object-center"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-navy-850 via-transparent to-transparent hidden md:block" />
          </div>
        </div>
      </section>

      {/* 2. MAIN SEARCH & RESULTS CONTAINER */}
      <div className="bg-navy-850 border border-navy-800 rounded-2xl shadow-xl p-6 sm:p-8 space-y-6">
        {/* Source Selector Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-800">
          <div>
            <h2 className="text-base font-bold text-white">
              Select Provider Directory
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Switch between national public facilities and verified insurer cashless network records.
            </p>
          </div>

          <div className="inline-flex p-1 rounded-xl bg-navy-950 border border-navy-800 self-start sm:self-auto">
            <button
              onClick={() => {
                setSourceTab('govt');
                setSearch('');
                setStateFilter('');
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                sourceTab === 'govt'
                  ? 'bg-navy-800 text-white shadow-xs font-bold border border-navy-700'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Building className="w-3.5 h-3.5 text-cyan-400" />
              <span>National Directory (29,974)</span>
            </button>
            <button
              onClick={() => {
                setSourceTab('insurer');
                setSearch('');
                setStateFilter('');
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                sourceTab === 'insurer'
                  ? 'bg-navy-800 text-white shadow-xs font-bold border border-navy-700'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Star Health Network (Sample: 10 Records)</span>
            </button>
          </div>
        </div>

        {/* Safety & Honest Limitations Notice */}
        <div className="p-4 rounded-xl bg-navy-950/80 border border-navy-800 text-xs text-slate-300 space-y-1 leading-relaxed">
          <div className="flex items-center gap-2 text-cyan-300 font-semibold">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>Important Distinction on Network Affiliation & Cashless Approval</span>
          </div>
          <p>
            • <strong className="text-white">National Directory:</strong> Lists government-registered healthcare providers (29,974 facilities). Inclusion does <strong className="text-white">not</strong> establish Star Health network membership.
          </p>
          <p>
            • <strong className="text-white">Star Health Network:</strong> Displays verified insurer network records. A network listing does <strong className="text-white">not</strong> guarantee claim approval, which remains subject to policy terms and pre-authorization.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <form onSubmit={handleSearchSubmit} className="space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              <input
                type="text"
                placeholder={
                  sourceTab === 'govt'
                    ? 'Search hospital name or district (e.g. Apollo, General Hospital)...'
                    : 'Search network hospital name or city (e.g. Fortis, Manipal)...'
                }
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-white border border-slate-300 hover:border-slate-400 text-xs sm:text-sm text-[#0C162E] font-medium placeholder:text-[#64748B] caret-[#0C162E] rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition"
                aria-label="Search hospital by name"
              />
            </div>

            {sourceTab === 'govt' && (
              <div className="w-full sm:w-52">
                <input
                  type="text"
                  placeholder="State (e.g. Karnataka)"
                  value={stateFilter}
                  onChange={(e) => setStateFilter(e.target.value)}
                  className="w-full bg-white border border-slate-300 hover:border-slate-400 text-xs sm:text-sm text-[#0C162E] font-medium placeholder:text-[#64748B] caret-[#0C162E] rounded-xl px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-sm transition"
                  aria-label="Filter by state"
                />
              </div>
            )}

            <div className="flex items-center gap-2">
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition disabled:opacity-50 shadow-md shadow-blue-600/30"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
              {(search || stateFilter) && (
                <button
                  type="button"
                  onClick={handleClearFilters}
                  className="px-3.5 py-2.5 rounded-xl bg-navy-900 text-slate-300 border border-navy-800 text-xs font-medium hover:text-white hover:bg-navy-800 transition flex items-center gap-1.5"
                  title="Clear all filters"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset</span>
                </button>
              )}
            </div>
          </div>
        </form>

        {/* Error Notification */}
        {error && (
          <div className="p-4 bg-red-950/40 border border-red-500/30 text-red-200 rounded-xl text-xs flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => loadData(1)}
              className="text-xs font-bold underline hover:no-underline ml-4"
            >
              Retry
            </button>
          </div>
        )}

        {/* Results Table */}
        <div className="overflow-x-auto rounded-xl border border-navy-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-navy-950 text-[11px] font-bold text-slate-200 uppercase tracking-wider border-b border-navy-800">
              <tr>
                <th className="py-3.5 px-4">Hospital Name & Details</th>
                <th className="py-3.5 px-4">Classification & Status</th>
                <th className="py-3.5 px-4">Location</th>
                <th className="py-3.5 px-4">Pincode</th>
                <th className="py-3.5 px-4 text-right">Capacity / Coverage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-800/80 bg-navy-900/50">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={5} className="py-4 px-4 h-12 bg-navy-950/40" />
                  </tr>
                ))
              ) : sourceTab === 'govt' ? (
                hospitals.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-slate-400">
                      <Building className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                      <p className="font-semibold text-white">No matching government hospitals found.</p>
                      <p className="text-xs mt-0.5">Try searching with a broader name or resetting state filters.</p>
                    </td>
                  </tr>
                ) : (
                  hospitals.map((h) => (
                    <tr key={h.id} className="hover:bg-navy-800/60 transition">
                      <td className="py-3.5 px-4 font-semibold text-white">
                        {h.hospital_name}
                        {h.hospital_category && (
                          <span className="block text-[11px] text-slate-400 font-normal mt-0.5">
                            {h.hospital_category}
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-medium bg-navy-950 text-slate-300 border border-navy-800">
                          <Building className="w-3 h-3 text-cyan-400" />
                          Government Directory
                        </span>
                        {h.network_status ? (
                          <span className="ml-1.5 inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/40">
                            <ShieldCheck className="w-3 h-3" />
                            Star Cashless
                          </span>
                        ) : (
                          <span className="ml-1.5 inline-block text-[11px] text-slate-400 italic">
                            (Network status not verified)
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-300">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                          {h.district || h.state || 'N/A'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-slate-400">
                        {h.pincode || 'Not available'}
                      </td>
                      <td className="py-3.5 px-4 text-right text-slate-300">
                        {h.total_beds ? (
                          <span className="inline-flex items-center gap-1 text-slate-200 font-medium">
                            <Bed className="w-3.5 h-3.5 text-cyan-400" />
                            {h.total_beds} beds
                          </span>
                        ) : (
                          <span className="text-slate-400 font-mono text-[11px]">Not available</span>
                        )}
                      </td>
                    </tr>
                  ))
                )
              ) : insurerRecords.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">
                    <ShieldCheck className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    <p className="font-semibold text-white">No matching hospitals found in the currently available Star Health network records.</p>
                    <p className="text-xs text-slate-400 mt-1">Search is restricted to the ingested sample of 10 verified Star Health network records. Try clearing search terms or switching to the National Directory tab.</p>
                  </td>
                </tr>
              ) : (
                insurerRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-navy-800/60 transition">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {r.hospital_name}
                      {r.address && (
                        <span className="block text-[11px] text-slate-400 font-normal mt-0.5 truncate max-w-md">
                          {r.address}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/40">
                        <ShieldCheck className="w-3 h-3" />
                        Star Health Network
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                        {r.city || r.state || 'N/A'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {r.pincode || 'Not available'}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <span className="text-[11px] font-semibold text-cyan-300 bg-cyan-950 border border-cyan-500/30 px-2.5 py-0.5 rounded">
                        {r.network_type || 'Cashless Eligible'}
                      </span>
                      <span className="block text-[10px] text-slate-400 mt-0.5 font-normal">Capacity: Not available</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {pagination.total_pages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 pt-2 gap-3">
            <span>
              Showing page <strong className="text-white">{pagination.page}</strong> of{' '}
              <strong className="text-white">{pagination.total_pages}</strong> ({pagination.total_items.toLocaleString()} total facilities)
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => loadData(pagination.page - 1)}
                disabled={pagination.page <= 1 || loading}
                className="px-3 py-1.5 rounded-lg bg-navy-900 hover:bg-navy-800 disabled:opacity-40 transition border border-navy-700 text-slate-200 font-medium flex items-center gap-1"
                aria-label="Previous page"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
              <button
                onClick={() => loadData(pagination.page + 1)}
                disabled={pagination.page >= pagination.total_pages || loading}
                className="px-3 py-1.5 rounded-lg bg-navy-900 hover:bg-navy-800 disabled:opacity-40 transition border border-navy-700 text-slate-200 font-medium flex items-center gap-1"
                aria-label="Next page"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
