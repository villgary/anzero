import ReactECharts from 'echarts-for-react'

interface AttackSourceMapProps {
  data?: {
    name: string
    value: number
    coords: [number, number]
  }[]
}

export function AttackSourceMap({ data }: AttackSourceMapProps) {
  // Default data for demo - major attack sources
  const defaultData = [
    { name: 'Beijing', value: 350, coords: [116.4, 39.9] },
    { name: 'Shanghai', value: 280, coords: [121.4, 31.2] },
    { name: 'Shenzhen', value: 220, coords: [114.1, 22.5] },
    { name: 'Hangzhou', value: 180, coords: [120.2, 30.3] },
    { name: 'Chengdu', value: 150, coords: [104.1, 30.7] },
    { name: 'US-East', value: 120, coords: [-73.9, 40.7] },
    { name: 'Russia', value: 95, coords: [37.6, 55.8] },
    { name: 'Germany', value: 75, coords: [13.4, 52.5] },
  ]

  const chartData = data || defaultData

  const option = {
    title: {
      text: 'Attack Source Geography',
      textStyle: { color: '#fff', fontSize: 14 },
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(31, 41, 55, 0.95)',
      borderColor: '#4b5563',
      textStyle: { color: '#fff' },
      formatter: (params: any) => `${params.data.name}: ${params.data.value} attacks`
    },
    geo: {
      map: 'world',
      roam: true,
      scaleLimit: {
        min: 1,
        max: 10
      },
      zoom: 1.2,
      center: [0, 20],
      itemStyle: {
        areaColor: '#1e3a5f',
        borderColor: '#4b5563',
        borderWidth: 1
      },
      emphasis: {
        itemStyle: {
          areaColor: '#2563eb'
        },
        label: {
          show: false
        }
      },
      nameMap: {
        'China': 'China',
        'United States': 'US'
      }
    },
    series: [
      {
        name: 'Attacks',
        type: 'scatter',
        coordinateSystem: 'geo',
        data: chartData.map(item => ({
          name: item.name,
          value: [...item.coords, item.value]
        })),
        symbolSize: (val: number[]) => Math.sqrt(val[2]) * 2,
        itemStyle: {
          color: '#ef4444',
          shadowBlur: 10,
          shadowColor: 'rgba(239, 68, 68, 0.5)'
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            position: 'right',
            formatter: (params: any) => `${params.data.name}: ${params.data.value[2]}`,
            color: '#fff'
          }
        }
      }
    ]
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
