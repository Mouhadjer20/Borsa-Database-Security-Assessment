import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import ProtectedRoute from './routes/ProtectedRoute.jsx';
import AppLayout from './components/layout/AppLayout.jsx';

// Pages
import LoginPage        from './pages/LoginPage.jsx';
import DashboardPage    from './pages/DashboardPage.jsx';
import AccountsPage     from './pages/AccountsPage.jsx';
import AccountDetailPage from './pages/AccountDetailPage.jsx';
import TransactionsPage from './pages/TransactionsPage.jsx';
import DiagnosticsPage  from './pages/DiagnosticsPage.jsx';
import SettingsPage     from './pages/SettingsPage.jsx';
import NotFoundPage     from './pages/NotFoundPage.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Root redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Protected routes — wrapped in AppLayout (sidebar + header) */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard"              element={<DashboardPage />} />
              <Route path="/accounts"               element={<AccountsPage />} />
              <Route path="/accounts/:accountId"    element={<AccountDetailPage />} />
              <Route path="/transactions"           element={<TransactionsPage />} />
              <Route path="/diagnostics"            element={<DiagnosticsPage />} />
              <Route path="/settings"               element={<SettingsPage />} />
            </Route>
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
