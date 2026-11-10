import { useState } from 'react';
import { searchUsers, lookupAccount, exportTransactions, dbPing } from '../services/api.js';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import ErrorMessage from '../components/common/ErrorMessage.jsx';

// ---------------------------------------------------------------------------
// Tool panel wrapper
// ---------------------------------------------------------------------------
function ToolPanel({ title, description, children }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-gray-100">{title}</h2>
        <p className="text-xs text-gray-500 mt-1">{description}</p>
      </div>
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Result display
// ---------------------------------------------------------------------------
function ResultBlock({ data, error, loading }) {
  if (loading) return <div className="mt-4"><LoadingSpinner size="sm" /></div>;
  if (error) return <div className="mt-4 text-xs text-red-400 font-mono">{error}</div>;
  if (!data) return null;
  return (
    <pre className="mt-4 p-3 rounded-lg bg-gray-950 border border-gray-800 text-xs text-green-300 font-mono overflow-x-auto whitespace-pre-wrap">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

// ---------------------------------------------------------------------------
// 1. User Search (SQLi — CWE-89)
// ---------------------------------------------------------------------------
function UserSearchTool() {
  const [q, setQ] = useState('');
  const [state, setState] = useState({ data: null, error: null, loading: false });

  const run = async (e) => {
    e.preventDefault();
    setState({ data: null, error: null, loading: true });
    try {
      const data = await searchUsers(q);
      setState({ data, error: null, loading: false });
    } catch (err) {
      setState({ data: null, error: err?.response?.data?.detail || err.message, loading: false });
    }
  };

  return (
    <ToolPanel
      title="User Directory Search"
      description="Search personnel records by username or name fragment."
    >
      <form onSubmit={run} className="flex gap-2">
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search users…"
          className="flex-1 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-amber-500 focus:outline-none"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-colors"
        >
          Search
        </button>
      </form>
      <ResultBlock {...state} />
    </ToolPanel>
  );
}

// ---------------------------------------------------------------------------
// 2. Account Lookup (BOLA — CWE-284)
// ---------------------------------------------------------------------------
function AccountLookupTool() {
  const [ref, setRef] = useState('');
  const [state, setState] = useState({ data: null, error: null, loading: false });

  const run = async (e) => {
    e.preventDefault();
    setState({ data: null, error: null, loading: true });
    try {
      const data = await lookupAccount(ref);
      setState({ data, error: null, loading: false });
    } catch (err) {
      setState({ data: null, error: err?.response?.data?.detail || err.message, loading: false });
    }
  };

  return (
    <ToolPanel
      title="Account Reference Lookup"
      description="Retrieve account details by internal reference number."
    >
      <form onSubmit={run} className="flex gap-2">
        <input
          type="text"
          value={ref}
          onChange={(e) => setRef(e.target.value)}
          placeholder="Account reference (e.g. 1, 2, 3)…"
          className="flex-1 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-amber-500 focus:outline-none"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-colors"
        >
          Lookup
        </button>
      </form>
      <ResultBlock {...state} />
    </ToolPanel>
  );
}

// ---------------------------------------------------------------------------
// 3. Transaction Export (CWE-250)
// ---------------------------------------------------------------------------
function TransactionExportTool() {
  const [limit, setLimit] = useState('10');
  const [state, setState] = useState({ data: null, error: null, loading: false });

  const run = async (e) => {
    e.preventDefault();
    setState({ data: null, error: null, loading: true });
    try {
      const data = await exportTransactions({ limit: parseInt(limit, 10) || 10 });
      setState({ data, error: null, loading: false });
    } catch (err) {
      setState({ data: null, error: err?.response?.data?.detail || err.message, loading: false });
    }
  };

  return (
    <ToolPanel
      title="Transaction Export"
      description="Export transaction records with session and audit metadata."
    >
      <form onSubmit={run} className="flex gap-2">
        <input
          type="number"
          value={limit}
          onChange={(e) => setLimit(e.target.value)}
          placeholder="Limit (default 10)"
          min="1"
          max="100"
          className="w-40 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-amber-500 focus:outline-none"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-colors"
        >
          Export
        </button>
      </form>
      <ResultBlock {...state} />
    </ToolPanel>
  );
}

// ---------------------------------------------------------------------------
// 4. DB Connectivity Check (SSRF / CWE-668)
// ---------------------------------------------------------------------------
function DbPingTool() {
  const [host, setHost] = useState('');
  const [port, setPort] = useState('5432');
  const [state, setState] = useState({ data: null, error: null, loading: false });

  const run = async (e) => {
    e.preventDefault();
    setState({ data: null, error: null, loading: true });
    try {
      const data = await dbPing(host, port);
      setState({ data, error: null, loading: false });
    } catch (err) {
      setState({ data: null, error: err?.response?.data?.detail || err.message, loading: false });
    }
  };

  return (
    <ToolPanel
      title="Database Connectivity Check"
      description="Test TCP reachability to a database endpoint from the application server."
    >
      <form onSubmit={run} className="flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          value={host}
          onChange={(e) => setHost(e.target.value)}
          placeholder="Host (e.g. 10.0.0.1 or db.internal)"
          className="flex-1 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-amber-500 focus:outline-none"
        />
        <input
          type="number"
          value={port}
          onChange={(e) => setPort(e.target.value)}
          placeholder="Port"
          className="w-28 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-amber-500 focus:outline-none"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-colors"
        >
          Ping
        </button>
      </form>
      <ResultBlock {...state} />
    </ToolPanel>
  );
}

// ---------------------------------------------------------------------------
// DiagnosticsPage
// ---------------------------------------------------------------------------
export default function DiagnosticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">System Diagnostics</h1>
        <p className="text-sm text-gray-400 mt-1">
          Internal tools for account management, data export, and infrastructure health checks.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <UserSearchTool />
        <AccountLookupTool />
        <TransactionExportTool />
        <DbPingTool />
      </div>
    </div>
  );
}

