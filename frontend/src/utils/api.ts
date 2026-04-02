import axios from 'axios';
import { FinancialState, DecisionOutput, Prediction, ActionPlan } from '../types';

const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const BASE = import.meta.env.VITE_API_URL || (isLocal ? 'http://localhost:8000' : 'https://finparvai.onrender.com');
const api = axios.create({ baseURL: BASE.replace(/\/$/, '') });

export const getDemoState = (): Promise<FinancialState> =>
  api.get('/api/ingest/demo-state').then(r => r.data);

export const uploadDocument = (file: File) => {
  const fd = new FormData();
  fd.append('file', file);
  return api.post('/api/ingest/upload', fd).then(r => r.data);
};

export const normalizeState = (state: FinancialState) =>
  api.post('/api/ingest/normalize', state).then(r => r.data);

export const runDecision = (state: FinancialState): Promise<DecisionOutput> =>
  api.post('/api/decision/run', state).then(r => r.data);

export const simulateCashFlow = (state: FinancialState, days = 14) =>
  api.post(`/api/decision/simulate?days=${days}`, state).then(r => r.data);

export const getForecast = (state: FinancialState, horizon = 30): Promise<Prediction> =>
  api.post(`/api/predict/forecast?horizon_days=${horizon}`, state).then(r => r.data);

export const generateActions = (state: FinancialState): Promise<{ decision_summary: any; action_plan: ActionPlan }> =>
  api.post('/api/actions/generate', state).then(r => r.data);
