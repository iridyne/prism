import { Navigate, Route, Routes } from 'react-router-dom'

import Dashboard from './pages/Dashboard'
import Wizard from './pages/Wizard'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Wizard />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/dashboard/:portfolioId" element={<Dashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
