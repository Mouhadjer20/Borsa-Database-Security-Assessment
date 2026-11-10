/**
 * ErrorMessage — dark-themed error display card.
 *
 * Props:
 *   title   — optional heading (default: 'Error')
 *   message — error message string
 *   onRetry — optional retry callback (shows a Retry button when provided)
 */
export default function ErrorMessage({ title = 'Error', message, onRetry }) {
  if (!message) return null;

  return (
    <div
      role="alert"
      className="rounded-xl border border-red-800/60 bg-red-950/30 p-4 animate-fade-in"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="shrink-0 mt-0.5">
          <svg
            className="w-5 h-5 text-red-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-red-400">{title}</p>
          <p className="text-sm text-red-300 mt-0.5 break-words">{message}</p>
        </div>

        {/* Retry button */}
        {onRetry && (
          <button
            onClick={onRetry}
            className="shrink-0 text-xs text-red-400 hover:text-red-300 font-medium underline underline-offset-2 transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
