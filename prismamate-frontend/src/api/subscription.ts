import api from './axios'

// 订阅管理 API

// 获取当前套餐详情
export const getMyPlan = () => {
  return api.get('/subscription/my-plan')
}

// 获取所有套餐列表
export const getPlans = () => {
  return api.get('/subscription/plans', { params: { _t: Date.now() } })
}

// 升级套餐
export const upgradePlan = (planId: string) => {
  return api.post('/subscription/upgrade', { plan_id: planId })
}

// 获取积分流水
export const getPointsHistory = (limit: number = 50) => {
  return api.get('/subscription/points-history', { params: { limit } })
}

// 积分充值
export const purchasePoints = (pointsAmount: number) => {
  return api.post('/subscription/purchase-points', { points_amount: pointsAmount })
}

// 获取订阅记录
export const getMySubscriptions = () => {
  return api.get('/subscription/my-subscriptions')
}
