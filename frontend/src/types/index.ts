export interface Provider {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface Encounter {
  id: number;
  patient_name?: string;
  patient_phone?: string;
  patient_age?: number;
  patient_gender?: string;
  chief_complaint?: string;
  symptoms?: string;
  duration?: string;
  medical_history?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'closed';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  source?: string;
  channel?: string;
  risk_code?: string;
  age_group?: string;
  assigned_provider_id?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EncounterCreate {
  patient_name: string;
  patient_phone: string;
  patient_age?: number;
  patient_gender?: string;
  chief_complaint: string;
  symptoms?: string;
  duration?: string;
  medical_history?: string;
  source?: string;
}

export interface Callback {
  id: number;
  encounter_id: number;
  msisdn_hash: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'queued' | 'in_progress' | 'done' | 'failed';
  provider_id?: number;
  outcome?: string;
  notes?: string;
  created_at: string;
  assigned_at?: string;
  completed_at?: string;
  updated_at: string;
}

export interface CallbackAssign {
  provider_id: number;
}

export interface CallbackComplete {
  outcome: string;
  notes?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
