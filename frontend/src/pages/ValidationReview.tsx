import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getCase, runResearch, updateCaseFacts } from '../api/client'
import type { CaseFacts, KeyDate, Party } from '../api/types'
import { StepNav } from '../components/StepNav'
import { TierBadge } from '../components/TierBadge'
import { IssuesList } from '../components/IssuesList'

function emptyParty(): Party {
  return { role: '', name: '', relationship: '', details: '' }
}

function emptyDate(): KeyDate {
  return { label: '', date: '', description: '' }
}

export function ValidationReview() {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [facts, setFacts] = useState<CaseFacts | null>(null)

  const query = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => getCase(caseId!),
    enabled: !!caseId,
  })

  useEffect(() => {
    if (query.data) setFacts(query.data.case_facts)
  }, [query.data])

  const saveMutation = useMutation({
    mutationFn: (updated: CaseFacts) => updateCaseFacts(caseId!, updated),
    onSuccess: (record) => {
      queryClient.setQueryData(['case', caseId], record)
      setFacts(record.case_facts)
    },
  })

  const researchMutation = useMutation({
    mutationFn: async () => {
      if (facts) await updateCaseFacts(caseId!, facts)
      return runResearch(caseId!)
    },
    onSuccess: () => navigate(`/cases/${caseId}/research`),
  })

  if (query.isLoading || !facts) {
    return <div className="font-ui mx-auto max-w-3xl px-6 py-10 text-sm text-gray-500">Loading…</div>
  }

  const updateField = <K extends keyof CaseFacts>(key: K, value: CaseFacts[K]) =>
    setFacts((prev) => (prev ? { ...prev, [key]: value } : prev))

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <StepNav current="validate" />
      <div className="flex items-center justify-between">
        <h1 className="font-ui text-2xl font-bold text-gray-900">Review extracted facts</h1>
        <TierBadge tier="EXTRACTED" />
      </div>
      <p className="font-ui mt-1 text-sm text-gray-500">
        These facts were extracted from your input. Fill in anything flagged below before
        running research.
      </p>

      <section className="mt-6">
        <h2 className="font-ui mb-2 text-sm font-semibold text-gray-700">Validation issues</h2>
        <IssuesList issues={query.data?.validation_issues ?? []} />
      </section>

      <section className="mt-8 space-y-4">
        <h2 className="font-ui text-sm font-semibold text-gray-700">Parties</h2>
        {facts.parties.map((party, idx) => (
          <div key={idx} className="font-ui grid grid-cols-4 gap-2">
            <input
              className="rounded border border-gray-300 p-2 text-sm"
              placeholder="role (e.g. petitioner, detenu)"
              value={party.role}
              onChange={(e) => {
                const parties = [...facts.parties]
                parties[idx] = { ...party, role: e.target.value }
                updateField('parties', parties)
              }}
            />
            <input
              className="rounded border border-gray-300 p-2 text-sm"
              placeholder="name"
              value={party.name ?? ''}
              onChange={(e) => {
                const parties = [...facts.parties]
                parties[idx] = { ...party, name: e.target.value }
                updateField('parties', parties)
              }}
            />
            <input
              className="rounded border border-gray-300 p-2 text-sm"
              placeholder="relationship"
              value={party.relationship ?? ''}
              onChange={(e) => {
                const parties = [...facts.parties]
                parties[idx] = { ...party, relationship: e.target.value }
                updateField('parties', parties)
              }}
            />
            <input
              className="rounded border border-gray-300 p-2 text-sm"
              placeholder="details (age, address…)"
              value={party.details ?? ''}
              onChange={(e) => {
                const parties = [...facts.parties]
                parties[idx] = { ...party, details: e.target.value }
                updateField('parties', parties)
              }}
            />
          </div>
        ))}
        <button
          type="button"
          className="font-ui text-xs text-gray-400 underline"
          onClick={() => updateField('parties', [...facts.parties, emptyParty()])}
        >
          + Add party
        </button>
      </section>

      <section className="mt-8 space-y-4">
        <h2 className="font-ui text-sm font-semibold text-gray-700">Key dates</h2>
        {facts.key_dates.map((date, idx) => (
          <div key={idx} className="font-ui grid grid-cols-3 gap-2">
            <input
              className="rounded border border-gray-300 p-2 text-sm"
              placeholder="label (e.g. date of arrest)"
              value={date.label}
              onChange={(e) => {
                const dates = [...facts.key_dates]
                dates[idx] = { ...date, label: e.target.value }
                updateField('key_dates', dates)
              }}
            />
            <input
              type="date"
              className="rounded border border-gray-300 p-2 text-sm"
              value={date.date ?? ''}
              onChange={(e) => {
                const dates = [...facts.key_dates]
                dates[idx] = { ...date, date: e.target.value }
                updateField('key_dates', dates)
              }}
            />
            <input
              className="rounded border border-gray-300 p-2 text-sm"
              placeholder="description"
              value={date.description ?? ''}
              onChange={(e) => {
                const dates = [...facts.key_dates]
                dates[idx] = { ...date, description: e.target.value }
                updateField('key_dates', dates)
              }}
            />
          </div>
        ))}
        <button
          type="button"
          className="font-ui text-xs text-gray-400 underline"
          onClick={() => updateField('key_dates', [...facts.key_dates, emptyDate()])}
        >
          + Add date
        </button>
      </section>

      <section className="mt-8 grid grid-cols-2 gap-4">
        <div>
          <label className="font-ui mb-1 block text-sm font-semibold text-gray-700">Location</label>
          <input
            className="font-ui w-full rounded border border-gray-300 p-2 text-sm"
            value={facts.location ?? ''}
            onChange={(e) => updateField('location', e.target.value)}
          />
        </div>
        <div>
          <label className="font-ui mb-1 block text-sm font-semibold text-gray-700">
            Police station / authority
          </label>
          <input
            className="font-ui w-full rounded border border-gray-300 p-2 text-sm"
            value={facts.police_station ?? ''}
            onChange={(e) => updateField('police_station', e.target.value)}
          />
        </div>
      </section>

      <section className="mt-8">
        <label className="font-ui mb-1 block text-sm font-semibold text-gray-700">
          Facts narrative
        </label>
        <textarea
          className="font-ui h-32 w-full rounded border border-gray-300 p-2 text-sm"
          value={facts.facts_narrative}
          onChange={(e) => updateField('facts_narrative', e.target.value)}
        />
      </section>

      <section className="mt-8">
        <label className="font-ui mb-1 block text-sm font-semibold text-gray-700">
          Legal issues (comma separated)
        </label>
        <input
          className="font-ui w-full rounded border border-gray-300 p-2 text-sm"
          value={facts.legal_issues.join(', ')}
          onChange={(e) =>
            updateField(
              'legal_issues',
              e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
            )
          }
        />
      </section>

      <div className="mt-10 flex items-center gap-3">
        <button
          type="button"
          onClick={() => saveMutation.mutate(facts)}
          disabled={saveMutation.isPending}
          className="font-ui rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-700"
        >
          {saveMutation.isPending ? 'Saving…' : 'Save changes'}
        </button>
        <button
          type="button"
          onClick={() => researchMutation.mutate()}
          disabled={researchMutation.isPending}
          className="font-ui flex-1 rounded-lg bg-gray-900 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
        >
          {researchMutation.isPending ? 'Researching…' : 'Run research'}
        </button>
      </div>
      {researchMutation.isError && (
        <p className="font-ui mt-2 text-sm text-rose-600">
          {(researchMutation.error as Error).message}
        </p>
      )}
    </div>
  )
}
