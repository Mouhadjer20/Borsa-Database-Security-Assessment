/**
 * StatCard — metric card for dashboards.
 *
 * Props:
 *   label     — descriptive label text
 *   value     — the main metric value (string or number)
 *   icon      — JSX icon element
 *   trend     — optional string like '+12%' or '-3%'
 *   trendUp   — boolean controlling trend colour (true=green, false=red)
 *   className — optional extra classes
 *   mono      — render value in monospace (default: false)
 */
export default function StatCard({
  label,
  value,
  icon,
  trend,
  trendUp,
  className = '',
  mono = false,
}) {
  return (
    <div className={`card p-5 flex flex-col gap-3 hover:border-gray-600 transition-colors ${className}`}>
      {/* Top row: label + icon */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          {label}
        </span>
        {icon && (
          <div className="w-9 h-9 rounded-lg bg-gray-700/60 flex items-center justify-center text-amber-400">
            {icon}
          </div>
        )}
      </div>

      {/* Value */}
      <div className="flex items-end gap-2">
        <span className={`text-2xl font-bold text-white ${mono ? 'font-mono tabular-nums' : ''}`}>
          {value ?? '—'}
        </span>

        {/* Trend badge */}
        {trend !== undefined && trend !== null && (
          <span
            className={`text-xs font-semibold mb-0.5 ${
              trendUp ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
    </div>
  );
}
