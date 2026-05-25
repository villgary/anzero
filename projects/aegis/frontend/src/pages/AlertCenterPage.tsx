import { useState, useEffect, useMemo } from 'react'
import { Tabs, Button } from 'antd'
import { AlertList, Alert } from '../components/alerts/AlertList'
import { AlertFilters, AlertFilters as AlertFiltersType } from '../components/alerts/AlertFilters'

// Demo historical data
const historicalAlerts: Alert[] = [
  { id: 'h1', priority: 'P0', confidence: 0.95, tool: 'PentestGPT', time: '2026-05-25 14:32:15' },
  { id: 'h2', priority: 'P1', confidence: 0.82, tool: 'ReconAI', time: '2026-05-25 13:28:42' },
  { id: 'h3', priority: 'P2', confidence: 0.68, tool: 'AttackGPT', time: '2026-05-25 12:15:08' },
  { id: 'h4', priority: 'P1', confidence: 0.75, tool: 'PentestGPT', time: '2026-05-25 11:42:33' },
  { id: 'h5', priority: 'P3', confidence: 0.42, tool: 'Scanner', time: '2026-05-25 10:20:19' },
  { id: 'h6', priority: 'P0', confidence: 0.91, tool: 'AttackGPT', time: '2026-05-24 16:45:22' },
  { id: 'h7', priority: 'P1', confidence: 0.78, tool: 'ReconAI', time: '2026-05-24 15:30:11' },
]

export function AlertCenterPage() {
  const [realtimeAlerts, setRealtimeAlerts] = useState<Alert[]>([])
  const [connected, setConnected] = useState(false)
  const [filters, setFilters] = useState<AlertFiltersType>({
    priorities: [],
    tools: [],
    timeRange: null,
    searchText: ''
  })
  const [activeTab, setActiveTab] = useState('realtime')

  // WebSocket connection
  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: number | null = null

    const connect = () => {
      ws = new WebSocket(`ws://${window.location.host}/api/v1/alerts/stream`)
      ws.onopen = () => setConnected(true)
      ws.onerror = () => {
        console.error('WebSocket error')
      }
      ws.onclose = () => {
        setConnected(false)
        reconnectTimer = window.setTimeout(connect, 3000)
      }
      ws.onmessage = (event) => {
        const newAlert = JSON.parse(event.data)
        setRealtimeAlerts(prev => [{ ...newAlert, id: Date.now().toString() }, ...prev])
      }
    }

    connect()

    return () => {
      if (ws) ws.close()
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }
  }, [])

  // Filter alerts based on current filters
  const filteredAlerts = useMemo(() => {
    const sourceAlerts = activeTab === 'realtime' ? realtimeAlerts : historicalAlerts

    return sourceAlerts.filter(alert => {
      // Priority filter
      if (filters.priorities.length > 0 && !filters.priorities.includes(alert.priority)) {
        return false
      }
      // Tool filter
      if (filters.tools.length > 0 && !filters.tools.includes(alert.tool)) {
        return false
      }
      // Search filter
      if (filters.searchText) {
        const searchLower = filters.searchText.toLowerCase()
        if (!alert.tool.toLowerCase().includes(searchLower)) {
          return false
        }
      }
      return true
    })
  }, [realtimeAlerts, historicalAlerts, filters, activeTab])

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Alert Center</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm">
            Status:{' '}
            {connected ? (
              <span className="text-green-400">Real-time Connected</span>
            ) : (
              <span className="text-gray-400">Disconnected</span>
            )}
          </span>
          <Button type="primary" danger>
            Export
          </Button>
        </div>
      </div>

      {/* Filters */}
      <AlertFilters onFilterChange={setFilters} />

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        className="text-white"
        items={[
          {
            key: 'realtime',
            label: 'Real-time',
            children: (
              <AlertList alerts={filteredAlerts} />
            )
          },
          {
            key: 'history',
            label: 'History',
            children: (
              <AlertList alerts={filteredAlerts} />
            )
          }
        ]}
      />
    </div>
  )
}
