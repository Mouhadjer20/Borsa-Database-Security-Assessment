import { useState } from 'react';
import LoadingSpinner from '../common/LoadingSpinner.jsx';
import ResultsPanel from './ResultsPanel.jsx';
import { runExperiment } from '../../services/api.js';

export default function ExperimentCard({
  id,
  title,
  cwe,
  objective,
  description,
  defaultPayload = '',
  supportsVariants = ['A', 'B'],
}) {
  const [selectedVariant, setSelectedVariant] = useState(supportsVariants[0] || 'A');
  const [payload, setPayload] = useState(defaultPayload);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runExperiment(id, {
        variant: selectedVariant,
        payload: payload || undefined,
      });
      setResult(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to execute security experiment.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/80 p-6 shadow-xl transition-all hover:border-gray-700">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <h3 className="text-lg font-bold text-gray-100 flex items-center gap-2">
          {title}
          {cwe && (
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-gray-800 text-amber-400 border border-amber-900/50">
              {cwe}
            </span>
          )}
        </h3>
        <span className="text-xs font-mono text-gray-400">ID: {id}</span>
      </div>

      <p className="text-xs font-semibold text-amber-500/90 mb-1 uppercase tracking-wider">Research Objective</p>
      <p className="text-sm text-gray-300 mb-4">{objective}</p>

      {description && (
        <p className="text-xs text-gray-400 mb-4 leading-relaxed">{description}</p>
      )}

      {/* Controls */}
      <div className="space-y-4 pt-3 border-t border-gray-800">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">
            Experiment Variant
          </label>
          <div className="flex gap-2">
            {supportsVariants.map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => setSelectedVariant(v)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  selectedVariant === v
                    ? v === 'A'
                      ? 'bg-red-950/60 text-red-300 border-red-700'
                      : 'bg-green-950/60 text-green-300 border-green-700'
                    : 'bg-gray-800/60 text-gray-400 border-gray-700 hover:bg-gray-800'
                }`}
              >
                {v === 'A' ? 'Variant A (Vulnerable)' : v === 'B' ? 'Variant B (Secure)' : `Variant ${v} (RLS)`}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">
            Test Payload / Parameter (Optional)
          </label>
          <input
            type="text"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
            placeholder="Payload or input string..."
            className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-xs font-mono text-gray-200 focus:border-amber-500 focus:outline-none"
          />
        </div>

        <button
          type="button"
          onClick={handleRun}
          disabled={loading}
          className="w-full sm:w-auto px-5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-xs uppercase tracking-wider transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-amber-500/10"
        >
          {loading ? (
            <>
              <LoadingSpinner size="sm" />
              <span>Running Experiment…</span>
            </>
          ) : (
            'Execute Experiment'
          )}
        </button>
      </div>

      {/* Errors */}
      {error && (
        <div className="mt-4 p-3 rounded-lg border border-red-800/50 bg-red-950/40 text-xs text-red-300">
          <strong>Execution Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {result && <ResultsPanel result={result} />}
    </div>
  );
}

