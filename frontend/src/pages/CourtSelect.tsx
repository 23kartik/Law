import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createDraft, listCourts } from '../api/client'
import { StepNav } from '../components/StepNav'

export function CourtSelect() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [selected, setSelected] = useState<string | null>(null)

  const courtsQuery = useQuery({ queryKey: ['courts'], queryFn: listCourts })

  const draftMutation = useMutation({
    mutationFn: () => {
      const combo = courtsQuery.data?.find(
        (c) => `${c.court_id}::${c.proceeding_type}` === selected,
      )
      if (!combo) throw new Error('Select a court and proceeding type first.')
      return createDraft(caseId!, combo.court_id, combo.proceeding_type)
    },
    onSuccess: () => navigate(`/cases/${caseId}/draft`),
  })

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <StepNav current="select" />
      <h1 className="font-ui text-2xl font-bold text-gray-900">Select the target court</h1>
      <p className="font-ui mt-1 text-sm text-gray-500">
        Format, structure, terminology and filing requirements are adapted to the court and
        proceeding you pick here.
      </p>

      <div className="mt-6 space-y-3">
        {courtsQuery.isLoading && <p className="font-ui text-sm text-gray-500">Loading…</p>}
        {courtsQuery.data?.map((combo) => {
          const key = `${combo.court_id}::${combo.proceeding_type}`
          return (
            <label
              key={key}
              className={`font-ui flex cursor-pointer items-center gap-3 rounded-lg border p-4 text-sm ${
                selected === key ? 'border-gray-900 bg-gray-50' : 'border-gray-200'
              }`}
            >
              <input
                type="radio"
                name="combo"
                checked={selected === key}
                onChange={() => setSelected(key)}
              />
              <div>
                <p className="font-semibold text-gray-900">{combo.proceeding_name}</p>
                <p className="text-gray-500">{combo.court_name}</p>
              </div>
            </label>
          )
        })}
        {courtsQuery.data?.length === 0 && (
          <p className="font-ui text-sm text-gray-500">No court templates configured yet.</p>
        )}
      </div>

      {draftMutation.isError && (
        <p className="font-ui mt-3 text-sm text-rose-600">{(draftMutation.error as Error).message}</p>
      )}

      <button
        type="button"
        disabled={!selected || draftMutation.isPending}
        onClick={() => draftMutation.mutate()}
        className="font-ui mt-8 w-full rounded-lg bg-gray-900 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
      >
        {draftMutation.isPending ? 'Generating draft…' : 'Generate draft'}
      </button>
    </div>
  )
}
