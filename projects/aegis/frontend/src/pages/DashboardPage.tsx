import { useState, useEffect } from 'react'
import { MetricCard } from '../components/dashboard/MetricCard'
import { AttackTrendChart } from '../components/dashboard/AttackTrendChart'
import { ToolDistributionChart } from '../components/dashboard/ToolDistributionChart'
import { AttackSourceMap } from '../components/dashboard/AttackSourceMap'
import { RecentAlerts } from '../components/dashboard/RecentAlerts'
import { api } from '../api/client'

interface DashboardStats {
  attackCount: number
  mttd: string
  counterRate: number
  threatLevel: string
}

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get('/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(() => setError('Failed to load dashboard data'))
  }, [])

  // Get current time for header
  const now = new Date()
  const timeStr = now.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })

  if (error) return <div className="text-red-400 p-6">{error}</div>
  if (!stats) return <div className="text-gray-400 p-6">Loading...</div>

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">AegisAI Dashboard</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-400 text-sm">{timeStr}</span>
          <button className="px-3 py-1 text-sm text-gray-400 hover:text-white border border-gray-600 rounded">
            Fullscreen
          </button>
          <button className="px-3 py-1 text-sm text-gray-400 hover:text-white border border-gray-600 rounded">
            Settings
          </button>
        </div>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard title="Attack Count" value={stats.attackCount} />
        <MetricCard title="MTTD" value={stats.mttd} />
        <MetricCard title="Counter Rate" value={`${stats.counterRate}%`} />
        <MetricCard title="Threat Level" value={stats.threatLevel} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="col-span-2">
          <AttackTrendChart />
        </div>
        <div>
          <ToolDistributionChart />
        </div>
      </div>

      {/* Map */}
      <div className="mb-6">
        <AttackSourceMap />
      </div>

      {/* Recent Alerts */}
      <RecentAlerts />
    </div>
  )
}
