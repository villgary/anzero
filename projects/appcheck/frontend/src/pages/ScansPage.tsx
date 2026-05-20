import { useState, useEffect } from 'react'
import { Table, Button, Tag, Upload, message, Modal, Form, Input, Popconfirm } from 'antd'
import { PlusOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { scanApi } from '../api/scan'
import type { ScanJob } from '../api/scan'

const { Dragger } = Upload

export default function ScansPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [scans, setScans] = useState<ScanJob[]>([])
  const [loading, setLoading] = useState(false)
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [form] = Form.useForm()

  const loadScans = async () => {
    setLoading(true)
    try {
      const data = await scanApi.list()
      setScans(data.items)
    } catch (error) {
      message.error(t('scans.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadScans()
  }, [])

  const handleUpload = async (values: { app_name: string; app_version?: string }) => {
    const file = (await new Promise<File | null>((resolve) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.apk,.ipa,.hap'
      input.onchange = () => resolve(input.files?.[0] || null)
      input.click()
    })) as File | null

    if (!file) return

    setUploading(true)
    try {
      await scanApi.upload(file, values.app_name, values.app_version)
      message.success(t('scans.uploadSuccess'))
      setUploadModalOpen(false)
      form.resetFields()
      loadScans()
    } catch (error: any) {
      message.error(error.message || t('scans.uploadFailed'))
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await scanApi.delete(id)
      message.success(t('scans.deleteSuccess'))
      loadScans()
    } catch (error) {
      message.error(t('scans.deleteFailed'))
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'default',
      scanning: 'processing',
      completed: 'success',
      failed: 'error',
    }
    return colors[status] || 'default'
  }

  const columns = [
    { title: t('scans.appName'), dataIndex: 'app_name', key: 'app_name' },
    { title: t('scans.platform'), dataIndex: 'platform', key: 'platform' },
    { title: t('scans.status'), dataIndex: 'status', key: 'status', render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag> },
    { title: t('scans.riskScore'), dataIndex: 'risk_score', key: 'risk_score', render: (score: number) => score?.toFixed(1) || '-' },
    { title: t('scans.createdAt'), dataIndex: 'created_at', key: 'created_at', render: (date: string) => date ? new Date(date).toLocaleString() : '-' },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_: any, record: ScanJob) => (
        <div style={{ display: 'flex', gap: 8 }}>
          <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/scans/${record.id}`)} />
          <Popconfirm title={t('scans.confirmDelete')} onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </div>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>{t('scans.title')}</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setUploadModalOpen(true)}>
          {t('scans.upload')}
        </Button>
      </div>
      <Table columns={columns} dataSource={scans} rowKey="id" loading={loading} />

      <Modal title={t('scans.uploadNew')} open={uploadModalOpen} onCancel={() => setUploadModalOpen(false)} footer={null}>
        <Form form={form} onFinish={handleUpload} layout="vertical">
          <Form.Item name="app_name" label={t('scans.appName')} rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="app_version" label={t('scans.appVersion')}>
            <Input />
          </Form.Item>
          <Form.Item label={t('scans.selectFile')}>
            <Dragger accept=".apk,.ipa,.hap" beforeUpload={() => false} showUploadList={false}>
              <p className="ant-upload-drag-icon"><PlusOutlined /></p>
              <p className="ant-upload-text">{t('scans.dragUpload')}</p>
            </Dragger>
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={uploading} block>{t('scans.upload')}</Button>
        </Form>
      </Modal>
    </div>
  )
}
