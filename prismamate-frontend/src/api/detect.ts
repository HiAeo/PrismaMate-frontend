/**
 * 检测 API
 */
import api from './axios'

export interface DetectionRequest {
  keywords: string[]
  brands?: string[]
  platform: string
}

export interface BrandMention {
  brand_name: string
  canonical_name: string
  context: string
  sentiment: string
}

export interface ReportResponse {
  report_id: string
  verification_code: string
  report_hash: string
  detection_time: string
  total_mentions: number
  brand_mentions: BrandMention[]
  total_citations: number
  keywords: string[]
  platforms: string[]
  report_html: string
  user_id?: string
  task_id?: string
}

export const detectApi = {
  /**
   * 执行品牌检测
   */
  detect(data: DetectionRequest) {
    return api.post<ReportResponse>('/detect/detect', data)
  },

  /**
   * 获取默认品牌列表
   */
  getBrands() {
    return api.get<{ brands: string[] }>('/detect/brands')
  },

  /**
   * 获取支持的平台列表
   */
  getPlatforms() {
    return api.get<{ platforms: Record<string, any> }>('/detect/platforms')
  },

  /**
   * 健康检查
   */
  healthCheck() {
    return api.get('/detect/health')
  }
}
