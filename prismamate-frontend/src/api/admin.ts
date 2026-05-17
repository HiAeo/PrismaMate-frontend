import api from './axios'

// 管理员 API

// 管理员登录
export const adminLogin = (username: string, password: string) => {
  return api.post('/superadmin/login', { username, password })
}

// 获取仪表盘数据
export const getDashboardStats = () => {
  return api.get('/superadmin/dashboard')
}

// 获取用户列表
export const getAdminUsers = (params: {
  search?: string
  plan_id?: string
  is_active?: boolean
  page?: number
  page_size?: number
}) => {
  return api.get('/superadmin/users', { params })
}

// 获取用户详情
export const getAdminUserDetail = (userId: string) => {
  return api.get(`/superadmin/users/${userId}`)
}

// 调整用户积分
export const adjustUserPoints = (
  userId: string,
  amount: number,
  reason: string
) => {
  return api.post(`/superadmin/users/${userId}/points`, { amount, reason })
}

// 调整用户套餐
export const adjustUserPlan = (userId: string, planId: string) => {
  return api.post(`/superadmin/users/${userId}/plan`, { plan_id: planId })
}

// 封禁/解封用户
export const toggleUserBan = (userId: string, ban: boolean) => {
  return api.post(`/superadmin/users/${userId}/ban`, { ban })
}

// 获取订阅记录
export const getSubscriptions = (params?: { page?: number; page_size?: number }) => {
  return api.get('/superadmin/subscriptions', { params })
}

// 获取积分流水
export const getPointsTransactions = (params?: { page?: number; page_size?: number }) => {
  return api.get('/superadmin/points-transactions', { params })
}

// 获取套餐列表
export const getPlans = () => {
  return api.get('/superadmin/plans')
}

// 更新套餐
export const updatePlan = (planId: string, updates: object) => {
  return api.put(`/superadmin/plans/${planId}`, updates)
}
