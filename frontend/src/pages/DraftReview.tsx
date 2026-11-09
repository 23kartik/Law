import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  approveDraft,
  deleteDocument,
  documentDownloadUrl,
  draftExportUrl,
  listDocuments,
  updateDraftSections,
  uploadDocument,
} from '../api/client'
import { StepNav } from '../components/StepNav'
import { TierBadge, TierLegend } from '../components/TierBadge'
import { FlaggedIssuesList } from '../components/IssuesList'
import type { DraftOutput, DraftSection } from '../api/types'

async function fetchDraft(caseId: string): Promise<DraftOutput> {
  const res = await fetch(`/api/cases/${caseId}/draft`)
  if (!res.ok) throw new Error('Draft not found — go back and generate it first.')
  return res.json()
}

function DocumentsPanel({ caseId }: { caseId: string }) {
  const queryClient = useQueryClient()
  const [file, setFile] = useState<File | null>(null)
  const [label, setLabel] = useState('')

  const documentsQuery = useQuery({
    queryKey: ['documents', caseId],
    queryFn: () => listDocuments(caseId),
  })

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error('Choose a file first.')
      return uploadDocument(caseId, file, label)
    },
    onSuccess: () => {
      setFile(null)
      setLabel('')
      queryClient.invalidateQueries({ queryKey: ['documents', caseId] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => deleteDocument(caseId, documentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents', caseId] }),
  })

  return (
    <div className="font-ui mt-8">
      <h2 className="mb-2 text-sm font-semibold text-gray-700">Supporting documents</h2>
      <p className="mb-3 text-xs text-gray-500">
        Attach or detach annexures and other supporting documents for this filing.
      </p>

      <ul className="space-y-2">
        {documentsQuery.data?.map((doc) => (
          <li
            key={doc.id}
            className="flex items-center justify-between gap-2 rounded-md border border-gray-200 p-2 text-sm"
          >
            <div className="min-w-0">
              <a
                href={documentDownloadUrl(caseId, doc.id)}
                target="_blank"
                rel="noreferrer"
                className="block truncate font-semibold text-sky-700 hover:underline"
              >
                {doc.annexure_label || doc.filename}
              </a>
              <p className="truncate text-xs text-gray-500">
                {doc.filename} · {(doc.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              type="button"
              onClick={() => deleteMutation.mutate(doc.id)}
              disabled={deleteMutation.isPending}
              className="shrink-0 text-xs font-semibold text-rose-600 underline disabled:opacity-40"
            >
              Detach
            </button>
          </li>
        ))}
        {documentsQuery.data?.length === 0 && (
          <p className="text-sm text-gray-500">No documents attached yet.</p>
        )}
      </ul>

      <div className="mt-3 space-y-2 rounded-md border border-dashed border-gray-300 p-3">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="block w-full text-xs"
        />
        <input
          className="w-full rounded border border-gray-300 p-1.5 text-xs"
          placeholder="Annexure label (e.g. Annexure No. 1 — FIR copy)"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        />
        <button
          type="button"
          onClick={() => uploadMutation.mutate()}
          disabled={!file || uploadMutation.isPending}
          className="w-full rounded-md bg-gray-900 py-1.5 text-xs font-semibold text-white disabled:opacity-40"
        >
          {uploadMutation.isPending ? 'Attaching…' : 'Attach document'}
        </button>
        {uploadMutation.isError && (
          <p className="text-xs text-rose-600">{(uploadMutation.error as Error).message}</p>
        )}
      </div>
    </div>
  )
}

export function DraftReview() {
  const { caseId } = useParams<{ caseId: string }>()
  const queryClient = useQueryClient()
  const [sections, setSections] = useState<DraftSection[] | null>(null)
  const [editing, setEditing] = useState(false)

  const draftQuery = useQuery({
    queryKey: ['draft', caseId],
    queryFn: () => fetchDraft(caseId!),
    enabled: !!caseId,
  })

  useEffect(() => {
    if (draftQuery.data) setSections(draftQuery.data.sections)
  }, [draftQuery.data])

  const saveMutation = useMutation({
    mutationFn: (updated: DraftSection[]) => updateDraftSections(caseId!, updated),
    onSuccess: (draft) => {
      queryClient.setQueryData(['draft', caseId], draft)
      setEditing(false)
    },
  })

  const approveMutation = useMutation({
    mutationFn: () => approveDraft(caseId!),
    onSuccess: (draft) => queryClient.setQueryData(['draft', caseId], draft),
  })

  if (draftQuery.isLoading || !sections) {
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
  const updateBlockText = (sectionIdx: number, blockIdx: number, text: string) => {
    setSections((prev) => {
      if (!prev) return prev
      const next = prev.map((s) => ({ ...s, blocks: s.blocks.map((b) => ({ ...b })) }))
      next[sectionIdx].blocks[blockIdx].text = text
      return next
    })
  }

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
        <div className="flex shrink-0 items-center gap-2">
          <span
            className={`font-ui rounded px-2 py-1 text-xs font-semibold uppercase tracking-wide ${
              draft.status === 'approved'
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {draft.status === 'approved' ? 'Approved' : 'Draft'}
          </span>
          <a
            href={draftExportUrl(caseId!)}
            className="font-ui rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white"
          >
            Download .docx
          </a>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <TierLegend />
        <div className="font-ui flex items-center gap-2">
          {editing ? (
            <>
              <button
                type="button"
                onClick={() => sections && saveMutation.mutate(sections)}
                disabled={saveMutation.isPending}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-semibold text-gray-700 disabled:opacity-40"
              >
                {saveMutation.isPending ? 'Saving…' : 'Save edits'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setSections(draft.sections)
                  setEditing(false)
                }}
                className="rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-500"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={() => setEditing(true)}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-semibold text-gray-700"
              >
                Edit draft
              </button>
              <button
                type="button"
                onClick={() => approveMutation.mutate()}
                disabled={approveMutation.isPending || draft.status === 'approved'}
                className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40"
              >
                {draft.status === 'approved'
                  ? 'Approved'
                  : approveMutation.isPending
                    ? 'Approving…'
                    : 'Approve final draft'}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-[1fr_320px] gap-8">
        <article className="rounded-lg border border-gray-200 bg-white p-8">
          {sections.map((section, idx) => (
            <section key={idx} className="mb-8">
              <h2 className="font-ui mb-3 text-sm font-bold uppercase tracking-wide text-gray-900">
                {section.heading}
              </h2>
              <div className="space-y-2">
                {section.blocks.map((block, bIdx) =>
                  editing ? (
                    <div key={bIdx} className="flex items-start gap-2">
                      <textarea
                        className="font-ui flex-1 rounded border border-gray-300 p-2 text-[15px] leading-relaxed text-gray-800"
                        value={block.text}
                        rows={Math.max(2, Math.ceil(block.text.length / 90))}
                        onChange={(e) => updateBlockText(idx, bIdx, e.target.value)}
                      />
                      <TierBadge tier={block.tier} />
                    </div>
                  ) : (
                    <p key={bIdx} className="group flex items-start gap-2 text-[15px] leading-relaxed text-gray-800">
                      <span className="flex-1 whitespace-pre-wrap">{block.text}</span>
                      <span className="opacity-0 transition-opacity group-hover:opacity-100">
                        <TierBadge tier={block.tier} />
                      </span>
                    </p>
                  ),
                )}
              </div>
            </section>
          ))}
        </article>

        <aside className="font-ui">
          <h2 className="mb-2 text-sm font-semibold text-gray-700">Flagged for review</h2>
          <FlaggedIssuesList issues={draft.flagged_issues} />
          <DocumentsPanel caseId={caseId!} />
        </aside>
      </div>
    </div>
  )
}
