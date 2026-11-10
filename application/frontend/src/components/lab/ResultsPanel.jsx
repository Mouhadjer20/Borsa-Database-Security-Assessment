/**
 * ResultsPanel — side-by-side display of vulnerable vs secure experiment results.
 *
 * Props:
 *   result — the full experiment result object from the backend.
 *            Expected shape (flexible):
 *            {
 *              vulnerable_result: any,
 *              secure_result:     any,
 *              explanation:       string,
 *              vulnerable_query:  string,
 *              secure_query:      string,
 *              ... any other fields
 *            }
 */

function prettify(value) {
  if (value === null || value === undefined) return 'null';
  if (typeof value === 'string') return value;
  return JSON.stringify(value, null, 2);
}

export default function ResultsPanel({ result }) {
  if (!result) return null;

  const hasVulnerable = 'vulnerable_result' in result;
  const hasSecure     = 'secure_result' in result;
  const hasSideBySide = hasVulnerable && hasSecure;

  return (
    <div className="mt-4 space-y-4 animate-slide-in">
      {/* Explanation */}
      {result.explanation && (
        <div className="p-4 rounded-lg bg-gray-900 border border-gray-700">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Explanation</p>
          <p className="text-sm text-gray-300 leading-relaxed">{result.explanation}</p>
        </div>
      )}

      {/* Query display */}
      {(result.vulnerable_query || result.secure_query) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {result.vulnerable_query && (
            <QueryBlock label="Vulnerable Query" query={result.vulnerable_query} variant="danger" />
          )}
          {result.secure_query && (
            <QueryBlock label="Secure Query" query={result.secure_query} variant="success" />
          )}
        </div>
      )}

      {/* Results side-by-side */}
      {hasSideBySide ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <ResultBlock
            label="Vulnerable Result"
            value={result.vulnerable_result}
            variant="danger"
          />
          <ResultBlock
            label="Secure Result"
            value={result.secure_result}
            variant="success"
          />
        </div>
      ) : (
        /* Single result */
        <ResultBlock label="Result" value={result.result ?? result.data ?? result} variant="neutral" />
      )}

      {/* Additional metadata */}
      {result.rows_affected !== undefined && (
        <p className="text-xs text-gray-500">
          Rows affected: <span className="font-mono text-gray-300">{result.rows_affected}</span>
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ResultBlock({ label, value, variant }) {
  const headerClass = {
    danger:  'text-red-400 border-red-900/50',
    success: 'text-green-400 border-green-900/50',
    neutral: 'text-gray-300 border-gray-700',
  }[variant] ?? 'text-gray-300 border-gray-700';

  const codeClass = {
    danger:  'text-red-300',
    success: 'text-green-400',
    neutral: 'text-gray-300',
  }[variant] ?? 'text-gray-300';

  return (
    <div className={`rounded-lg border bg-gray-900 overflow-hidden ${headerClass}`}>
      <div className={`px-4 py-2 border-b text-xs font-semibold uppercase tracking-wider ${headerClass}`}>
        {label}
      </div>
      <pre className={`px-4 py-3 text-xs font-mono overflow-x-auto max-h-64 whitespace-pre-wrap break-words ${codeClass}`}>
        {prettify(value)}
      </pre>
    </div>
  );
}

function QueryBlock({ label, query, variant }) {
  const headerClass = {
    danger:  'text-red-400 border-red-900/50',
    success: 'text-green-400 border-green-900/50',
  }[variant] ?? 'text-gray-400 border-gray-700';

  return (
    <div className={`rounded-lg border bg-gray-900 overflow-hidden ${headerClass}`}>
      <div className={`px-4 py-2 border-b text-xs font-semibold uppercase tracking-wider ${headerClass}`}>
        {label}
      </div>
      <pre className="px-4 py-3 text-xs font-mono text-gray-300 overflow-x-auto whitespace-pre-wrap break-all">
        {query}
      </pre>
    </div>
  );
}
