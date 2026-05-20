import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ScansPage from './pages/ScansPage'
import ScanDetailPage from './pages/ScanDetailPage'
import MainLayout from './components/MainLayout'
import { useAuthStore } from './store/auth'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="scans" element={<ScansPage />} />
        <Route path="scans/:scan_id" element={<ScanDetailPage />} />
      </Route>
    </Routes>
  )
}

export default App