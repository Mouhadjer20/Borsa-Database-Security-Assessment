import { useAuth } from '../context/AuthContext.jsx';
import { useAccounts } from '../hooks/useAccounts.js';
import { useTransactions } from '../hooks/useTransactions.js';
import BalanceSummary from '../components/financial/BalanceSummary.jsx';
import AccountCard from '../components/financial/AccountCard.jsx';
import TransactionTable from '../components/financial/TransactionTable.jsx';
import StatCard from '../components/common/StatCard.jsx';
import ErrorMessage from '../components/common/ErrorMessage.jsx';

export default function DashboardPage() {
  const { user } = useAuth();
  const { accounts, loading: accountsLoading, error: accountsError, refetch: refetchAccounts } = useAccounts();
  const { transactions, loading: txLoading, error: txError, refetch: refetchTx } = useTransactions(null, { limit: 5 });

  const normalizedAccounts = accounts.map((acc) => ({
    ...acc,
    id: acc.account_id || acc.id,
  }));

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">
            Welcome back, {user?.username || 'User'}
          </h1>
          <p className="text-xs text-gray-400 mt-1 font-mono">
            User ID: {user?.user_id} • Role: {user?.role || 'Customer'}
          </p>
        </div>
      </div>

      {/* Quick stats row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StatCard
          label="Active Accounts"
          value={accountsLoading ? '—' : normalizedAccounts.length}
          helperText="Financial accounts owned"
        />
        <StatCard
          label="Recent Activities"
          value={txLoading ? '—' : transactions.length}
          helperText="Latest logged transactions"
        />
      </div>

      {/* Balance Summary Card */}
      <BalanceSummary accounts={normalizedAccounts} loading={accountsLoading} />

      {/* Accounts list section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-200">Your Bank Accounts</h2>
        </div>

        {accountsError ? (
          <ErrorMessage
            title="Unable to load accounts"
            message={accountsError}
            onRetry={refetchAccounts}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {normalizedAccounts.map((account) => (
              <AccountCard key={account.id} account={account} />
            ))}
          </div>
        )}
      </div>

      {/* Recent Transactions Section */}
      <div className="mt-8">
        <TransactionTable
          title="Recent Transactions"
          transactions={transactions}
          loading={txLoading}
          error={txError}
          onRetry={refetchTx}
        />
      </div>
    </div>
  );
}

