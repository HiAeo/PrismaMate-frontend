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

  // 全局登录/注册弹窗状态
  const showAuthDialog = ref(false)
  const authDialogTab = ref<'login' | 'register'>('login')

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
      // axios 拦截器返回完整 AxiosResponse，数据在 response.data 下
      const data = response.data
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      // 登录成功后获取用户信息（失败不阻断登录流程）
      try {
        await fetchUserInfo()
      } catch (e) {
        console.warn('获取用户信息失败，但登录 token 已获取', e)
      }
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
      const res = await getMe()
      user.value = res.data
    } catch (error: any) {
      const status = error?.response?.status
      if (status === 401) {
        // Token 过期或无效，静默清除登录状态（不在控制台抛错）
        token.value = null
        user.value = null
        usage.value = null
        localStorage.removeItem('token')
        return
      }
      // 其他错误（非 401）才完整退出
      logout()
    }
  }

  /**
   * 获取用户用量统计
   */
  async function fetchUsage(): Promise<void> {
    if (!token.value) return
    try {
      const res = await getUsage()
      usage.value = res.data
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

  // 初始化时获取用户信息（静默处理所有异常，避免控制台报错）
  if (token.value) {
    fetchUserInfo().catch(() => {})
  }

  return {
    token,
    user,
    usage,
    loading,
    isLoggedIn,
    showAuthDialog,
    authDialogTab,
    loginAction,
    registerAction,
    fetchUserInfo,
    fetchUsage,
    logout,
  }
})
