import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import Header  from './Header.jsx';

/**
 * AppLayout — the shell that wraps all protected pages.
 * Layout: [Sidebar | flex-col(Header + <Outlet />)]
 */
export default function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">

      {/* Sidebar */}
      <Sidebar />

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
