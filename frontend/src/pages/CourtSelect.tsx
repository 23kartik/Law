import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createDraft, getCase, listCourts } from '../api/client'
import { StepNav } from '../components/StepNav'
import { WRIT_CATEGORY_LABELS } from '../api/types'

export function CourtSelect() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const [selected, setSelected] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(false)

  const caseQuery = useQuery({ queryKey: ['case', caseId], queryFn: () => getCase(caseId!), enabled: !!caseId })
  const courtsQuery = useQuery({ queryKey: ['courts'], queryFn: listCourts })

  const category = caseQuery.data?.case_facts.case_type
  const combos = courtsQuery.data ?? []
  const matching = category ? combos.filter((c) => c.proceeding_type === category) : combos
  const visible = showAll || matching.length === 0 ? combos : matching

  useEffect(() => {
    if (!selected && matching.length === 1) {
      setSelected(`${matching[0].court_id}::${matching[0].proceeding_type}`)
    }
  }, [matching, selected])

  const draftMutation = useMutation({
    mutationFn: () => {
      const combo = combos.find((c) => `${c.court_id}::${c.proceeding_type}` === selected)
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
        {category && (
          <>
            {' '}
            Showing templates for the selected category:{' '}
            <span className="font-semibold text-gray-700">{WRIT_CATEGORY_LABELS[category]}</span>.
          </>
        )}
      </p>

      <div className="mt-6 space-y-3">
        {(courtsQuery.isLoading || caseQuery.isLoading) && (
          <p className="font-ui text-sm text-gray-500">Loading…</p>
        )}
        {visible.map((combo) => {
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
        {combos.length === 0 && (
          <p className="font-ui text-sm text-gray-500">No court templates configured yet.</p>
        )}
      </div>

      {matching.length > 0 && matching.length < combos.length && (
        <button
          type="button"
          className="font-ui mt-3 text-xs text-gray-400 underline"
          onClick={() => setShowAll((v) => !v)}
        >
          {showAll ? 'Show only templates for the selected category' : 'Show all court/proceeding templates'}
        </button>
      )}

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
