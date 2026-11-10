import { useState, useEffect, useCallback } from 'react';
import { getLabStatus } from '../services/api.js';

/**
 * useLabStatus — fetches the current security lab status from the backend.
 *
 * Returns:
 *   labStatus  — status object | null
 *   loading    — boolean
 *   error      — string | null
 *   refetch    — function to refresh
 */
export function useLabStatus() {
  const [labStatus, setLabStatus] = useState(null);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const fetchLabStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getLabStatus();
      setLabStatus(data);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Failed to load lab status.';
      setError(message);
      setLabStatus(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLabStatus();
  }, [fetchLabStatus]);

  return { labStatus, loading, error, refetch: fetchLabStatus };
}

export default useLabStatus;
