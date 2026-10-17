const STEPS = [
  { key: 'new', label: 'Input case' },
  { key: 'validate', label: 'Validate' },
  { key: 'research', label: 'Research' },
  { key: 'select', label: 'Select court' },
  { key: 'draft', label: 'Draft' },
]

export function StepNav({ current }: { current: string }) {
  const currentIdx = STEPS.findIndex((s) => s.key === current)
  return (
    <ol className="font-ui mb-8 flex items-center gap-2 text-sm">
      {STEPS.map((step, idx) => {
        const isActive = idx === currentIdx
        const isDone = idx < currentIdx
        return (
          <li key={step.key} className="flex items-center gap-2">
            <span
              className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold ${
                isActive
                  ? 'bg-gray-900 text-white'
                  : isDone
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-gray-100 text-gray-400'
              }`}
            >
              {idx + 1}
            </span>
            <span className={isActive ? 'font-semibold text-gray-900' : 'text-gray-400'}>
              {step.label}
            </span>
            {idx < STEPS.length - 1 && <span className="mx-1 text-gray-300">—</span>}
          </li>
        )
      })}
    </ol>
  )
}
