import TransactionRow from './TransactionRow.jsx';
import LoadingSpinner from '../common/LoadingSpinner.jsx';
import EmptyState     from '../common/EmptyState.jsx';
import ErrorMessage   from '../common/ErrorMessage.jsx';

/**
 * TransactionTable — full table of transactions with loading/empty/error states.
 *
 * Props:
 *   transactions     — array of transaction objects
 *   loading          — boolean
 *   error            — string | null
 *   onRetry          — optional retry callback
 *   currentAccountId — optional, forwarded to TransactionRow for in/out perspective
 *   title            — optional table heading
 */
export default function TransactionTable({
  transactions = [],
  loading = false,
  error = null,
  onRetry,
  currentAccountId,
  title,
}) {
  return (
    <div className="card overflow-hidden">
      {/* Optional heading */}
      {title && (
        <div className="px-5 py-4 border-b border-gray-700">
          <h3 className="text-base font-semibold text-gray-100">{title}</h3>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="py-16 flex flex-col items-center gap-3">
          <LoadingSpinner size="md" label="Loading transactions…" />
          <p className="text-sm text-gray-500">Loading transactions…</p>
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className="p-5">
          <ErrorMessage title="Failed to load transactions" message={error} onRetry={onRetry} />
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && transactions.length === 0 && (
        <EmptyState
          title="No transactions"
          message="There are no transactions to display for this selection."
        />
      )}

      {/* Table */}
      {!loading && !error && transactions.length > 0 && (
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th className="text-right">Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <TransactionRow
                  key={tx.id ?? tx.transaction_id ?? Math.random()}
                  transaction={tx}
                  currentAccountId={currentAccountId}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
