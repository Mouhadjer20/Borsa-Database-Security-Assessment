/**
 * LoadingSpinner — dark-themed animated spinner.
 *
 * Props:
 *   size  — 'sm' | 'md' | 'lg' (default: 'md')
 *   label — optional accessible label (default: 'Loading…')
 */
export default function LoadingSpinner({ size = 'md', label = 'Loading…' }) {
  const sizeClasses = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-[3px]',
  };

  return (
    <div role="status" aria-label={label} className="flex items-center justify-center">
      <div
        className={`
          ${sizeClasses[size]}
          rounded-full
          border-gray-700
          border-t-amber-500
          animate-spin
        `}
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}
