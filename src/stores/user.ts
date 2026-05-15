import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getMe, getUsage, UserInfo } from '@/api/auth'
import { ElMessage } from 'element-plus'

export interface UsageStats {
  total_tasks: number
  completed_tasks: number
  total_reports: number
  total_mentions: number
  total_detections: number
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)
  const usage = ref<UsageStats | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  /**
   * 判断字符串是否为邮箱格式
   */
  function isEmail(str: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str)
  }

  /**
   * 用户登录
   */
  async function loginAction(emailOrUsername: string, password: string): Promise<void> {
    loading.value = true
    try {
      const response = isEmail(emailOrUsername)
        ? await login(emailOrUsername, password)
        : await login(emailOrUsername, password, true)
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      // 登录成功后获取用户信息
      await fetchUserInfo()
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户注册
   */
  async function registerAction(email: string, username: string, password: string): Promise<void> {
    loading.value = true
    try {
      await register(email, username, password)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchUserInfo(): Promise<void> {
    if (!token.value) return
    try {
      user.value = await getMe()
    } catch {
      // Token 过期，清除登录状态
      logout()
    }
  }

  /**
   * 获取用户用量统计
   */
  async function fetchUsage(): Promise<void> {
    if (!token.value) return
    try {
      usage.value = await getUsage()
    } catch {
      // 忽略错误
    }
  }

  /**
   * 退出登录
   */
  function logout(): void {
    token.value = null
    user.value = null
    usage.value = null
    localStorage.removeItem('token')
    ElMessage.success('已退出登录')
  }

  // 初始化时获取用户信息
  if (token.value) {
    fetchUserInfo()
  }

  return {
    token,
    user,
    usage,
    loading,
    isLoggedIn,
    loginAction,
    registerAction,
    fetchUserInfo,
    fetchUsage,
    logout,
  }
})
