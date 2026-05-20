import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Table, Tag } from 'antd'
import {
  ScanOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { apiClient } from '../api/client'
import ReactECharts from 'echarts-for-react'

interface ScanItem {
  id: string
  app_name: string
  platform: string
  status: string
  risk_score: number | null
  created_at: string
}

interface Stats {
  total: number
  completed: number
  in_progress: number
  failed: number
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<Stats>({ total: 0, completed: 0, in_progress: 0, failed: 0 })
  const [recentScans, setRecentScans] = useState<ScanItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [scansRes] = await Promise.all([
          apiClient.get('/scans?limit=5'),
        ])
        const scans = scansRes.data.items || []
        setRecentScans(scans)
        setStats({
          total: scansRes.data.total || 0,
          completed: scans.filter((s: ScanItem) => s.status === 'completed').length,
          in_progress: scans.filter((s: ScanItem) => ['pending', 'queued', 'scanning'].includes(s.status)).length,
          failed: scans.filter((s: ScanItem) => s.status === 'failed').length,
        })
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green'
      case 'failed': return 'red'
      case 'scanning': return 'processing'
      default: return 'default'
    }
  }

  const columns = [
    { title: t('scan.appName'), dataIndex: 'app_name', key: 'app_name' },
    { title: t('scan.platform'), dataIndex: 'platform', key: 'platform' },
    {
      title: t('scan.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag>
    },
    {
      title: t('scan.riskScore'),
      dataIndex: 'risk_score',
      key: 'risk_score',
      render: (score: number | null) => score ?? '-'
    },
  ]

  const pieOption = {
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 20, fontWeight: 'bold' }
      },
      labelLine: { show: false },
      data: [
        { value: stats.completed, name: t('dashboard.completedScans'), itemStyle: { color: '#52c41a' } },
        { value: stats.in_progress, name: t('dashboard.inProgressScans'), itemStyle: { color: '#1890ff' } },
        { value: stats.failed, name: t('dashboard.failedScans'), itemStyle: { color: '#ff4d4f' } },
      ],
    }],
  }

  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title={t('dashboard.totalScans')}
              value={stats.total}
              prefix={<ScanOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title={t('dashboard.completedScans')}
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title={t('dashboard.inProgressScans')}
              value={stats.in_progress}
              prefix={<SyncOutlined />}
              valueStyle={{ color: '#1890ff' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title={t('dashboard.failedScans')}
              value={stats.failed}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={16}>
          <Card title={t('dashboard.recentScans')}>
            <Table
              dataSource={recentScans}
              columns={columns}
              rowKey="id"
              pagination={false}
              loading={loading}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={t('dashboard.riskDistribution')}>
            <ReactECharts option={pieOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
