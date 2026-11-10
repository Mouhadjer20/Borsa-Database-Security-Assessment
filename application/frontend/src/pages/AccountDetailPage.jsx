import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAccount } from '../services/api.js';
import { useTransactions } from '../hooks/useTransactions.js';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import ErrorMessage from '../components/common/ErrorMessage.jsx';
import Badge from '../components/common/Badge.jsx';
import TransactionTable from '../components/financial/TransactionTable.jsx';

export default function AccountDetailPage() {
  const { accountId } = useParams();
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    transactions,
    loading: txLoading,
    error: txError,
    refetch: refetchTx,
  } = useTransactions(accountId);

  const fetchDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAccount(accountId);
      setAccount({ ...data, id: data.account_id || data.id });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to retrieve account details.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (accountId) fetchDetail();
  }, [accountId]);

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner size="lg" label="Loading account details…" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Link to="/accounts" className="text-sm text-amber-400 hover:underline flex items-center gap-1">
          ← Back to accounts
        </Link>
        <ErrorMessage
          title="Account Unavailable"
          message={error}
          onRetry={fetchDetail}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Link to="/accounts" className="text-sm text-gray-400 hover:text-amber-400 transition-colors">
          ← All Accounts
        </Link>
        <span className="text-gray-600">/</span>
        <span className="text-sm font-mono text-gray-200">Account #{accountId}</span>
      </div>

      {/* Account detail overview card */}
      <div className="card p-6 border border-gray-700 bg-gray-900 rounded-xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold font-mono text-gray-100">
                Account #{account?.id}
              </h1>
              <Badge
                variant={account?.status === 'active' ? 'active' : 'inactive'}
                label={account?.status || 'active'}
                dot
              />
            </div>
            <p className="text-xs uppercase tracking-wider text-amber-500 mt-1 font-semibold">
              {account?.account_type || 'Checking'} Account
            </p>
          </div>

          <div className="text-right">
            <p className="text-xs text-gray-500 mb-1">Available Balance</p>
            <p className="text-3xl font-bold font-mono text-white">
              {new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: account?.currency || 'USD',
              }).format(account?.balance || 0)}
            </p>
            <p className="text-xs font-mono text-gray-400 mt-0.5">{account?.currency || 'USD'}</p>
          </div>
        </div>
      </div>

      {/* Scoped transactions */}
      <div>
        <TransactionTable
          title={`Transaction History for Account #${accountId}`}
          transactions={transactions}
          loading={txLoading}
          error={txError}
          onRetry={refetchTx}
          currentAccountId={accountId}
        />
      </div>
    </div>
  );
}

