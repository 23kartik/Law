import { Navigate, Route, Routes } from 'react-router-dom'
import { CourtSelect } from './pages/CourtSelect'
import { DraftReview } from './pages/DraftReview'
import { NewCase } from './pages/NewCase'
import { ResearchResults } from './pages/ResearchResults'
import { ValidationReview } from './pages/ValidationReview'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="font-ui border-b border-gray-200 bg-white px-6 py-4">
        <span className="font-semibold text-gray-900">Evidence-Driven Legal Advocacy Platform</span>
      </header>
      <Routes>
        <Route path="/" element={<NewCase />} />
        <Route path="/cases/:caseId/validate" element={<ValidationReview />} />
        <Route path="/cases/:caseId/research" element={<ResearchResults />} />
        <Route path="/cases/:caseId/select" element={<CourtSelect />} />
        <Route path="/cases/:caseId/draft" element={<DraftReview />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
