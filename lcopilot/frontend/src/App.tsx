import { Routes, Route, Navigate } from 'react-router-dom'
import WelcomePage from './pages/WelcomePage'
import UploadPage from './pages/UploadPage'
import ReviewPage from './pages/ReviewPage'
import ReportPage from './pages/ReportPage'
import StubModeIndicator from './components/StubModeIndicator'
import DiscrepancyListDemo from './components/DiscrepancyListDemo'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/review/:sessionId" element={<ReviewPage />} />
        <Route path="/report/:sessionId" element={<ReportPage />} />
        <Route path="/demo" element={<DiscrepancyListDemo />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <StubModeIndicator />
    </>
  )
}

export default App