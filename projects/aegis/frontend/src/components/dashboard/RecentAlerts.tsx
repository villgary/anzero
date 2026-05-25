import { Tag } from 'antd'
import { Alert } from '../alerts/AlertList'

interface RecentAlertsProps {
  alerts?: Alert[]
}

const priorityColors: Record<string, string> = {
  P0: 'red',
  P1: 'orange',
  P2: 'yellow',
  P3: 'blue'
}

export function RecentAlerts({ alerts }: RecentAlertsProps) {
  // Default demo data
  const defaultAlerts: Alert[] = [
    { id: '1', priority: 'P0', confidence: 0.92, tool: 'PentestGPT', time: '14:32:15' },
    { id: '2', priority: 'P1', confidence: 0.78, tool: 'ReconAI', time: '14:28:42' },
    { id: '3', priority: 'P2', confidence: 0.65, tool: 'AttackGPT', time: '14:25:08' },
    { id: '4', priority: 'P1', confidence: 0.72, tool: 'PentestGPT', time: '14:20:33' },
    { id: '5', priority: 'P3', confidence: 0.45, tool: 'Scanner', time: '14:15:19' },
  ]

  const displayAlerts = alerts?.slice(0, 5) || defaultAlerts

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h3 className="text-white text-lg mb-4">Recent AI Attack Events</h3>
      <div className="space-y-3">
        {displayAlerts.map((alert) => (
          <div
            key={alert.id}
            className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Tag color={priorityColors[alert.priority]}>{alert.priority}</Tag>
              <div className="text-white">
                <span className="font-medium">{alert.tool}</span>
                <span className="text-gray-400 ml-2">
                  {(alert.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            <span className="text-gray-400 text-sm">{alert.time}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
