import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { AlertCenterPage } from './pages/AlertCenterPage'
import { InvestigationPage } from './pages/InvestigationPage'

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/alerts" element={<AlertCenterPage />} />
          <Route path="/investigation" element={<InvestigationPage />} />
          <Route path="/config" element={<div className="p-6 text-white">Configuration - Coming Soon</div>} />
          <Route path="/intel" element={<div className="p-6 text-white">Intelligence - Coming Soon</div>} />
          <Route path="/museum" element={<div className="p-6 text-white">Museum - Coming Soon</div>} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  )
}

export default App
