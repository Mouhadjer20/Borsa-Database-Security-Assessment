import axios from 'axios';

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  withCredentials: true, // send cookies with every request (session-based auth)
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 15000,
});

// ---------------------------------------------------------------------------
// Request interceptor — attach any additional headers here if needed
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// ---------------------------------------------------------------------------
// Response interceptor — handle 401 globally
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Avoid redirect loop if already on login page
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

/** POST /api/auth/login */
export async function login(username, password) {
  const res = await apiClient.post('/api/auth/login', { username, password });
  return res.data;
}

/** POST /api/auth/logout */
export async function logout() {
  const res = await apiClient.post('/api/auth/logout');
  return res.data;
}

/** GET /api/auth/me — returns current authenticated user */
export async function getMe() {
  const res = await apiClient.get('/api/auth/me');
  return res.data;
}

// ---------------------------------------------------------------------------
// Accounts
// ---------------------------------------------------------------------------

/** GET /api/accounts — list accounts for the authenticated user */
export async function getAccounts() {
  const res = await apiClient.get('/api/accounts');
  return res.data;
}

/** GET /api/accounts/:id — single account details */
export async function getAccount(accountId) {
  const res = await apiClient.get(`/api/accounts/${accountId}`);
  return res.data;
}

// ---------------------------------------------------------------------------
// Transactions
// ---------------------------------------------------------------------------

/**
 * GET /api/transactions — fetch transactions.
 * @param {Object} params - optional query params: account_id, limit, offset
 */
export async function getTransactions(params = {}) {
  const res = await apiClient.get('/api/transactions', { params });
  return res.data;
}

// ---------------------------------------------------------------------------
// Security Lab
// ---------------------------------------------------------------------------

/** GET /api/lab/status — current lab/security mode status */
export async function getLabStatus() {
  const res = await apiClient.get('/api/lab/status');
  return res.data;
}

/**
 * POST /api/lab/experiments/:experimentId/run — execute an experiment.
 * @param {string} experimentId
 * @param {Object} payload - experiment-specific parameters
 */
export async function runExperiment(experimentId, payload = {}) {
  const res = await apiClient.post(`/api/lab/experiments/${experimentId}/run`, payload);
  return res.data;
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

/** GET /api/health — backend health check */
export async function getHealth() {
  const res = await apiClient.get('/api/health');
  return res.data;
}

export default apiClient;
