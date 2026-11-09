import type {
  AttachedPrecedent,
  CaseDocument,
  CaseFacts,
  CaseRecord,
  CategorySuggestion,
  CourtProceedingCombo,
  DraftOutput,
  DraftSection,
  ManualPrecedentInput,
  Precedent,
  ResearchReport,
} from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, init)
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      // ignore — fall back to statusText
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export async function createCaseFromText(text: string): Promise<CaseRecord> {
  const form = new FormData()
  form.append('text', text)
  return request('/cases', { method: 'POST', body: form })
}

export async function createCaseFromFile(file: File): Promise<CaseRecord> {
  const form = new FormData()
  form.append('file', file)
  return request('/cases', { method: 'POST', body: form })
}

export async function getCase(caseId: string): Promise<CaseRecord> {
  return request(`/cases/${caseId}`)
}

export async function updateCaseFacts(caseId: string, facts: CaseFacts): Promise<CaseRecord> {
  return request(`/cases/${caseId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(facts),
  })
}

export async function suggestCategory(caseId: string): Promise<CategorySuggestion> {
  return request(`/cases/${caseId}/suggest-category`, { method: 'POST' })
}

export async function runResearch(caseId: string): Promise<ResearchReport> {
  return request(`/cases/${caseId}/research`, { method: 'POST' })
}

export async function listCourts(): Promise<CourtProceedingCombo[]> {
  return request('/courts')
}

export async function createDraft(
  caseId: string,
  courtId: string,
  proceedingType: string,
): Promise<DraftOutput> {
  return request(`/cases/${caseId}/draft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ court_id: courtId, proceeding_type: proceedingType }),
  })
}

export function draftExportUrl(caseId: string): string {
  return `/api/cases/${caseId}/draft/export`
}

export async function updateDraftSections(caseId: string, sections: DraftSection[]): Promise<DraftOutput> {
  return request(`/cases/${caseId}/draft`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sections }),
  })
}

export async function approveDraft(caseId: string): Promise<DraftOutput> {
  return request(`/cases/${caseId}/draft/approve`, { method: 'POST' })
}

export async function listDocuments(caseId: string): Promise<CaseDocument[]> {
  return request(`/cases/${caseId}/documents`)
}

export async function uploadDocument(
  caseId: string,
  file: File,
  annexureLabel: string,
): Promise<CaseDocument> {
  const form = new FormData()
  form.append('file', file)
  if (annexureLabel.trim()) form.append('annexure_label', annexureLabel.trim())
  return request(`/cases/${caseId}/documents`, { method: 'POST', body: form })
}

export async function deleteDocument(caseId: string, documentId: string): Promise<void> {
  const res = await fetch(`/api/cases/${caseId}/documents/${documentId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to remove document.')
}

export function documentDownloadUrl(caseId: string, documentId: string): string {
  return `/api/cases/${caseId}/documents/${documentId}`
}

export async function listAttachedPrecedents(caseId: string): Promise<AttachedPrecedent[]> {
  return request(`/cases/${caseId}/precedents`)
}

export async function attachPrecedent(caseId: string, precedent: Precedent): Promise<AttachedPrecedent> {
  return request(`/cases/${caseId}/precedents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(precedent),
  })
}

export async function attachManualPrecedent(
  caseId: string,
  input: ManualPrecedentInput,
): Promise<AttachedPrecedent> {
  return request(`/cases/${caseId}/precedents/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
}

export async function detachPrecedent(caseId: string, precedentId: string): Promise<void> {
  const res = await fetch(`/api/cases/${caseId}/precedents/${precedentId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to remove precedent.')
}
