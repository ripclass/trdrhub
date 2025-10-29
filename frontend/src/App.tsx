import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LCopilotPage from './pages/LCopilotPage'
import './index.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/lcopilot" element={<LCopilotPage />} />
      </Routes>
    </Router>
  )
}

export default App
