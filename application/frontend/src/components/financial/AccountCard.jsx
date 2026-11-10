import { Link } from 'react-router-dom';
import Badge from '../common/Badge.jsx';

/**
 * AccountCard — displays a single bank account summary.
 *
 * Props: account object with fields:
 *   id          — account identifier
 *   account_number — masked account number (optional)
 *   account_type   — 'checking' | 'savings' | 'investment' | ...
 *   balance        — numeric balance
 *   currency       — ISO currency code (e.g. 'USD')
 *   status         — 'active' | 'inactive' | 'pending'
 *   owner_name     — optional display name override
 */

// Map account types to display labels and icon colors
const TYPE_META = {
  checking:   { label: 'Checking',   color: 'text-blue-400',  bg: 'bg-blue-900/30' },
  savings:    { label: 'Savings',    color: 'text-green-400', bg: 'bg-green-900/30' },
  investment: { label: 'Investment', color: 'text-purple-400', bg: 'bg-purple-900/30' },
  loan:       { label: 'Loan',       color: 'text-red-400',   bg: 'bg-red-900/30' },
};

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

function maskAccountNumber(raw) {
  if (!raw) return '•••• •••• ••••';
  const str = String(raw);
  if (str.length <= 4) return `•••• ${str}`;
  return `•••• •••• ${str.slice(-4)}`;
}

export default function AccountCard({ account }) {
  if (!account) return null;

  const {
    id,
    account_number,
    account_type = 'checking',
    balance = 0,
    currency = 'USD',
    status = 'active',
  } = account;

  const meta = TYPE_META[account_type?.toLowerCase()] ?? {
    label: account_type ?? 'Account',
    color: 'text-amber-400',
    bg: 'bg-amber-900/30',
  };

  const isNegative = Number(balance) < 0;

  return (
    <Link
      to={`/accounts/${id}`}
      className="card p-5 flex flex-col gap-4 hover:border-gray-600 hover:shadow-card-lg transition-all duration-200 group"
    >
      {/* Top row: account type icon + status badge */}
      <div className="flex items-center justify-between">
        <div className={`flex items-center gap-2 px-2.5 py-1 rounded-lg ${meta.bg}`}>
          <svg className={`w-4 h-4 ${meta.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
          <span className={`text-xs font-semibold ${meta.color}`}>{meta.label}</span>
        </div>
        <Badge variant={status === 'active' ? 'active' : status === 'pending' ? 'pending' : 'inactive'} label={status} dot />
      </div>

      {/* Masked account number */}
      <div className="font-mono text-sm text-gray-400 tracking-widest">
        {maskAccountNumber(account_number || id)}
      </div>

      {/* Balance */}
      <div className="mt-auto">
        <p className="text-xs text-gray-500 mb-0.5">Available Balance</p>
        <p className={`text-2xl font-bold font-mono tabular-nums ${isNegative ? 'text-red-400' : 'text-white'}`}>
          {formatCurrency(balance, currency)}
        </p>
        <p className="text-xs text-gray-600 mt-0.5">{currency}</p>
      </div>

      {/* Footer: view arrow */}
      <div className="flex items-center justify-end text-gray-600 group-hover:text-amber-400 transition-colors">
        <span className="text-xs">View details</span>
        <svg className="w-4 h-4 ml-1 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  );
}
