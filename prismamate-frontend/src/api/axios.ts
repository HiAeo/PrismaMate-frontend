import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 Axios 实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 管理员接口需要 X-Admin-ID 请求头
    const adminToken = localStorage.getItem('admin_token')
    if (adminToken && config.url?.startsWith('/superadmin')) {
      config.headers['X-Admin-ID'] = adminToken
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 对于 2xx 响应，直接返回完整 AxiosResponse，保留 response.data 供调用方使用
    return response
  },
  (error) => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401: {
          const url = error.config?.url || ''
          const isSilent = url.includes('/auth/me')

          // 管理员接口 401，清除 admin_token 并重定向到管理员登录页
          if (url.startsWith('/superadmin')) {
            localStorage.removeItem('admin_token')
            if (router.currentRoute.value.name !== 'AdminLogin') {
              ElMessage.error('管理员登录已过期，请重新登录')
              router.push({ name: 'AdminLogin', query: { redirect: router.currentRoute.value.fullPath } })
            }
            break
          }

          // 普通用户接口 401
          localStorage.removeItem('token')
          if (!isSilent && router.currentRoute.value.name !== 'Login' && router.currentRoute.value.name !== 'Register') {
            ElMessage.error('登录已过期，请重新登录')
            router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } })
          }
          break
        }
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('资源不存在')
          break
        case 422:
          // 验证错误
          const message = data.detail || '验证失败'
          ElMessage.error(Array.isArray(message) ? message[0] : message)
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }

    return Promise.reject(error)
  }
)

export default api
