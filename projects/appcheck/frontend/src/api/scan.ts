import { apiClient } from './client'

export interface ScanJob {
  id: string
  app_name: string
  app_version?: string
  platform: string
  file_size: number
  file_md5: string
  status: string
  risk_score?: number
  sdk_count?: number
  error_message?: string
  created_at?: string
  completed_at?: string
}

export interface ScanResult {
  id: string
  category: string
  severity: string
  cvss_score?: number
  cwe_id?: string
  title: string
  description: string
  remediation: string
}

interface ListResponse {
  total: number
  items: ScanJob[]
}

interface ResultsResponse {
  scan_id: string
  risk_score?: number
  sdk_count?: number
  total_findings: number
  findings: ScanResult[]
}

export const scanApi = {
  list: async (skip = 0, limit = 20): Promise<ListResponse> => {
    const { data } = await apiClient.get('/scans', { params: { skip, limit } })
    return data
  },

  get: async (id: string): Promise<ScanJob> => {
    const { data } = await apiClient.get(`/scans/${id}`)
    return data
  },

  getResults: async (id: string): Promise<ResultsResponse> => {
    const { data } = await apiClient.get(`/scans/${id}/results`)
    return data
  },

  upload: async (file: File, appName: string, appVersion?: string): Promise<ScanJob> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('app_name', appName)
    if (appVersion) formData.append('app_version', appVersion)

    const { data } = await apiClient.post('/scans/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/scans/${id}`)
  },
}
