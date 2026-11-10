import LoadingSpinner from '../common/LoadingSpinner.jsx';

/**
 * BalanceSummary — displays the aggregated total balance across all accounts.
 *
 * Props:
 *   accounts — array of account objects (each with .balance and .currency)
 *   loading  — boolean
 */

function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function BalanceSummary({ accounts = [], loading = false }) {
  // Aggregate by currency
  const totals = accounts.reduce((acc, account) => {
    const cur = account.currency ?? 'USD';
    acc[cur] = (acc[cur] ?? 0) + Number(account.balance ?? 0);
    return acc;
  }, {});

  const primaryCurrency = Object.keys(totals)[0] ?? 'USD';
  const primaryTotal    = totals[primaryCurrency] ?? 0;
  const isNegative      = primaryTotal < 0;

  return (
    <div className="card p-6">
      <div className="flex flex-col gap-1">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Total Portfolio Value
        </p>

        {loading ? (
          <div className="mt-2">
            <LoadingSpinner size="md" />
          </div>
        ) : (
          <>
            <p className={`text-4xl font-bold font-mono tabular-nums mt-1 ${isNegative ? 'text-red-400' : 'text-white'}`}>
              {formatCurrency(primaryTotal, primaryCurrency)}
            </p>

            {/* Per-currency breakdown if multiple currencies */}
            {Object.keys(totals).length > 1 && (
              <div className="flex flex-wrap gap-3 mt-3">
                {Object.entries(totals).map(([cur, total]) => (
                  <span key={cur} className="text-sm text-gray-400 font-mono">
                    {cur}: {formatCurrency(total, cur)}
                  </span>
                ))}
              </div>
            )}

            {/* Account count */}
            <p className="text-xs text-gray-500 mt-2">
              Across {accounts.length} account{accounts.length !== 1 ? 's' : ''}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
