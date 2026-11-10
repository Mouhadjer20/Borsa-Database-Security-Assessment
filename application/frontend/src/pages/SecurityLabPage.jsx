import { Link } from 'react-router-dom';
import { useLabStatus } from '../hooks/useLabStatus.js';
import LabStatusBanner from '../components/lab/LabStatusBanner.jsx';

export default function SecurityLabPage() {
  const { labStatus, loading, error } = useLabStatus();

  const scenarios = [
    {
      id: 'sqli',
      title: '1. SQL Injection (SQLi)',
      cwe: 'CWE-89',
      summary: 'Test unsafe dynamic SQL string concatenation vs parameterized prepared statements.',
    },
    {
      id: 'privileges',
      title: '2. Excessive Database Privileges',
      cwe: 'CWE-250',
      summary: 'Evaluate least-privilege DB roles vs overprivileged application accounts.',
    },
    {
      id: 'bola',
      title: '3. Broken Authorization (BOLA/IDOR)',
      cwe: 'CWE-284',
      summary: 'Demonstrate missing ownership controls, application verification, and PostgreSQL Row-Level Security (RLS).',
    },
    {
      id: 'network',
      title: '4. Database Network Exposure',
      cwe: 'CWE-668',
      summary: 'Assess isolated internal subnet (DB-NET) restrictions vs direct exposure to external audit networks.',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Security Research Laboratory</h1>
          <p className="text-sm text-gray-400 mt-1">
            Controlled platform for assessing web application and PostgreSQL database security.
          </p>
        </div>
        <Link
          to="/experiments"
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-colors self-start sm:self-auto shadow-lg shadow-amber-500/10"
        >
          Open Experiment Console →
        </Link>
      </div>

      {/* Lab status banner */}
      <LabStatusBanner labStatus={labStatus} loading={loading} error={error} />

      {/* Research overview cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
        {scenarios.map((sc) => (
          <div key={sc.id} className="card p-6 border border-gray-800 bg-gray-900 rounded-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-gray-800 text-amber-400 border border-amber-900/50">
                  {sc.cwe}
                </span>
              </div>
              <h3 className="text-lg font-bold text-gray-100 mb-2">{sc.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{sc.summary}</p>
            </div>
            <div className="mt-5 pt-4 border-t border-gray-800 flex justify-end">
              <Link
                to="/experiments"
                className="text-xs font-semibold text-amber-400 hover:text-amber-300 flex items-center gap-1"
              >
                Test Scenario →
              </Link>
            </div>
          </div>
        ))}
      </div>

      {/* Architecture notes */}
      <div className="card p-6 bg-gray-900 border border-gray-800 rounded-xl">
        <h3 className="text-base font-bold text-gray-200 mb-2">Research Protocol & Isolation</h3>
        <p className="text-xs text-gray-400 leading-relaxed">
          All experiments execute exclusively within the 3-VM isolated virtual laboratory (Kali Linux VM1,
          Dual-homed App Server VM2, and Database Server VM3). Data tested is synthetic and fictional.
          Vulnerable implementations must never connect to production databases or services.
        </p>
      </div>
    </div>
  );
}

