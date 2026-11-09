import type { CaseType, CategorySuggestion } from '../api/types'
import { WRIT_CATEGORY_DESCRIPTIONS, WRIT_CATEGORY_LABELS } from '../api/types'
import { TierBadge } from './TierBadge'

const CATEGORIES: CaseType[] = ['habeas_corpus', 'mandamus', 'prohibition', 'certiorari', 'quo_warranto', 'other']

export function CategoryPicker({
  suggestion,
  value,
  onChange,
  onResuggest,
  resuggesting,
}: {
  suggestion: CategorySuggestion | null
  value: CaseType
  onChange: (category: CaseType) => void
  onResuggest?: () => void
  resuggesting?: boolean
}) {
  return (
    <div>
      {suggestion && (
        <div className="font-ui mb-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-amber-900">
                Suggested category: {WRIT_CATEGORY_LABELS[suggestion.category]}
              </span>
              <TierBadge tier="AI_ANALYSIS" />
            </div>
            <span className="shrink-0 text-xs text-amber-700">
              confidence {Math.round(suggestion.confidence * 100)}%
            </span>
          </div>
          <p className="mt-2 text-sm text-amber-900">{suggestion.reasoning}</p>
          {onResuggest && (
            <button
              type="button"
              onClick={onResuggest}
              disabled={resuggesting}
              className="mt-2 text-xs font-semibold text-amber-800 underline disabled:opacity-40"
            >
              {resuggesting ? 'Re-suggesting…' : 'Re-run suggestion from current facts'}
            </button>
          )}
        </div>
      )}

      <p className="font-ui mb-2 text-sm text-gray-500">
        Review the suggested writ petition category below, or pick a different one — this
        determines which required fields are checked and which draft template is used.
      </p>

      <div className="grid gap-2">
        {CATEGORIES.map((category) => {
          const isSelected = value === category
          const isSuggested = suggestion?.category === category
          return (
            <label
              key={category}
              className={`font-ui flex cursor-pointer items-start gap-3 rounded-lg border p-3 text-sm ${
                isSelected ? 'border-gray-900 bg-gray-50' : 'border-gray-200'
              }`}
            >
              <input
                type="radio"
                name="writ-category"
                className="mt-1"
                checked={isSelected}
                onChange={() => onChange(category)}
              />
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{WRIT_CATEGORY_LABELS[category]}</span>
                  {isSuggested && (
                    <span className="rounded border border-amber-300 bg-amber-50 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">
                      AI suggested
                    </span>
                  )}
                </div>
                <p className="text-gray-500">{WRIT_CATEGORY_DESCRIPTIONS[category]}</p>
              </div>
            </label>
          )
        })}
      </div>
    </div>
  )
}
