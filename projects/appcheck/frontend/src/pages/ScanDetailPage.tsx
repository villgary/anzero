import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Table, Tag, Button, Spin, message, Row, Col, Statistic, Progress } from 'antd'
import { ArrowLeftOutlined, SafetyCertificateOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { scanApi } from '../api/scan'
import type { ScanResult } from '../api/scan'

export default function ScanDetailPage() {
  const { scan_id } = useParams<{ scan_id: string }>()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [loading, setLoading] = useState(true)
  const [scan, setScan] = useState<any>(null)
  const [results, setResults] = useState<ScanResult[]>([])

  useEffect(() => {
    loadData()
  }, [scan_id])

  const loadData = async () => {
    if (!scan_id) return
    setLoading(true)
    try {
      const [scanData, resultsData] = await Promise.all([
        scanApi.get(scan_id),
        scanApi.getResults(scan_id),
      ])
      setScan(scanData)
      setResults(resultsData.findings)
    } catch (error) {
      message.error(t('scans.detailLoadFailed'))
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'red',
      high: 'orange',
      medium: 'gold',
      low: 'green',
      info: 'blue',
    }
    return colors[severity] || 'default'
  }

  const getRiskProgress = (score: number) => {
    if (score >= 9) return { percent: 90, status: 'exception' as const }
    if (score >= 7) return { percent: 70, status: 'exception' as const }
    if (score >= 4) return { percent: 50, status: 'normal' as const }
    return { percent: 30, status: 'normal' as const }
  }

  const columns = [
    { title: t('results.severity'), dataIndex: 'severity', key: 'severity', render: (sev: string) => <Tag color={getSeverityColor(sev)}>{sev?.toUpperCase()}</Tag> },
    { title: t('results.title'), dataIndex: 'title', key: 'title' },
    { title: t('results.category'), dataIndex: 'category', key: 'category', render: (cat: string) => <Tag>{cat}</Tag> },
    { title: t('results.cvssScore'), dataIndex: 'cvss_score', key: 'cvss_score', render: (score: number) => score?.toFixed(1) || '-' },
    { title: t('results.description'), dataIndex: 'description', key: 'description', ellipsis: true },
    { title: t('results.remediation'), dataIndex: 'remediation', key: 'remediation', ellipsis: true },
  ]

  if (loading) return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/scans')} style={{ marginBottom: 16 }}>
        {t('common.back')}
      </Button>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title={t('scans.appName')}
              value={scan?.app_name}
              prefix={<SafetyCertificateOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title={t('scans.platform')}
              value={scan?.platform?.toUpperCase()}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title={t('scans.riskScore')}
              value={scan?.risk_score?.toFixed(1) || '0.0'}
              suffix="/ 10"
              valueStyle={{ color: scan?.risk_score >= 7 ? '#cf1322' : scan?.risk_score >= 4 ? '#faad14' : '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title={t('fileInfo.title')} style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title={t('fileInfo.fileSize')} value={scan?.file_size ? `${(scan.file_size / 1024 / 1024).toFixed(2)} MB` : '-'} />
          </Col>
          <Col span={6}>
            <Statistic title={t('fileInfo.md5')} value={scan?.file_md5 ? `${scan.file_md5.substring(0, 16)}...` : '-'} />
          </Col>
          <Col span={6}>
            <Statistic title={t('fileInfo.appVersion')} value={scan?.app_version || '-'} />
          </Col>
          <Col span={6}>
            <Statistic title={t('fileInfo.createdAt')} value={scan?.created_at ? new Date(scan.created_at).toLocaleString() : '-'} />
          </Col>
        </Row>
      </Card>

      <Card title={t('results.riskAssessment')} style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Statistic title={t('results.sdkCount')} value={scan?.sdk_count || 0} />
          </Col>
          <Col span={12}>
            <Statistic title={t('results.totalFindings')} value={results.length} />
          </Col>
        </Row>
        <Progress
          percent={getRiskProgress(scan?.risk_score || 0).percent}
          status={getRiskProgress(scan?.risk_score || 0).status}
          format={() => `${t('results.riskLevel')}: ${scan?.risk_score >= 7 ? 'HIGH' : scan?.risk_score >= 4 ? 'MEDIUM' : 'LOW'}`}
          style={{ marginTop: 16 }}
        />
      </Card>

      <Card title={t('results.title')}>
        <Table
          columns={columns}
          dataSource={results}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}
