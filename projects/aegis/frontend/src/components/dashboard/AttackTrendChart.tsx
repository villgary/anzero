import ReactECharts from 'echarts-for-react'

interface AttackTrendChartProps {
  data?: {
    month: string
    attacks: number
  }[]
}

export function AttackTrendChart({ data }: AttackTrendChartProps) {
  // Default data for demo
  const defaultData = [
    { month: 'Jan', attacks: 45 },
    { month: 'Feb', attacks: 52 },
    { month: 'Mar', attacks: 38 },
    { month: 'Apr', attacks: 67 },
    { month: 'May', attacks: 89 },
    { month: 'Jun', attacks: 73 },
    { month: 'Jul', attacks: 95 },
    { month: 'Aug', attacks: 82 },
    { month: 'Sep', attacks: 110 },
    { month: 'Oct', attacks: 98 },
    { month: 'Nov', attacks: 125 },
    { month: 'Dec', attacks: 127 },
  ]

  const chartData = data || defaultData

  const option = {
    title: {
      text: 'Attack Trend (12 months)',
      textStyle: { color: '#fff', fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(31, 41, 55, 0.95)',
      borderColor: '#4b5563',
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.map(d => d.month),
      axisLine: { lineStyle: { color: '#4b5563' } },
      axisLabel: { color: '#9ca3af' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#4b5563' } },
      axisLabel: { color: '#9ca3af' },
      splitLine: { lineStyle: { color: '#374151' } }
    },
    series: [
      {
        name: 'Attacks',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#ef4444', width: 2 },
        itemStyle: { color: '#ef4444' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(239, 68, 68, 0.4)' },
              { offset: 1, color: 'rgba(239, 68, 68, 0.05)' }
            ]
          }
        },
        data: chartData.map(d => d.attacks)
      }
    ]
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}
