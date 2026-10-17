export type Tier = 'VERIFIED_COURT' | 'EXTRACTED' | 'AI_ANALYSIS'

export type Severity = 'missing' | 'conflicting' | 'unsupported' | 'needs_review'

export type CaseType = 'habeas_corpus' | 'other'

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

export interface CaseRecord {
  id: string
  raw_text: string
  case_facts: CaseFacts
  validation_issues: ValidationIssue[]
  created_at: string
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
  generated_at: string
}

export interface CourtProceedingCombo {
  court_id: string
  court_name: string
  proceeding_type: string
  proceeding_name: string
}
