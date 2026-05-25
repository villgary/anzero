import ReactECharts from 'echarts-for-react'

interface ToolDistributionChartProps {
  data?: {
    name: string
    value: number
  }[]
}

export function ToolDistributionChart({ data }: ToolDistributionChartProps) {
  // Default data for demo
  const defaultData = [
    { name: 'PentestGPT', value: 42 },
    { name: 'ReconAI', value: 28 },
    { name: 'AttackGPT', value: 15 },
    { name: 'Other', value: 15 },
  ]

  const chartData = data || defaultData

  const option = {
    title: {
      text: 'Attack Tools Distribution',
      textStyle: { color: '#fff', fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(31, 41, 55, 0.95)',
      borderColor: '#4b5563',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#9ca3af' },
      itemWidth: 12,
      itemHeight: 12
    },
    series: [
      {
        name: 'Tools',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#1f2937',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#fff'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: chartData.map((item, index) => ({
          ...item,
          itemStyle: {
            color: ['#ef4444', '#f97316', '#eab308', '#22c55e'][index % 4]
          }
        }))
      }
    ]
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
