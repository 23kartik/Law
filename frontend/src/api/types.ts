export type Tier = 'VERIFIED_COURT' | 'EXTRACTED' | 'AI_ANALYSIS'

export type Severity = 'missing' | 'conflicting' | 'unsupported' | 'needs_review'

export type DraftStatus = 'draft' | 'approved'

export type CaseType =
  | 'habeas_corpus'
  | 'mandamus'
  | 'prohibition'
  | 'certiorari'
  | 'quo_warranto'
  | 'other'

export const WRIT_CATEGORY_LABELS: Record<CaseType, string> = {
  habeas_corpus: 'Habeas Corpus',
  mandamus: 'Mandamus',
  prohibition: 'Prohibition',
  certiorari: 'Certiorari',
  quo_warranto: 'Quo Warranto',
  other: 'Other / none of the above',
}

export const WRIT_CATEGORY_DESCRIPTIONS: Record<CaseType, string> = {
  habeas_corpus:
    'A person is allegedly detained illegally — seeks production of the detained person before the court and appropriate relief.',
  mandamus:
    'A government authority or public official has failed to perform a legal or public duty — seeks a court direction to perform it.',
  prohibition:
    'A lower court or tribunal is proceeding beyond its legal authority — seeks to stop it before it decides the matter.',
  certiorari:
    'A lower court, tribunal, or authority has already passed an unlawful order (e.g. an FIR) — seeks to quash it.',
  quo_warranto:
    "A person's legal authority to hold a public office is in question — seeks to challenge their right to hold it.",
  other: 'The matter does not fit any of the five writ categories above.',
}

export interface Party {
  role: string
  name: string | null
  relationship: string | null
  details: string | null
}

export interface KeyDate {
  label: string
  date: string | null
  description: string | null
}

export interface CaseFacts {
  case_type: CaseType
  parties: Party[]
  key_dates: KeyDate[]
  location: string | null
  police_station: string | null
  case_reference_number: string | null
  authority_name: string | null
  facts_narrative: string
  legal_issues: string[]
  missing_fields: string[]
}

export interface ValidationIssue {
  field: string
  severity: Severity
  message: string
  tier: Tier
}

export interface CategorySuggestion {
  category: CaseType
  confidence: number
  reasoning: string
  tier: Tier
}

export interface CaseRecord {
  id: string
  raw_text: string
  case_facts: CaseFacts
  validation_issues: ValidationIssue[]
  category_suggestion: CategorySuggestion | null
  created_at: string
}

export interface CaseDocument {
  id: string
  filename: string
  content_type: string
  size: number
  annexure_label: string | null
  uploaded_at: string
}

export interface Precedent {
  title: string
  citation: string | null
  court: string | null
  date: string | null
  source_url: string
  snippet: string
  relevance_score: number
  applicability_note: string | null
  retrieved_at: string
  source_adapter: string
  tier: Tier
}

export interface ResearchFinding {
  summary: string
  tier: Tier
  supporting_precedent_titles: string[]
}

export interface ConfidenceBreakdown {
  data_completeness: number
  source_count_score: number
  court_authority_weight: number
  llm_relevance_avg: number
}

export interface ResearchReport {
  findings: ResearchFinding[]
  precedents: Precedent[]
  confidence_score: number
  confidence_breakdown: ConfidenceBreakdown
  generated_at: string
}

export interface AttachedPrecedent extends Precedent {
  id: string
  attach_source: 'research' | 'manual'
  attached_at: string
}

export interface ManualPrecedentInput {
  title: string
  citation: string | null
  court: string | null
  date: string | null
  source_url: string | null
  note: string | null
}

export interface ContentBlock {
  text: string
  tier: Tier
}

export interface DraftSection {
  heading: string
  paragraph_prefix: string | null
  blocks: ContentBlock[]
}

export interface FlaggedIssue {
  category: string
  severity: Severity
  message: string
  section: string | null
}

export interface DraftOutput {
  court_id: string
  proceeding_type: string
  sections: DraftSection[]
  flagged_issues: FlaggedIssue[]
  confidence_score: number
  status: DraftStatus
  generated_at: string
}

export interface CourtProceedingCombo {
  court_id: string
  court_name: string
  proceeding_type: string
  proceeding_name: string
}
