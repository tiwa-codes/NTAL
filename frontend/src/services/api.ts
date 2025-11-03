import axios from 'axios';
import type { Encounter, EncounterCreate, LoginRequest, TokenResponse, Provider } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', credentials);
    return response.data;
  },

  getCurrentProvider: async (): Promise<Provider> => {
    const response = await api.get<Provider>('/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

export const triageService = {
  create: async (data: EncounterCreate): Promise<Encounter> => {
    const response = await api.post<Encounter>('/triage', data);
    return response.data;
  },
};

export const encounterService = {
  getAll: async (): Promise<Encounter[]> => {
    const response = await api.get<Encounter[]>('/encounters');
    return response.data;
  },

  getById: async (id: number): Promise<Encounter> => {
    const response = await api.get<Encounter>(`/encounters/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<Encounter>): Promise<Encounter> => {
    const response = await api.put<Encounter>(`/encounters/${id}`, data);
    return response.data;
  },
};

export const healthService = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};
