import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { ConfidenceGauge } from '../components/ConfidenceGauge'
import { StepNav } from '../components/StepNav'
import { TierBadge } from '../components/TierBadge'
import type { ResearchReport } from '../api/types'

async function fetchResearch(caseId: string): Promise<ResearchReport> {
  const res = await fetch(`/api/cases/${caseId}/research`)
  if (!res.ok) throw new Error('Research not found — go back and run it first.')
  return res.json()
}

export function ResearchResults() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()

  const researchQuery = useQuery({
    queryKey: ['research', caseId],
    queryFn: () => fetchResearch(caseId!),
    enabled: !!caseId,
  })

  if (researchQuery.isLoading) {
    return <div className="font-ui mx-auto max-w-3xl px-6 py-10 text-sm text-gray-500">Loading…</div>
  }
  if (researchQuery.isError || !researchQuery.data) {
    return (
      <div className="font-ui mx-auto max-w-3xl px-6 py-10 text-sm text-rose-600">
        {(researchQuery.error as Error)?.message ?? 'Something went wrong.'}
      </div>
    )
  }

  const report = researchQuery.data

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <StepNav current="research" />
      <h1 className="font-ui text-2xl font-bold text-gray-900">Research results</h1>
      <p className="font-ui mt-1 text-sm text-gray-500">
        Precedents below come directly from connected court-data sources. Analysis comparing
        them to your case is AI-generated and must be verified before relying on it.
      </p>

      <div className="mt-6">
        <ConfidenceGauge score={report.confidence_score} breakdown={report.confidence_breakdown} />
      </div>

      <section className="mt-8">
        <div className="mb-2 flex items-center gap-2">
          <h2 className="font-ui text-sm font-semibold text-gray-700">Findings</h2>
          <TierBadge tier="AI_ANALYSIS" />
        </div>
        {report.findings.length === 0 ? (
          <p className="font-ui text-sm text-gray-500">No findings generated.</p>
        ) : (
          <ul className="space-y-2">
            {report.findings.map((f, idx) => (
              <li key={idx} className="font-ui rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                {f.summary}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <div className="mb-2 flex items-center gap-2">
          <h2 className="font-ui text-sm font-semibold text-gray-700">
            Precedents ({report.precedents.length})
          </h2>
          <TierBadge tier="VERIFIED_COURT" />
        </div>
        {report.precedents.length === 0 ? (
          <p className="font-ui text-sm text-gray-500">
            No precedents were returned by the connected sources for this case's search terms.
          </p>
        ) : (
          <ul className="space-y-3">
            {report.precedents.map((p, idx) => (
              <li key={idx} className="font-ui rounded-lg border border-gray-200 p-4">
                <div className="flex items-start justify-between gap-2">
                  <a
                    href={p.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-semibold text-sky-700 hover:underline"
                  >
                    {p.title}
                  </a>
                  <span className="shrink-0 text-xs text-gray-400">
                    relevance {Math.round(p.relevance_score * 100)}
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {p.court ?? 'Unknown court'} {p.date ? `· ${p.date}` : ''}
                </p>
                <p className="mt-2 text-sm text-gray-700">{p.snippet}</p>
                {p.applicability_note && (
                  <p className="mt-2 border-l-2 border-amber-300 pl-2 text-sm text-amber-900">
                    {p.applicability_note}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <button
        type="button"
        onClick={() => navigate(`/cases/${caseId}/select`)}
        className="font-ui mt-10 w-full rounded-lg bg-gray-900 py-2.5 text-sm font-semibold text-white"
      >
        Continue to draft a document
      </button>
    </div>
  )
}
