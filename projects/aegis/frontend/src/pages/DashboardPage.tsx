import { useState, useEffect } from 'react'
import { MetricCard } from '../components/dashboard/MetricCard'
import { AttackTrendChart } from '../components/dashboard/AttackTrendChart'
import { api } from '../api/client'

interface DashboardStats {
  attackCount: number
  mttd: string
  counterRate: number
  threatLevel: string
}

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)

  useEffect(() => {
    api.get('/dashboard/stats').then(res => setStats(res.data))
  }, [])

  if (!stats) return <div>Loading...</div>

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard title="本月攻击" value={stats.attackCount} />
        <MetricCard title="MTTD" value={stats.mttd} />
        <MetricCard title="反制率" value={`${stats.counterRate}%`} />
        <MetricCard title="威胁等级" value={stats.threatLevel} color="red" />
      </div>
      <AttackTrendChart />
    </div>
  )
}