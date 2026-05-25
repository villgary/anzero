import { useState, useEffect } from 'react'
import { AlertList } from '../components/alerts/AlertList'
import { api } from '../api/client'

export function AlertCenterPage() {
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/api/v1/alerts/stream')
    ws.onmessage = (event) => {
      setAlerts(prev => [JSON.parse(event.data), ...prev])
    }
    return () => ws.close()
  }, [])

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-bold text-white mb-6">Alert Center</h1>
      <AlertList alerts={alerts} />
    </div>
  )
}