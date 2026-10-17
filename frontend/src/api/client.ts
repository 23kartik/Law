import type {
  CaseFacts,
  CaseRecord,
  CourtProceedingCombo,
  DraftOutput,
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
