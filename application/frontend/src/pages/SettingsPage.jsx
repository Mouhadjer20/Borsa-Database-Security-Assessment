import { useAuth } from '../context/AuthContext.jsx';

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Application Settings & Configuration</h1>
        <p className="text-sm text-gray-400 mt-1">
          System metadata and current session parameters. All credentials are isolated.
        </p>
      </div>

      {/* User Session Info */}
      <div className="card p-6 bg-gray-900 border border-gray-800 rounded-xl space-y-4">
        <h3 className="text-base font-semibold text-gray-200 border-b border-gray-800 pb-3">
          Authenticated Session
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-500">Username</p>
            <p className="text-sm font-mono text-gray-200 mt-0.5">{user?.username || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">User ID</p>
            <p className="text-sm font-mono text-gray-200 mt-0.5">{user?.user_id ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Assigned Role</p>
            <p className="text-sm font-mono text-amber-400 mt-0.5 capitalize">{user?.role || 'customer'}</p>
          </div>
        </div>
      </div>

      {/* Environment Info */}
      <div className="card p-6 bg-gray-900 border border-gray-800 rounded-xl space-y-4">
        <h3 className="text-base font-semibold text-gray-200 border-b border-gray-800 pb-3">
          Security Environment
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500">Application Security Mode</p>
            <p className="text-sm font-semibold text-green-400 mt-0.5 uppercase">
              Secure
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Environment</p>
            <p className="text-sm font-semibold text-gray-200 mt-0.5">
              Internal Assessment Platform
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
