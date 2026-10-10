import {
  HealthResponse,
  DashboardSummary,
  HospitalListResponse,
  InsurerHospitalListResponse,
  DocumentListResponse,
  SearchResponse,
  QuestionRequest,
  QuestionResponse,
} from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  if (!res.ok) throw new Error(`Failed to fetch dashboard summary: ${res.statusText}`);
  return res.json();
}

export async function fetchHospitals(params: {
  page?: number;
  pageSize?: number;
  search?: string;
  state?: string;
  district?: string;
  pincode?: string;
} = {}): Promise<HospitalListResponse> {
  const url = new URL(`${window.location.origin}${API_BASE}/hospitals`);
  if (params.page) url.searchParams.set('page', params.page.toString());
  if (params.pageSize) url.searchParams.set('page_size', params.pageSize.toString());
  if (params.search) url.searchParams.set('search', params.search);
  if (params.state) url.searchParams.set('state', params.state);
  if (params.district) url.searchParams.set('district', params.district);
  if (params.pincode) url.searchParams.set('pincode', params.pincode);

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch hospitals: ${res.statusText}`);
  return res.json();
}

export async function fetchInsurerHospitals(params: {
  page?: number;
  pageSize?: number;
  search?: string;
  city?: string;
} = {}): Promise<InsurerHospitalListResponse> {
  const url = new URL(`${window.location.origin}${API_BASE}/hospitals/insurer-network`);
  if (params.page) url.searchParams.set('page', params.page.toString());
  if (params.pageSize) url.searchParams.set('page_size', params.pageSize.toString());
  if (params.search) url.searchParams.set('search', params.search);
  if (params.city) url.searchParams.set('city', params.city);

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch insurer network hospitals: ${res.statusText}`);
  return res.json();
}

export async function fetchDocuments(params: {
  page?: number;
  pageSize?: number;
  documentType?: string;
} = {}): Promise<DocumentListResponse> {
  const url = new URL(`${window.location.origin}${API_BASE}/documents`);
  if (params.page) url.searchParams.set('page', params.page.toString());
  if (params.pageSize) url.searchParams.set('page_size', params.pageSize.toString());
  if (params.documentType) url.searchParams.set('document_type', params.documentType);

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  return res.json();
}

export async function searchDocuments(query: string, documentType?: string): Promise<SearchResponse> {
  const url = new URL(`${window.location.origin}${API_BASE}/documents/search`);
  url.searchParams.set('q', query);
  if (documentType) url.searchParams.set('document_type', documentType);

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
  return res.json();
}

export async function askQuestion(params: QuestionRequest): Promise<QuestionResponse> {
  const res = await fetch(`${API_BASE}/qa/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Question answering failed: ${res.statusText}`);
  }
  return res.json();
}
