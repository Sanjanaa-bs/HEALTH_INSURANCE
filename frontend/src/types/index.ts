export interface HealthResponse {
  status: string;
  environment: string;
  database_connected: boolean;
  version: string;
  timestamp: string;
}

export interface DatasetStatus {
  hospitals_csv_exists: boolean;
  insurer_network_files: number;
  policies_files: number;
  claim_guidance_files: number;
  evaluation_files: number;
}

export interface DashboardSummary {
  total_hospitals: number;
  total_insurer_records: number;
  total_documents: number;
  total_document_chunks: number;
  total_conversations: number;
  total_evaluations: number;
  dataset_status: DatasetStatus;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface Hospital {
  id: number;
  sr_no?: string;
  hospital_name: string;
  hospital_category?: string;
  care_type?: string;
  discipline?: string;
  address?: string;
  state?: string;
  district?: string;
  subdistrict?: string;
  pincode?: string;
  telephone?: string;
  mobile_number?: string;
  emergency_num?: string;
  ambulance_phone?: string;
  bloodbank_phone?: string;
  email?: string;
  website?: string;
  specialties?: string;
  facilities?: string;
  total_beds?: number;
  latitude?: number;
  longitude?: number;
  source_type: string;
  network_status?: string;
  created_at: string;
  updated_at: string;
}

export interface InsurerHospitalRecord {
  id: number;
  insurer_name: string;
  hospital_name: string;
  city?: string;
  state?: string;
  pincode?: string;
  address?: string;
  network_type?: string;
  total_beds?: number;
  source_type: string;
  matched_hospital_id?: number;
  created_at: string;
}

export interface HospitalListResponse {
  items: Hospital[];
  pagination: PaginationMeta;
}

export interface InsurerHospitalListResponse {
  items: InsurerHospitalRecord[];
  pagination: PaginationMeta;
}

export interface Document {
  id: number;
  title: string;
  document_type: string;
  source_path: string;
  file_format: string;
  file_size_bytes?: number;
  version?: string;
  is_processed: boolean;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: Document[];
  pagination: PaginationMeta;
}

export interface SearchResultItem {
  chunk_id: number;
  document_id: number;
  document_title: string;
  document_type: string;
  version?: string;
  page_number?: number;
  printed_page_number?: number;
  page_label?: string;
  section_heading?: string;
  excerpt: string;
  content_hash: string;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResultItem[];
}

export interface CitationItem {
  chunk_id: number;
  document_id: number;
  document_title: string;
  document_type: string;
  version?: string;
  page_number?: number;
  printed_page_number?: number;
  page_label?: string;
  section_heading?: string;
  supporting_text: string;
  content_hash: string;
}

export interface QuestionRequest {
  question: string;
  document_type?: string;
  conversation_id?: string;
  max_citations?: number;
}

export interface QuestionResponse {
  question: string;
  answer: string;
  status: string;
  is_sufficient_evidence: boolean;
  provider: string;
  generation_mode?: string; // "RAG + LLM", "Hybrid Retrieval", "Keyword Retrieval Fallback"
  retrieval_mode?: string; // "hybrid", "vector", "keyword"
  embedding_provider?: string;
  llm_provider?: string;
  citations: CitationItem[];
  disclaimer: string;
  conversation_id: string;
  created_at: string;
}
