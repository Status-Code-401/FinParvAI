import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';
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

export const ingestBankCSV = (file: File) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/api/ingest/bank-statement', form).then(r => r.data);
};

export const ingestInvoices = (file: File) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/api/ingest/invoices', form).then(r => r.data);
};

export default api;
