import axios from 'axios';

const BASE_URL = 'http://localhost:8000';
const api = axios.create({ baseURL: BASE_URL });

export const getDashboard = () => api.get('/api/dashboard').then(r => r.data);
export const getCashFlow = (days = 30) => api.get(`/api/cash-flow?days=${days}`).then(r => r.data);
export const getAnalysis = () => api.get('/api/analyze').then(r => r.data);
export const getRecommendations = () => api.get('/api/recommendations').then(r => r.data);
export const getEmailDrafts = () => api.get('/api/email-drafts').then(r => r.data);
export const getPayables = () => api.get('/api/payables').then(r => r.data);
export const getReceivables = () => api.get('/api/receivables').then(r => r.data);
export const getVendors = () => api.get('/api/vendors').then(r => r.data);
export const getInventory = () => api.get('/api/inventory').then(r => r.data);
export const getForecast = () => api.get('/api/forecast').then(r => r.data);
export const getLedger = () => api.get('/api/ledger').then(r => r.data);
export const getTransactions = () => api.get('/api/transactions').then(r => r.data);
export const getFinancialState = () => api.get('/api/financial-state').then(r => r.data);
export const getCalendar = () => api.get('/api/calendar').then(r => r.data);

// ── v2: Cost Intelligence Endpoints ──────────────────────────────────────────
export const getCostIntelligence = () => api.get('/api/cost-intelligence').then(r => r.data);
export const getImpactAnalysis = () => api.get('/api/impact/calculate').then(r => r.data);
export const getLeakageDetection = () => api.get('/api/leakage/detect').then(r => r.data);
export const getSignalAnalysis = () => api.get('/api/signals/analyze').then(r => r.data);
export const getExecutionState = () => api.get('/api/execution/run').then(r => r.data);
export const getExecutionLogs = () => api.get('/api/execution/logs').then(r => r.data);
export const getExecutionPending = () => api.get('/api/execution/pending').then(r => r.data);

export const approveAction = (actionId: string) =>
  api.post('/api/execution/approve', { action_id: actionId }).then(r => r.data);
export const executeAction = (actionId: string) =>
  api.post('/api/execution/execute', { action_id: actionId }).then(r => r.data);
export const rejectAction = (actionId: string, reason = '') =>
  api.post('/api/execution/reject', { action_id: actionId, reason }).then(r => r.data);
export const toggleAutoExecute = (enabled: boolean, threshold = 0.85) =>
  api.post('/api/execution/auto-toggle', { enabled, threshold }).then(r => r.data);

export const ingestBankCSV = (files: File[]) => {
  const form = new FormData();
  files.forEach(f => form.append('files', f));
  return api.post('/api/ingest/bank-statement', form).then(r => r.data);
};

export const ingestInvoices = (files: File[]) => {
  const form = new FormData();
  files.forEach(f => form.append('files', f));
  return api.post('/api/ingest/invoices', form).then(r => r.data);
};

export const ingestDocument = (files: File[]) => {
  const form = new FormData();
  files.forEach(f => form.append('files', f));
  return api.post('/api/ingest/document', form).then(r => r.data);
};
export default api;

