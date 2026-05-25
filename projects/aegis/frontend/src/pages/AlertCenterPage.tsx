import { useState, useEffect } from 'react'
import { AlertList } from '../components/alerts/AlertList'
import { api } from '../api/client'

export function AlertCenterPage() {
  const [alerts, setAlerts] = useState([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: number | null = null

    const connect = () => {
      ws = new WebSocket(`ws://${window.location.host}/api/v1/alerts/stream`)
      ws.onopen = () => setConnected(true)
      ws.onerror = (err) => {
        console.error('WebSocket error:', err)
      }
      ws.onclose = () => {
        setConnected(false)
        reconnectTimer = window.setTimeout(connect, 3000)
      }
      ws.onmessage = (event) => {
        setAlerts(prev => [JSON.parse(event.data), ...prev])
      }
    }

    connect()

    return () => {
      if (ws) ws.close()
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }
  }, [])

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-bold text-white mb-6">Alert Center</h1>
      <div className="text-sm mb-4">
        Status: {connected ? (
          <span className="text-green-400">Connected</span>
        ) : (
          <span className="text-gray-400">Disconnected</span>
        )}
      </div>
      <AlertList alerts={alerts} />
    </div>
  )
}