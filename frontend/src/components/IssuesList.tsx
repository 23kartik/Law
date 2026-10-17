import type { FlaggedIssue, Severity, ValidationIssue } from '../api/types'

const SEVERITY_STYLES: Record<Severity, string> = {
  missing: 'border-rose-300 bg-rose-50 text-rose-800',
  conflicting: 'border-orange-300 bg-orange-50 text-orange-800',
  unsupported: 'border-amber-300 bg-amber-50 text-amber-800',
  needs_review: 'border-violet-300 bg-violet-50 text-violet-800',
}

const SEVERITY_LABELS: Record<Severity, string> = {
  missing: 'Missing',
  conflicting: 'Conflicting',
  unsupported: 'Unsupported claim',
  needs_review: 'Needs lawyer review',
}

export function IssuesList({ issues }: { issues: ValidationIssue[] }) {
  if (issues.length === 0) {
    return <p className="font-ui text-sm text-emerald-700">No validation issues found.</p>
  }
  return (
    <ul className="space-y-2">
      {issues.map((issue, idx) => (
        <li
          key={idx}
          className={`font-ui rounded-md border px-3 py-2 text-sm ${SEVERITY_STYLES[issue.severity]}`}
        >
          <span className="mr-2 text-[10px] font-semibold uppercase tracking-wide">
            {SEVERITY_LABELS[issue.severity]}
          </span>
          <span className="font-semibold">{issue.field}:</span> {issue.message}
        </li>
      ))}
    </ul>
  )
}

export function FlaggedIssuesList({ issues }: { issues: FlaggedIssue[] }) {
  if (issues.length === 0) {
    return <p className="font-ui text-sm text-emerald-700">Nothing flagged.</p>
  }
  return (
    <ul className="space-y-2">
      {issues.map((issue, idx) => (
        <li
          key={idx}
          className={`font-ui rounded-md border px-3 py-2 text-sm ${SEVERITY_STYLES[issue.severity]}`}
        >
          <div className="flex items-center justify-between gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-wide">
              {issue.category.replace(/_/g, ' ')}
            </span>
            {issue.section && (
              <span className="text-[10px] text-gray-500">{issue.section}</span>
            )}
          </div>
          <p>{issue.message}</p>
        </li>
      ))}
    </ul>
  )
}
