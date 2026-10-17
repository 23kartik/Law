import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCaseFromFile, createCaseFromText } from '../api/client'
import { StepNav } from '../components/StepNav'

const EXAMPLE =
  'My brother has been detained by Karlobag Police for the past 24 hours. I want to file a Habeas Corpus petition to challenge his detention and seek his immediate release.'

export function NewCase() {
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)

  const mutation = useMutation({
    mutationFn: async () => {
      if (file) return createCaseFromFile(file)
      return createCaseFromText(text)
    },
    onSuccess: (record) => navigate(`/cases/${record.id}/validate`),
  })

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <StepNav current="new" />
      <h1 className="font-ui text-2xl font-bold text-gray-900">Start a new case</h1>
      <p className="font-ui mt-1 text-sm text-gray-500">
        Describe the matter in your own words, or upload an existing document. We'll validate
        the facts before doing anything else.
      </p>

      <div className="mt-6 space-y-4">
        <textarea
          className="font-ui h-40 w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-gray-900 focus:outline-none"
          placeholder={EXAMPLE}
          value={text}
          disabled={!!file}
          onChange={(e) => setText(e.target.value)}
        />
        <button
          type="button"
          className="font-ui text-xs text-gray-400 underline"
          onClick={() => setText(EXAMPLE)}
        >
          Use example narrative
        </button>

        <div className="font-ui flex items-center gap-3 text-sm text-gray-400">
          <div className="h-px flex-1 bg-gray-200" />
          or
          <div className="h-px flex-1 bg-gray-200" />
        </div>

        <label className="font-ui flex cursor-pointer items-center justify-center rounded-lg border border-dashed border-gray-300 p-6 text-sm text-gray-500 hover:border-gray-400">
          {file ? file.name : 'Upload a PDF document'}
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        {file && (
          <button
            type="button"
            className="font-ui text-xs text-gray-400 underline"
            onClick={() => setFile(null)}
          >
            Remove file
          </button>
        )}

        {mutation.isError && (
          <p className="font-ui text-sm text-rose-600">{(mutation.error as Error).message}</p>
        )}

        <button
          type="button"
          disabled={(!text.trim() && !file) || mutation.isPending}
          onClick={() => mutation.mutate()}
          className="font-ui w-full rounded-lg bg-gray-900 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
        >
          {mutation.isPending ? 'Validating…' : 'Validate case data'}
        </button>
      </div>
    </div>
  )
}
