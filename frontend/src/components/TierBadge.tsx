import type { Tier } from '../api/types'

const TIER_STYLES: Record<Tier, { label: string; className: string }> = {
  VERIFIED_COURT: {
    label: 'Verified court data',
    className: 'bg-emerald-50 text-emerald-800 border-emerald-300',
  },
  EXTRACTED: {
    label: 'From your input',
    className: 'bg-sky-50 text-sky-800 border-sky-300',
  },
  AI_ANALYSIS: {
    label: 'AI analysis',
    className: 'bg-amber-50 text-amber-800 border-amber-300',
  },
}

export function TierBadge({ tier }: { tier: Tier }) {
  const style = TIER_STYLES[tier]
  return (
    <span
      className={`font-ui inline-block shrink-0 whitespace-nowrap rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${style.className}`}
    >
      {style.label}
    </span>
  )
}

export function TierLegend() {
  return (
    <div className="font-ui flex flex-wrap gap-3 text-xs text-gray-500">
      {(Object.keys(TIER_STYLES) as Tier[]).map((tier) => (
        <div key={tier} className="flex items-center gap-1.5">
          <TierBadge tier={tier} />
        </div>
      ))}
    </div>
  )
}
