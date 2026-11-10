import { useState, useEffect, useCallback } from 'react';
import { getTransactions } from '../services/api.js';

/**
 * useTransactions — fetches transactions, optionally scoped to an account.
 *
 * @param {string|null} accountId - pass null/undefined to fetch all transactions
 * @param {Object}      options   - { limit, offset } query params
 *
 * Returns:
 *   transactions — array of transaction objects
 *   loading      — boolean
 *   error        — string | null
 *   refetch      — function
 */
export function useTransactions(accountId = null, options = {}) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { ...options };
      if (accountId) params.account_id = accountId;

      const data = await getTransactions(params);
      // Backend may return { transactions: [...] } or just the array
      setTransactions(Array.isArray(data) ? data : data.transactions ?? []);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Failed to load transactions.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [accountId, JSON.stringify(options)]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return { transactions, loading, error, refetch: fetchTransactions };
}

export default useTransactions;
