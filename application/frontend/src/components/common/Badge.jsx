/**
 * Badge — coloured status pill.
 *
 * Props:
 *   variant — 'active' | 'inactive' | 'pending' | 'success' | 'danger' | 'warning' | 'info' | 'lab'
 *   label   — text to display (falls back to variant name if omitted)
 *   dot     — show a small status dot (default: false)
 */

const VARIANTS = {
  active:   'bg-green-900/50  text-green-400  border-green-700/50',
  success:  'bg-green-900/50  text-green-400  border-green-700/50',
  inactive: 'bg-gray-800     text-gray-400   border-gray-700',
  pending:  'bg-amber-900/40 text-amber-400  border-amber-700/50',
  warning:  'bg-amber-900/40 text-amber-400  border-amber-700/50',
  danger:   'bg-red-900/40   text-red-400    border-red-700/50',
  info:     'bg-blue-900/40  text-blue-400   border-blue-700/50',
  lab:      'bg-amber-950    text-amber-300  border-amber-600',
};

const DOT_COLORS = {
  active:   'bg-green-400',
  success:  'bg-green-400',
  inactive: 'bg-gray-500',
  pending:  'bg-amber-400',
  warning:  'bg-amber-400',
  danger:   'bg-red-400',
  info:     'bg-blue-400',
  lab:      'bg-amber-400',
};

export default function Badge({ variant = 'info', label, dot = false }) {
  const styles = VARIANTS[variant] ?? VARIANTS.info;
  const dotColor = DOT_COLORS[variant] ?? 'bg-gray-400';
  const text = label ?? variant;

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-0.5
        text-xs font-semibold uppercase tracking-wide
        rounded-full border
        ${styles}
      `}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColor}`} />
      )}
      {text}
    </span>
  );
}
