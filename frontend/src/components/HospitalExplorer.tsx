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
  HelpCircle,
  Info,
} from 'lucide-react';
import { Hospital, InsurerHospitalRecord, PaginationMeta } from '../types';
import { fetchHospitals, fetchInsurerHospitals } from '../api/client';

export const HospitalExplorer: React.FC = () => {
  const [sourceTab, setSourceTab] = useState<'govt' | 'insurer'>('govt');
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [insurerRecords, setInsurerRecords] = useState<InsurerHospitalRecord[]>([]);
  const [insurerTotalCount, setInsurerTotalCount] = useState<number | null>(null);
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
  });
  const [search, setSearch] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [appliedSearch, setAppliedSearch] = useState('');
  const [appliedLocation, setAppliedLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch actual count of imported insurer records on mount
  useEffect(() => {
    fetchInsurerHospitals({ page: 1, pageSize: 1, source: 'insurer' })
      .then((data) => {
        if (data && data.pagination) {
          setInsurerTotalCount(data.pagination.total_items);
        }
      })
      .catch((err) => {
        console.warn('Could not load insurer record count:', err);
      });
  }, []);

  const loadData = async (
    page = 1,
    currentTab: 'govt' | 'insurer' = sourceTab,
    searchTerm = appliedSearch,
    locTerm = appliedLocation
  ) => {
    setLoading(true);
    setError(null);
    try {
      if (currentTab === 'govt') {
        const data = await fetchHospitals({
          page,
          pageSize: 10,
          search: searchTerm.trim() || undefined,
          location: locTerm.trim() || undefined,
          source: 'govt',
          nationwide: !locTerm.trim() ? true : false,
        });
        setHospitals(data.items);
        setPagination(data.pagination);
      } else {
        const data = await fetchInsurerHospitals({
          page,
          pageSize: 10,
          search: searchTerm.trim() || undefined,
          location: locTerm.trim() || undefined,
          source: 'insurer',
        });
        setInsurerRecords(data.items);
        setPagination(data.pagination);
        if (!searchTerm.trim() && !locTerm.trim()) {
          setInsurerTotalCount(data.pagination.total_items);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load hospital records. Please check the backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(1, sourceTab, appliedSearch, appliedLocation);
  }, [sourceTab]);

  const handleTabChange = (tab: 'govt' | 'insurer') => {
    setSourceTab(tab);
    setSearch('');
    setLocationFilter('');
    setAppliedSearch('');
    setAppliedLocation('');
    loadData(1, tab, '', '');
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanSearch = search.trim();
    const cleanLoc = locationFilter.trim();
    setAppliedSearch(cleanSearch);
    setAppliedLocation(cleanLoc);
    loadData(1, sourceTab, cleanSearch, cleanLoc);
  };

  const handleQuickScope = (loc: string) => {
    setLocationFilter(loc);
    setAppliedLocation(loc);
    loadData(1, sourceTab, appliedSearch, loc);
  };

  const handleClearFilters = () => {
    setSearch('');
    setLocationFilter('');
    setAppliedSearch('');
    setAppliedLocation('');
    loadData(1, sourceTab, '', '');
  };

  const handlePageChange = (newPage: number) => {
    loadData(newPage, sourceTab, appliedSearch, appliedLocation);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* 1. COMPACT INTRODUCTORY BANNER */}
      <section className="editorial-card overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-12 items-center">
          <div className="p-6 sm:p-8 md:col-span-8 space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-3 py-1 rounded-full inline-block">
              HOSPITAL DIRECTORY & NETWORK VERIFICATION
            </span>
            <h1 className="page-title text-3xl sm:text-4xl font-semibold text-white tracking-tight">
              Hospital Search & Network Verification
            </h1>
            <p className="text-base text-slate-300 max-w-2xl leading-relaxed">
              Search nationwide healthcare facilities or verify hospital coverage against the verified Star Health network dataset.
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
      <div className="editorial-card p-5 sm:p-7 space-y-6">
        {/* Source Selector Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-navy-800">
          <div>
            <h2 className="text-base font-bold text-white">
              Select Dataset Source
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Choose between the national facility directory and the insurer-specific network dataset.
            </p>
          </div>

          <div role="tablist" aria-label="Hospital data source" className="inline-flex p-1 rounded-xl bg-navy-950 border border-navy-800 self-start sm:self-auto">
            <button
              role="tab"
              aria-selected={sourceTab === 'govt'}
              onClick={() => handleTabChange('govt')}
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
              role="tab"
              aria-selected={sourceTab === 'insurer'}
              onClick={() => handleTabChange('insurer')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                sourceTab === 'insurer'
                  ? 'bg-navy-800 text-white shadow-xs font-bold border border-navy-700'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>
                Star Health Network Sample{insurerTotalCount !== null ? ` (${insurerTotalCount})` : ''}
              </span>
            </button>
          </div>
        </div>

        {/* Transparent Dataset Scope & Semantics Notice */}
        <div className="p-4 sm:p-5 rounded-xl bg-navy-950/80 border border-navy-800 text-sm text-slate-300 space-y-2 leading-relaxed">
          <div className="flex items-center gap-2 text-cyan-300 font-semibold text-xs uppercase tracking-wider">
            <Info className="w-4 h-4 flex-shrink-0" />
            <span>Dataset Scope & Network Verification Semantics</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-xs text-slate-300">
            <div className="bg-navy-900/60 p-3 rounded-lg border border-navy-800 space-y-1">
              <span className="font-semibold text-white flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-cyan-400" />
                Government Facility Directory (29,974 records)
              </span>
              <p className="text-slate-400">
                Nationwide registry of healthcare providers. A directory listing describes facility existence and does <strong>not</strong> imply Star Health network participation, cashless authorization, or claim approval.
              </p>
            </div>
            <div className="bg-navy-900/60 p-3 rounded-lg border border-navy-800 space-y-1">
              <span className="font-semibold text-white flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Star Health Network Sample (10 Bengaluru records)
              </span>
              <p className="text-slate-400">
                Offline sample covering Bengaluru, Karnataka only. Absence from this sample does <strong>not</strong> prove a hospital is out of network. Facilities outside Bengaluru are classified as <em>Unverified</em>.
              </p>
            </div>
          </div>
        </div>

        {/* Search & Location Filter Controls */}
        <form onSubmit={handleSearchSubmit} className="space-y-3">
          <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              <input
                type="text"
                placeholder={
                  sourceTab === 'govt'
                    ? 'Search hospital name (e.g. Apollo, Baptist, Fortis, Manipal)...'
                    : 'Search network hospital name (e.g. Apollo, Baptist, Cambridge)...'
                }
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-white border border-slate-300 hover:border-slate-400 text-sm text-[#1C3437] font-medium placeholder:text-[#718383] caret-[#1C3437] rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-brand-cyan shadow-sm transition"
                aria-label="Search hospital by name"
              />
            </div>

            <div className="w-full sm:w-64 relative">
              <MapPin className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Location / City / State (e.g. Bengaluru)"
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                className="w-full bg-white border border-slate-300 hover:border-slate-400 text-sm text-[#1C3437] font-medium placeholder:text-[#718383] caret-[#1C3437] rounded-xl pl-9 pr-3.5 py-3 focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-brand-cyan shadow-sm transition"
                aria-label="Filter by location"
              />
            </div>

            <div className="flex items-center gap-2">
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition disabled:opacity-50 shadow-md shadow-blue-600/30"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
              {(search || locationFilter || appliedSearch || appliedLocation) && (
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

          {/* Quick Scope Filter Buttons */}
          <div className="flex items-center gap-2 text-xs text-slate-400 pt-1">
            <span className="text-[11px] font-medium text-slate-500">Quick scope:</span>
            <button
              type="button"
              onClick={() => handleQuickScope('Bengaluru')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition border ${
                appliedLocation.toLowerCase().includes('bengaluru') || locationFilter.toLowerCase().includes('bengaluru')
                  ? 'bg-cyan-950 text-cyan-300 border-cyan-500/40'
                  : 'bg-navy-950 text-slate-300 border-navy-800 hover:text-white hover:border-navy-700'
              }`}
            >
              Bengaluru (Sample Scope)
            </button>
            <button
              type="button"
              onClick={() => handleQuickScope('')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition border ${
                !appliedLocation && !locationFilter
                  ? 'bg-cyan-950 text-cyan-300 border-cyan-500/40'
                  : 'bg-navy-950 text-slate-300 border-navy-800 hover:text-white hover:border-navy-700'
              }`}
            >
              All India (Nationwide)
            </button>
            {appliedLocation && (
              <span className="text-cyan-400 text-[11px] ml-auto">
                Filtered by location: <strong className="text-white">{appliedLocation}</strong>
              </span>
            )}
          </div>
        </form>

        {/* Error Notification */}
        {error && (
          <div className="p-4 bg-red-950/40 border border-red-500/30 text-red-200 rounded-xl text-xs flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => loadData(pagination.page, sourceTab, appliedSearch, appliedLocation)}
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
                <th className="py-3.5 px-4">Hospital Name & Category</th>
                <th className="py-3.5 px-4">Data Source</th>
                <th className="py-3.5 px-4">Insurer Network Status</th>
                <th className="py-3.5 px-4">Location</th>
                <th className="py-3.5 px-4">Pincode</th>
                <th className="py-3.5 px-4 text-right">Capacity / Coverage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-800/80 bg-navy-900/50">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={6} className="py-4 px-4 h-12 bg-navy-950/40" />
                  </tr>
                ))
              ) : sourceTab === 'govt' ? (
                hospitals.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-400">
                      <Building className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                      <p className="font-semibold text-white">No matching government hospitals found.</p>
                      <p className="text-xs mt-0.5">Try searching with a broader name or resetting location filters.</p>
                    </td>
                  </tr>
                ) : (
                  hospitals.map((h) => {
                    const isListed =
                      h.network_status_code === 'LISTED' ||
                      h.network_status === 'Listed in Star Health network data';
                    const isNotFound =
                      h.network_status_code === 'NOT_FOUND' ||
                      h.network_status === 'Not found in available network data' ||
                      h.network_status === 'Not found in the imported network data';

                    return (
                      <tr key={h.id} className="hover:bg-navy-800/60 transition">
                        {/* 1. Hospital Name & Category */}
                        <td className="py-3.5 px-4 font-semibold text-white max-w-xs">
                          <div>{h.hospital_name}</div>
                          {h.hospital_category && (
                            <span className="block text-[11px] text-slate-400 font-normal mt-0.5">
                              {h.hospital_category}
                            </span>
                          )}
                        </td>

                        {/* 2. Data Source (Separate Column) */}
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-medium bg-navy-950 text-slate-200 border border-navy-700">
                            <Building className="w-3.5 h-3.5 text-cyan-400" />
                            Government Directory
                          </span>
                        </td>

                        {/* 3. Insurer Network Status (Separate Column with Transparent Explanation) */}
                        <td className="py-3.5 px-4 max-w-sm">
                          {isListed ? (
                            <div className="space-y-0.5">
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950 text-emerald-300 border border-emerald-500/40">
                                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                                Listed in Star Health network data
                              </span>
                              <p className="text-[10px] text-slate-400 leading-tight">
                                {h.network_status_explanation ||
                                  'Matched in offline Star Health sample. Subject to policy terms and pre-authorization.'}
                              </p>
                            </div>
                          ) : isNotFound ? (
                            <div className="space-y-0.5">
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950/60 text-amber-300 border border-amber-500/30">
                                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                                Not found in available network data
                              </span>
                              <p className="text-[10px] text-slate-400 leading-tight">
                                {h.network_status_explanation ||
                                  'No matching record found in available Star Health sample (offline Bengaluru sample). Does not prove hospital is out of network.'}
                              </p>
                            </div>
                          ) : (
                            <div className="space-y-0.5">
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-slate-900 text-slate-300 border border-slate-700">
                                <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                                Network status unverified
                              </span>
                              <p className="text-[10px] text-slate-400 leading-tight">
                                {h.network_status_explanation ||
                                  "The available Star Health dataset contains only a limited Bengaluru sample. This hospital's network status cannot be confirmed using the available data. Please verify with Star Health before planning cashless treatment."}
                              </p>
                            </div>
                          )}
                        </td>

                        {/* 4. Location */}
                        <td className="py-3.5 px-4 text-slate-300 whitespace-nowrap">
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                            {h.district ? `${h.district}, ${h.state || ''}` : h.state || 'N/A'}
                          </span>
                        </td>

                        {/* 5. Pincode */}
                        <td className="py-3.5 px-4 font-mono text-slate-400 whitespace-nowrap">
                          {h.pincode || 'Not reported'}
                        </td>

                        {/* 6. Capacity / Coverage */}
                        <td className="py-3.5 px-4 text-right text-slate-300 whitespace-nowrap">
                          {h.total_beds ? (
                            <span className="inline-flex items-center gap-1 text-slate-200 font-medium">
                              <Bed className="w-3.5 h-3.5 text-cyan-400" />
                              {h.total_beds} beds
                            </span>
                          ) : (
                            <span className="text-slate-400 font-mono text-[11px]">Not reported</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )
              ) : insurerRecords.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <ShieldCheck className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    <p className="font-semibold text-white">No match in the imported Star Health network data.</p>
                    <p className="text-xs text-slate-400 mt-1 max-w-xl mx-auto">
                      The offline dataset contains 10 Bengaluru records only. Absence from this sample does not prove a hospital is out of network.
                    </p>
                  </td>
                </tr>
              ) : (
                insurerRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-navy-800/60 transition">
                    {/* 1. Hospital Name & Address */}
                    <td className="py-3.5 px-4 font-semibold text-white max-w-xs">
                      <div>{r.hospital_name}</div>
                      {r.address && (
                        <span className="block text-[11px] text-slate-400 font-normal mt-0.5 truncate max-w-md">
                          {r.address}
                        </span>
                      )}
                    </td>

                    {/* 2. Data Source */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-medium bg-navy-950 text-emerald-300 border border-emerald-500/30">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        Star Health Sample
                      </span>
                    </td>

                    {/* 3. Network Status */}
                    <td className="py-3.5 px-4 max-w-sm">
                      <div className="space-y-0.5">
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/40">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                          Listed in Star Health network data
                        </span>
                        <p className="text-[10px] text-slate-400 leading-tight">
                          Imported from offline Star Health Bengaluru network sample. Cashless access is subject to policy terms and pre-authorization.
                        </p>
                      </div>
                    </td>

                    {/* 4. Location */}
                    <td className="py-3.5 px-4 text-slate-300 whitespace-nowrap">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                        {r.city ? `${r.city}, ${r.state || ''}` : r.state || 'N/A'}
                      </span>
                    </td>

                    {/* 5. Pincode */}
                    <td className="py-3.5 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {r.pincode || 'Not reported'}
                    </td>

                    {/* 6. Coverage Type */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <span className="text-[11px] font-semibold text-cyan-300 bg-cyan-950 border border-cyan-500/30 px-2.5 py-0.5 rounded">
                        {r.network_type || 'Cashless Network'}
                      </span>
                      <span className="block text-[10px] text-slate-400 mt-0.5 font-normal">
                        {r.total_beds ? `${r.total_beds} beds in directory` : 'Bed count not reported'}
                      </span>
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
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page <= 1 || loading}
                className="px-3 py-1.5 rounded-lg bg-navy-900 hover:bg-navy-800 disabled:opacity-40 transition border border-navy-700 text-slate-200 font-medium flex items-center gap-1"
                aria-label="Previous page"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
              <button
                onClick={() => handlePageChange(pagination.page + 1)}
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
