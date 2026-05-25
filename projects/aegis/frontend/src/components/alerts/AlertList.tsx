import { Tag } from 'antd'

interface Alert {
  id: string
  priority: 'P0' | 'P1' | 'P2' | 'P3'
  confidence: number
  tool: string
  time: string
}

const priorityColors = { P0: 'red', P1: 'orange', P2: 'yellow', P3: 'blue' }

export function AlertList({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="space-y-3">
      {alerts.map(alert => (
        <div key={alert.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <Tag color={priorityColors[alert.priority]}>{alert.priority}</Tag>
            <span className="text-gray-400 text-sm">{alert.time}</span>
          </div>
          <div className="mt-2 text-white">
            Confidence: {(alert.confidence * 100).toFixed(0)}% | Tool: {alert.tool}
          </div>
        </div>
      ))}
    </div>
  )
}