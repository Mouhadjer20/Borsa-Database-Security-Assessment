export default function SecurityModeToggle({ mode = 'secure', labEnabled = false }) {
  const isLab = labEnabled || mode === 'lab' || mode === 'vulnerable';

  return (
    <div className="flex items-center gap-2">
      <div
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border ${
          isLab
            ? 'bg-amber-950/60 text-amber-400 border-amber-700/80 animate-pulse'
            : 'bg-green-950/60 text-green-400 border-green-700/80'
        }`}
      >
        <span
          className={`w-2 h-2 rounded-full ${
            isLab ? 'bg-amber-400' : 'bg-green-400'
          }`}
        />
        {isLab ? 'Lab Mode' : 'Secure Mode'}
      </div>
    </div>
  );
}

