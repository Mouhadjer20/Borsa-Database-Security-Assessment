import Badge from '../common/Badge.jsx';

/**
 * TransactionRow — single row in a transaction table.
 *
 * Props: transaction object with fields:
 *   id              — transaction ID
 *   created_at      — ISO date string
 *   description     — narrative / memo
 *   from_account_id — source account
 *   to_account_id   — destination account
 *   amount          — numeric (positive = credit, negative = debit, or use direction)
 *   direction       — 'credit' | 'debit' (optional, derived from amount sign if absent)
 *   currency        — ISO currency code
 *   status          — 'completed' | 'pending' | 'failed'
 *   transaction_type — 'transfer' | 'deposit' | 'withdrawal' | ...
 *   currentAccountId — optional, to determine in/out from perspective of this account
 */

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(Math.abs(amount));
}

function formatDate(isoString) {
  if (!isoString) return '—';
  try {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(isoString));
  } catch {
    return isoString;
  }
}

function statusVariant(status) {
  switch (status?.toLowerCase()) {
    case 'completed': return 'active';
    case 'pending':   return 'pending';
    case 'failed':    return 'danger';
    default:          return 'info';
  }
}

export default function TransactionRow({ transaction, currentAccountId }) {
  if (!transaction) return null;

  // Support both backend field names:
  //   transaction_id / id
  //   timestamp / created_at
  //   source_account / from_account_id
  //   destination_account / to_account_id
  const {
    transaction_id,
    id = transaction_id,
    timestamp,
    created_at = timestamp,
    description,
    source_account,
    destination_account,
    from_account_id = source_account,
    to_account_id   = destination_account,
    amount = 0,
    direction,
    currency = 'USD',
    status = 'completed',
    transaction_type,
  } = transaction;

  // Determine credit/debit from perspective of currentAccountId (if provided)
  let isCredit;
  if (direction) {
    isCredit = direction === 'credit';
  } else if (currentAccountId) {
    isCredit = String(to_account_id) === String(currentAccountId);
  } else {
    isCredit = Number(amount) >= 0;
  }

  const displayAmount = formatCurrency(amount, currency);
  const amountClass = isCredit ? 'text-green-400' : 'text-red-400';
  const amountSign  = isCredit ? '+' : '−';

  // Counterparty / description label
  // The DB has no free-text description — build a readable label from account IDs.
  let counterparty = description;
  if (!counterparty) {
    const src  = from_account_id  ?? source_account  ?? null;
    const dest = to_account_id    ?? destination_account ?? null;
    if (currentAccountId) {
      counterparty = isCredit
        ? `From account #${src ?? '—'}`
        : `To account #${dest ?? '—'}`;
    } else {
      const typeLabel = transaction_type
        ? transaction_type.charAt(0).toUpperCase() + transaction_type.slice(1)
        : 'Transfer';
      counterparty = src && dest
        ? `${typeLabel} · #${src} → #${dest}`
        : src
          ? `From account #${src}`
          : dest
            ? `To account #${dest}`
            : typeLabel;
    }
  }

  return (
    <tr>
      {/* Date */}
      <td className="px-4 py-3 text-xs text-gray-500 whitespace-nowrap">
        {formatDate(created_at)}
      </td>

      {/* Description / counterparty */}
      <td className="px-4 py-3">
        <div className="text-sm text-gray-200 truncate max-w-xs">{counterparty}</div>
        {transaction_type && (
          <div className="text-xs text-gray-600 mt-0.5 capitalize">{transaction_type}</div>
        )}
      </td>

      {/* Amount */}
      <td className={`px-4 py-3 font-mono tabular-nums font-semibold text-sm whitespace-nowrap ${amountClass}`}>
        {amountSign} {displayAmount}
      </td>

      {/* Status */}
      <td className="px-4 py-3 text-right">
        <Badge variant={statusVariant(status)} label={status} />
      </td>
    </tr>
  );
}
