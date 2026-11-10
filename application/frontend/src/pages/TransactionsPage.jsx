import { useTransactions } from '../hooks/useTransactions.js';
import TransactionTable from '../components/financial/TransactionTable.jsx';

export default function TransactionsPage() {
  const { transactions, loading, error, refetch } = useTransactions(null, { limit: 50 });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">All Transactions</h1>
          <p className="text-sm text-gray-400 mt-1">
            Audit history of transfers, deposits, and debits across all your accounts.
          </p>
        </div>
        <button
          onClick={refetch}
          className="px-4 py-2 text-xs font-semibold rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition-colors self-start sm:self-auto"
        >
          Refresh Feed
        </button>
      </div>

      <TransactionTable
        transactions={transactions}
        loading={loading}
        error={error}
        onRetry={refetch}
      />
    </div>
  );
}

