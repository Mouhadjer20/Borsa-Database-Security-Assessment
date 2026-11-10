import { useAccounts } from '../hooks/useAccounts.js';
import AccountCard from '../components/financial/AccountCard.jsx';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import ErrorMessage from '../components/common/ErrorMessage.jsx';
import EmptyState from '../components/common/EmptyState.jsx';

export default function AccountsPage() {
  const { accounts, loading, error, refetch } = useAccounts();

  const normalizedAccounts = accounts.map((acc) => ({
    ...acc,
    id: acc.account_id || acc.id,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">My Accounts</h1>
          <p className="text-sm text-gray-400 mt-1">
            Overview of all your deposit, savings, and investment accounts.
          </p>
        </div>
      </div>

      {loading && (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" label="Loading accounts…" />
        </div>
      )}

      {!loading && error && (
        <ErrorMessage
          title="Failed to load accounts"
          message={error}
          onRetry={refetch}
        />
      )}

      {!loading && !error && normalizedAccounts.length === 0 && (
        <EmptyState
          title="No accounts found"
          message="There are no active bank accounts associated with your customer profile."
        />
      )}

      {!loading && !error && normalizedAccounts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {normalizedAccounts.map((account) => (
            <AccountCard key={account.id} account={account} />
          ))}
        </div>
      )}
    </div>
  );
}

