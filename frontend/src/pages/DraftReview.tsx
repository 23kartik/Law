import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { draftExportUrl } from '../api/client'
import { StepNav } from '../components/StepNav'
import { TierBadge, TierLegend } from '../components/TierBadge'
import { FlaggedIssuesList } from '../components/IssuesList'
import type { DraftOutput } from '../api/types'

async function fetchDraft(caseId: string): Promise<DraftOutput> {
  const res = await fetch(`/api/cases/${caseId}/draft`)
  if (!res.ok) throw new Error('Draft not found — go back and generate it first.')
  return res.json()
}

export function DraftReview() {
  const { caseId } = useParams<{ caseId: string }>()

  const draftQuery = useQuery({
    queryKey: ['draft', caseId],
    queryFn: () => fetchDraft(caseId!),
    enabled: !!caseId,
  })

  if (draftQuery.isLoading) {
    return <div className="font-ui mx-auto max-w-5xl px-6 py-10 text-sm text-gray-500">Loading…</div>
  }
  if (draftQuery.isError || !draftQuery.data) {
    return (
      <div className="font-ui mx-auto max-w-5xl px-6 py-10 text-sm text-rose-600">
        {(draftQuery.error as Error)?.message ?? 'Something went wrong.'}
      </div>
    )
  }

  const draft = draftQuery.data

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <StepNav current="draft" />
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-ui text-2xl font-bold text-gray-900">Draft document</h1>
          <p className="font-ui mt-1 text-sm text-gray-500">
            Review every highlighted claim before filing. This is a drafting aid, not a
            substitute for lawyer review.
          </p>
        </div>
        <a
          href={draftExportUrl(caseId!)}
          className="font-ui shrink-0 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white"
        >
          Download .docx
        </a>
      </div>

      <div className="mt-4">
        <TierLegend />
      </div>

      <div className="mt-8 grid grid-cols-[1fr_320px] gap-8">
        <article className="rounded-lg border border-gray-200 bg-white p-8">
          {draft.sections.map((section, idx) => (
            <section key={idx} className="mb-8">
              <h2 className="font-ui mb-3 text-sm font-bold uppercase tracking-wide text-gray-900">
                {section.heading}
              </h2>
              <div className="space-y-2">
                {section.blocks.map((block, bIdx) => (
                  <p key={bIdx} className="group flex items-start gap-2 text-[15px] leading-relaxed text-gray-800">
                    <span className="flex-1">{block.text}</span>
                    <span className="opacity-0 transition-opacity group-hover:opacity-100">
                      <TierBadge tier={block.tier} />
                    </span>
                  </p>
                ))}
              </div>
            </section>
          ))}
        </article>

        <aside className="font-ui">
          <h2 className="mb-2 text-sm font-semibold text-gray-700">Flagged for review</h2>
          <FlaggedIssuesList issues={draft.flagged_issues} />
        </aside>
      </div>
    </div>
  )
}
