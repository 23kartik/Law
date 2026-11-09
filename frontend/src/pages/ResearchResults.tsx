import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ConfidenceGauge } from '../components/ConfidenceGauge'
import { StepNav } from '../components/StepNav'
import { TierBadge } from '../components/TierBadge'
import {
  attachManualPrecedent,
  attachPrecedent,
  detachPrecedent,
  listAttachedPrecedents,
} from '../api/client'
import type { ManualPrecedentInput, Precedent, ResearchReport } from '../api/types'

async function fetchResearch(caseId: string): Promise<ResearchReport> {
  const res = await fetch(`/api/cases/${caseId}/research`)
  if (!res.ok) throw new Error('Research not found — go back and run it first.')
  return res.json()
}

const emptyManualPrecedent: ManualPrecedentInput = {
  title: '',
  citation: '',
  court: '',
  date: '',
  source_url: '',
  note: '',
}

export function ResearchResults() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [manual, setManual] = useState<ManualPrecedentInput>(emptyManualPrecedent)
  const [showManualForm, setShowManualForm] = useState(false)

  const researchQuery = useQuery({
    queryKey: ['research', caseId],
    queryFn: () => fetchResearch(caseId!),
    enabled: !!caseId,
  })

  const attachedQuery = useQuery({
    queryKey: ['attachedPrecedents', caseId],
    queryFn: () => listAttachedPrecedents(caseId!),
    enabled: !!caseId,
  })

  const attachMutation = useMutation({
    mutationFn: (precedent: Precedent) => attachPrecedent(caseId!, precedent),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['attachedPrecedents', caseId] }),
  })

  const attachManualMutation = useMutation({
    mutationFn: (input: ManualPrecedentInput) => attachManualPrecedent(caseId!, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attachedPrecedents', caseId] })
      setManual(emptyManualPrecedent)
      setShowManualForm(false)
    },
  })

  const detachMutation = useMutation({
    mutationFn: (precedentId: string) => detachPrecedent(caseId!, precedentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['attachedPrecedents', caseId] }),
  })

  const attachedTitles = new Set((attachedQuery.data ?? []).map((p) => p.title.trim().toLowerCase()))

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
            {report.precedents.map((p, idx) => {
              const isAttached = attachedTitles.has(p.title.trim().toLowerCase())
              return (
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
                  <button
                    type="button"
                    disabled={isAttached || attachMutation.isPending}
                    onClick={() => attachMutation.mutate(p)}
                    className={`mt-3 rounded-md border px-3 py-1.5 text-xs font-semibold disabled:opacity-60 ${
                      isAttached
                        ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                        : 'border-gray-300 text-gray-700'
                    }`}
                  >
                    {isAttached ? 'Attached to case' : 'Attach to case'}
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="font-ui mb-2 text-sm font-semibold text-gray-700">
          Attached precedents ({attachedQuery.data?.length ?? 0})
        </h2>
        <p className="font-ui mb-3 text-xs text-gray-500">
          When one or more precedents are attached, the draft cites only these instead of
          every precedent research turned up. Attach a few above, or add one by hand below
          if you know of a case research didn't surface.
        </p>

        {(attachedQuery.data?.length ?? 0) === 0 ? (
          <p className="font-ui text-sm text-gray-500">No precedents attached yet.</p>
        ) : (
          <ul className="space-y-2">
            {attachedQuery.data!.map((p) => (
              <li
                key={p.id}
                className="font-ui flex items-start justify-between gap-2 rounded-md border border-gray-200 p-3 text-sm"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900">{p.title}</span>
                    <TierBadge tier={p.tier} />
                    {p.attach_source === 'manual' && (
                      <span className="rounded border border-gray-300 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-gray-500">
                        Manually added
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500">
                    {p.citation || 'No citation given'} · {p.court ?? 'Unknown court'}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => detachMutation.mutate(p.id)}
                  disabled={detachMutation.isPending}
                  className="shrink-0 text-xs font-semibold text-rose-600 underline disabled:opacity-40"
                >
                  Detach
                </button>
              </li>
            ))}
          </ul>
        )}

        {showManualForm ? (
          <div className="mt-3 space-y-2 rounded-md border border-dashed border-gray-300 p-3">
            <input
              className="font-ui w-full rounded border border-gray-300 p-1.5 text-sm"
              placeholder="Case title (required)"
              value={manual.title}
              onChange={(e) => setManual((m) => ({ ...m, title: e.target.value }))}
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                className="font-ui rounded border border-gray-300 p-1.5 text-sm"
                placeholder="Citation"
                value={manual.citation ?? ''}
                onChange={(e) => setManual((m) => ({ ...m, citation: e.target.value }))}
              />
              <input
                className="font-ui rounded border border-gray-300 p-1.5 text-sm"
                placeholder="Court"
                value={manual.court ?? ''}
                onChange={(e) => setManual((m) => ({ ...m, court: e.target.value }))}
              />
            </div>
            <input
              className="font-ui w-full rounded border border-gray-300 p-1.5 text-sm"
              placeholder="Source URL (optional)"
              value={manual.source_url ?? ''}
              onChange={(e) => setManual((m) => ({ ...m, source_url: e.target.value }))}
            />
            <textarea
              className="font-ui w-full rounded border border-gray-300 p-1.5 text-sm"
              placeholder="Why this precedent applies (optional)"
              value={manual.note ?? ''}
              onChange={(e) => setManual((m) => ({ ...m, note: e.target.value }))}
            />
            <div className="flex gap-2">
              <button
                type="button"
                disabled={!manual.title.trim() || attachManualMutation.isPending}
                onClick={() => attachManualMutation.mutate(manual)}
                className="font-ui flex-1 rounded-md bg-gray-900 py-1.5 text-xs font-semibold text-white disabled:opacity-40"
              >
                {attachManualMutation.isPending ? 'Adding…' : 'Add precedent'}
              </button>
              <button
                type="button"
                onClick={() => setShowManualForm(false)}
                className="font-ui rounded-md px-3 py-1.5 text-xs font-semibold text-gray-500"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setShowManualForm(true)}
            className="font-ui mt-3 text-xs font-semibold text-gray-600 underline"
          >
            + Add a precedent by hand
          </button>
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
