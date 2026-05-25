import ReactECharts from 'echarts-for-react'

interface AttackSourceMapProps {
  data?: {
    name: string
    value: number
  }[]
}

export function AttackSourceMap({ data }: AttackSourceMapProps) {
  // Default data for demo - top attack sources
  const defaultData = [
    { name: 'Beijing', value: 350 },
    { name: 'Shanghai', value: 280 },
    { name: 'Shenzhen', value: 220 },
    { name: 'Hangzhou', value: 180 },
    { name: 'Chengdu', value: 150 },
    { name: 'US-East', value: 120 },
    { name: 'Russia', value: 95 },
    { name: 'Germany', value: 75 },
  ]

  const chartData = data || defaultData

  const option = {
    title: {
      text: 'Attack Source Distribution',
      textStyle: { color: '#fff', fontSize: 14 },
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(31, 41, 55, 0.95)',
      borderColor: '#4b5563',
      textStyle: { color: '#fff' }
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => item.name),
      axisLabel: {
        color: '#9ca3af',
        rotate: 45
      },
      axisLine: {
        lineStyle: { color: '#4b5563' }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#9ca3af' },
      axisLine: { lineStyle: { color: '#4b5563' } },
      splitLine: { lineStyle: { color: '#374151' } }
    },
    series: [
      {
        name: 'Attacks',
        type: 'bar',
        data: chartData.map(item => item.value),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#ef4444' },
              { offset: 1, color: '#991b1b' }
            ]
          },
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '60%'
      }
    ],
    grid: {
      left: 50,
      right: 20,
      bottom: 60,
      top: 40
    }
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
