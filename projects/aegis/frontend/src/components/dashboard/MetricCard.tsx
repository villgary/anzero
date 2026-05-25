import { Card } from 'antd'

interface MetricCardProps {
  title: string
  value: string | number
  trend?: { value: number; direction: 'up' | 'down' }
  color?: string
}

export function MetricCard({ title, value, trend, color }: MetricCardProps) {
  return (
    <Card className="bg-gray-800 border-gray-700">
      <div className="text-gray-400 text-sm">{title}</div>
      <div className="text-3xl font-bold text-white mt-2">{value}</div>
      {trend && (
        <div className={`text-sm mt-2 ${trend.direction === 'up' ? 'text-red-400' : 'text-green-400'}`}>
          {trend.direction === 'up' ? '↑' : '↓'} {Math.abs(trend.value)}%
        </div>
      )}
    </Card>
  )
}