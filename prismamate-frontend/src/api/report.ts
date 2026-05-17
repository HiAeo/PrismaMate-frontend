import api from './axios'

export interface Report {
  id: number
  report_id: string
  task_id: number
  report_hash: string
  pdf_url?: string
  verification_code: string
  created_at: string
  blockchain_tx_id?: string
  blockchain_status?: string
}

export interface VerifyResult {
  is_valid: boolean
  report_id: string
  brand_names: string[]
  keywords: string[]
  platforms: string[]
  detection_time: string
  report_hash: string
  message: string
}

export function createReport(taskId: number) {
  return api.post('/reports', { task_id: taskId })
}

export function getReport(reportId: string) {
  return api.get(`/reports/${reportId}`)
}

export function verifyReport(code: string) {
  return api.get(`/reports/verify/${code}`)
}

export function listReports(skip = 0, limit = 20) {
  return api.get('/reports', { params: { skip, limit } })
}

// 获取报告列表（兼容别名）
export const getReports = (skip = 0, limit = 50) => listReports(skip, limit)
