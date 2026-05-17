/**
 * 品牌智库 API
 */
import api from './axios'

export interface BrandProfile {
  id: number
  user_id: number
  company_name: string
  brand_names: string[]
  website: string
  products: string
  description?: string
  keywords: string[]
  competitors: string[]
  created_at: string
  updated_at: string
}

export interface CreateBrandProfile {
  company_name: string
  brand_names: string[]
  website: string
  products: string
  description?: string
  keywords: string[]
  competitors?: string[]
}

export interface UpdateBrandProfile {
  company_name?: string
  brand_names?: string[]
  website?: string
  products?: string
  description?: string
  keywords?: string[]
  competitors?: string[]
}

export const brandHubApi = {
  /**
   * 创建品牌档案
   */
  create(data: CreateBrandProfile) {
    return api.post<BrandProfile>('/brand-hub', data)
  },

  /**
   * 获取当前用户的所有品牌档案
   */
  list() {
    return api.get<BrandProfile[]>('/brand-hub')
  },

  /**
   * 获取单个品牌档案详情
   */
  get(id: number) {
    return api.get<BrandProfile>(`/brand-hub/${id}`)
  },

  /**
   * 更新品牌档案
   */
  update(id: number, data: UpdateBrandProfile) {
    return api.put<BrandProfile>(`/brand-hub/${id}`, data)
  },

  /**
   * 删除品牌档案
   */
  delete(id: number) {
    return api.delete(`/brand-hub/${id}`)
  }
}
