import type { ConfidenceBreakdown } from '../api/types'

const BREAKDOWN_LABELS: Record<keyof ConfidenceBreakdown, string> = {
  data_completeness: 'Case data completeness',
  source_count_score: 'Number of sources found',
  court_authority_weight: 'Authority of courts cited',
  llm_relevance_avg: 'AI-assessed relevance',
}

function scoreColor(score: number): string {
  if (score >= 70) return 'bg-emerald-500'
  if (score >= 40) return 'bg-amber-500'
  return 'bg-rose-500'
}

export function ConfidenceGauge({
  score,
  breakdown,
}: {
  score: number
  breakdown: ConfidenceBreakdown
}) {
  return (
    <div className="font-ui rounded-lg border border-gray-200 p-4">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Research confidence</h3>
        <span className="text-2xl font-bold text-gray-900">{score.toFixed(0)}</span>
      </div>
      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className={`h-full rounded-full ${scoreColor(score)}`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-gray-500">
        Not a prediction of case outcome — reflects how strongly the available evidence
        supports these research findings.
      </p>
      <dl className="mt-4 space-y-2">
        {(Object.keys(breakdown) as (keyof ConfidenceBreakdown)[]).map((key) => (
          <div key={key} className="flex items-center gap-2 text-xs">
            <dt className="w-40 shrink-0 text-gray-500">{BREAKDOWN_LABELS[key]}</dt>
            <dd className="flex-1">
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full rounded-full bg-gray-400"
                  style={{ width: `${breakdown[key] * 100}%` }}
                />
              </div>
            </dd>
            <dd className="w-8 text-right text-gray-500">{Math.round(breakdown[key] * 100)}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
