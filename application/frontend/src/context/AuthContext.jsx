import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient, { login as apiLogin, logout as apiLogout, getMe } from '../services/api.js';

// ---------------------------------------------------------------------------
// Context definition
// ---------------------------------------------------------------------------
const AuthContext = createContext(null);

/**
 * Custom hook — consume auth context anywhere in the tree.
 * Throws if used outside of <AuthProvider>.
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an <AuthProvider>');
  }
  return ctx;
}

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------
export function AuthProvider({ children }) {
  const [user, setUser]               = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading]     = useState(true); // start true: waiting for /me
  const [authError, setAuthError]     = useState(null);

  // ----- Bootstrap: check existing session on mount -----
  useEffect(() => {
    let cancelled = false;

    async function checkSession() {
      try {
        const me = await getMe();
        if (!cancelled) {
          setUser(me);
          setIsAuthenticated(true);
        }
      } catch (err) {
        // No active session — that's fine, just not authenticated
        if (!cancelled) {
          setUser(null);
          setIsAuthenticated(false);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    checkSession();
    return () => { cancelled = true; };
  }, []);

  // ----- login -----
  const login = useCallback(async (username, password) => {
    setAuthError(null);
    try {
      const data = await apiLogin(username, password);
      // After login the backend sets an auth cookie; fetch current user
      const me = await getMe();
      setUser(me);
      setIsAuthenticated(true);
      return { success: true };
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Login failed. Please check your credentials.';
      setAuthError(message);
      setIsAuthenticated(false);
      setUser(null);
      return { success: false, error: message };
    }
  }, []);

  // ----- logout -----
  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch (_) {
      // Ignore backend errors on logout — always clear local state
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  }, []);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    authError,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
