<template>
  <el-dialog
    v-model="visible"
    :title="activeTab === 'login' ? '登录 PrismaMate 棱镜' : '注册 PrismaMate 棱镜'"
    width="420px"
    :close-on-click-modal="false"
    :modal-class="'auth-dialog-overlay'"
    @closed="reset"
  >
    <!-- 登录表单 -->
    <template v-if="activeTab === 'login'">
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top">
        <el-form-item label="邮箱 / 用户名" prop="emailOrUsername">
          <el-input
            v-model="loginForm.emailOrUsername"
            placeholder="请输入邮箱或用户名"
            size="large"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="dialog-footer">
        还没有账号？<el-link type="primary" @click="activeTab = 'register'">立即注册</el-link>
      </div>
    </template>

    <!-- 注册表单 -->
    <template v-else>
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-position="top">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" size="large" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名（3-50个字符）" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            size="large"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="dialog-footer">
        已有账号？<el-link type="primary" @click="activeTab = 'login'">立即登录</el-link>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const visible = ref(false)
const activeTab = ref<'login' | 'register'>('login')
const loading = ref(false)
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

const loginForm = reactive({ emailOrUsername: '', password: '' })
const registerForm = reactive({ email: '', username: '', password: '', confirmPassword: '' })

const loginRules = {
  emailOrUsername: [{ required: true, message: '请输入邮箱或用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

function open(tab: 'login' | 'register' = 'login') {
  activeTab.value = tab
  visible.value = true
}

function reset() {
  loginForm.emailOrUsername = ''
  loginForm.password = ''
  registerForm.email = ''
  registerForm.username = ''
  registerForm.password = ''
  registerForm.confirmPassword = ''
  loginFormRef.value?.resetFields()
  registerFormRef.value?.resetFields()
}

async function handleLogin() {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.loginAction(loginForm.emailOrUsername, loginForm.password)
    // 确保响应式状态已更新
    await nextTick()
    if (!userStore.isLoggedIn) {
      ElMessage.error('登录状态异常，请重试')
      return
    }

    // 检测到 admin 用户，自动跳转到管理员登录页
    const isAdminUsername = loginForm.emailOrUsername.toLowerCase() === 'admin'
    if (isAdminUsername) {
      visible.value = false
      ElMessage.info('检测到管理员账号，正在跳转...')
      // 清除普通用户状态
      userStore.logout()
      // 跳转到管理员登录页
      setTimeout(() => {
        window.location.href = '/admin/login'
      }, 300)
      return
    }

    ElMessage.success('登录成功')
    visible.value = false
    // 登录成功后跳转：优先使用 redirect 参数，否则默认 dashboard
    const redirect = router.currentRoute.value.query.redirect as string
    await router.push(redirect || '/brand-hub')
  } catch (error: any) {
    ElMessage.error(error?.detail || error?.response?.data?.detail || '登录失败，请检查邮箱/用户名和密码')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.registerAction(registerForm.email, registerForm.username, registerForm.password)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    registerFormRef.value?.resetFields()
  } catch (error: any) {
    ElMessage.error(error?.detail || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>

<style scoped>
.dialog-footer {
  text-align: center;
  margin-top: var(--spacing-md);
  color: var(--muted);
}
</style>
