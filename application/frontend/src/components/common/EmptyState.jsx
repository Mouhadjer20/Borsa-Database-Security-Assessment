/**
 * EmptyState — shown when a list or table has no data.
 *
 * Props:
 *   icon    — optional JSX icon element
 *   title   — heading text
 *   message — supporting description
 *   action  — optional JSX element (e.g. a CTA button)
 */
export default function EmptyState({ icon, title = 'No data', message, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center animate-fade-in">
      {icon ? (
        <div className="text-gray-600 mb-4">{icon}</div>
      ) : (
        <svg
          className="w-12 h-12 text-gray-700 mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0H4"
          />
        </svg>
      )}
      <h3 className="text-base font-semibold text-gray-400">{title}</h3>
      {message && (
        <p className="text-sm text-gray-600 mt-1 max-w-xs">{message}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
