import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center mb-6 shadow-xl shadow-amber-500/5">
        <span className="text-2xl font-black font-mono">404</span>
      </div>
      <h1 className="text-3xl font-extrabold text-gray-100 tracking-tight">
        Page Not Found
      </h1>
      <p className="mt-3 text-sm text-gray-400 max-w-md">
        The requested financial resource or laboratory endpoint does not exist.
      </p>
      <div className="mt-8">
        <Link
          to="/dashboard"
          className="px-6 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-colors shadow-lg shadow-amber-500/10"
        >
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}

