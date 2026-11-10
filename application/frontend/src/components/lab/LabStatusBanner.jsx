import LoadingSpinner from '../common/LoadingSpinner.jsx';

/**
 * LabStatusBanner — prominent banner showing current security lab status.
 *
 * Props:
 *   labStatus — object from /api/lab/status
 *   loading   — boolean
 *   error     — string | null
 */
export default function LabStatusBanner({ labStatus, loading, error }) {
  if (loading) {
    return (
      <div className="lab-banner p-5 flex items-center gap-3">
        <LoadingSpinner size="sm" />
        <span className="text-amber-400 text-sm">Loading lab status…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-800/50 bg-red-950/30 p-5">
        <p className="text-red-400 text-sm font-medium">⚠ Could not load lab status: {error}</p>
      </div>
    );
  }

  if (!labStatus) return null;

  const labEnabled   = labStatus.lab_enabled ?? (labStatus.mode === 'lab');
  const identity     = labStatus.active_identity ?? labStatus.db_user ?? labStatus.database_user ?? '—';
  const mode         = labStatus.mode ?? (labEnabled ? 'lab' : 'secure');
  const dbStatus     = labStatus.db_status ?? labStatus.database_status ?? 'unknown';

  return (
    <div className={`rounded-xl border p-5 ${
      labEnabled
        ? 'bg-amber-950/40 border-amber-700/60'
        : 'bg-green-950/30 border-green-800/50'
    }`}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          {/* Status indicator */}
          {labEnabled ? (
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center shrink-0">
              <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15" />
              </svg>
            </div>
          ) : (
            <div className="w-10 h-10 rounded-lg bg-green-900/40 border border-green-700/40 flex items-center justify-center shrink-0">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
            </div>
          )}

          <div>
            <h3 className={`text-base font-bold ${labEnabled ? 'text-amber-300' : 'text-green-400'}`}>
              {labEnabled ? '⚠ LAB MODE ACTIVE' : '✓ SECURE MODE'}
            </h3>
            <p className="text-sm text-gray-400 mt-0.5">
              {labEnabled
                ? 'Security controls are relaxed for educational experiments.'
                : 'All security controls are active and enforced.'}
            </p>
          </div>
        </div>

        {/* Mode badge */}
        <span className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${
          labEnabled
            ? 'bg-amber-950 text-amber-400 border-amber-700'
            : 'bg-green-950/50 text-green-400 border-green-700/50'
        }`}>
          {mode}
        </span>
      </div>

      {/* Status grid */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        <StatusItem label="Database Status" value={dbStatus} valueClass="text-gray-200" />
        <StatusItem
          label="Active DB Identity"
          value={identity}
          valueClass="font-mono text-amber-300"
        />
        <StatusItem
          label="Experiment Endpoints"
          value={labEnabled ? 'Enabled' : 'Disabled'}
          valueClass={labEnabled ? 'text-amber-400' : 'text-gray-500'}
        />
      </div>

      {/* Warning notice for lab mode */}
      {labEnabled && (
        <div className="mt-4 flex items-start gap-2 p-3 rounded-lg bg-amber-900/20 border border-amber-800/40">
          <svg className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
          <p className="text-xs text-amber-400">
            <strong>Educational Notice:</strong> This environment intentionally demonstrates
            security vulnerabilities. Data may be accessible beyond normal authorization boundaries.
            For research and learning purposes only.
          </p>
        </div>
      )}
    </div>
  );
}

function StatusItem({ label, value, valueClass = 'text-gray-200' }) {
  return (
    <div className="bg-gray-900/60 rounded-lg p-3 border border-gray-800">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-sm font-semibold ${valueClass}`}>{value}</p>
    </div>
  );
}
