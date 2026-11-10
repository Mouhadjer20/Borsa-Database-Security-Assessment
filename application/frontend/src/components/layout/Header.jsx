import { useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

// ---------------------------------------------------------------------------
// Map route paths to human-readable page titles
// ---------------------------------------------------------------------------
const PAGE_TITLES = {
  '/dashboard':    'Dashboard',
  '/accounts':     'My Accounts',
  '/transactions': 'Transactions',
  '/diagnostics':  'System Diagnostics',
  '/settings':     'Settings',
};

function getPageTitle(pathname) {
  if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname];
  // Handle /accounts/:id
  if (pathname.startsWith('/accounts/')) return 'Account Detail';
  return 'Borsa';
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------
export default function Header() {
  const location = useLocation();
  const { user } = useAuth();

  const title = getPageTitle(location.pathname);

  return (
    <header className="h-16 bg-gray-900 border-b border-gray-800 px-6 flex items-center justify-between shrink-0 sticky top-0 z-10">

      {/* Page title */}
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>

      {/* Right cluster */}
      <div className="flex items-center gap-4">
        {/* User badge */}
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
          <span className="font-medium text-gray-300">{user?.username ?? '—'}</span>
        </div>
      </div>
    </header>
  );
}
