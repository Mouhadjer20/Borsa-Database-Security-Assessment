import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';

/**
 * ProtectedRoute — renders child routes only when authenticated.
 *
 * While the auth state is being resolved (initial /me fetch), shows a
 * full-screen loading spinner. Once resolved:
 *   - Authenticated  → renders <Outlet /> (child routes)
 *   - Not authenticated → redirects to /login
 */
export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" />
          <p className="text-gray-500 text-sm">Verifying session…</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
