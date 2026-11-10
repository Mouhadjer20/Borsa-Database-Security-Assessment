import { useState, useEffect, useCallback } from 'react';
import { getAccounts } from '../services/api.js';

/**
 * useAccounts — fetches the list of accounts for the authenticated user.
 *
 * Returns:
 *   accounts  — array of account objects ([] while loading)
 *   loading   — boolean
 *   error     — error message string | null
 *   refetch   — function to manually refresh
 */
export function useAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAccounts();
      // Backend may return { accounts: [...] } or just the array
      setAccounts(Array.isArray(data) ? data : data.accounts ?? []);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Failed to load accounts.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  return { accounts, loading, error, refetch: fetchAccounts };
}

export default useAccounts;
