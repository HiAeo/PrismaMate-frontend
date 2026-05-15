<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <el-icon><Monitor /></el-icon>
          <span>登录 PrismaMate 棱镜</span>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="邮箱 / 用户名" prop="emailOrUsername">
          <el-input 
            v-model="form.emailOrUsername" 
            placeholder="请输入邮箱或用户名" 
            size="large" 
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            size="large" 
            show-password 
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            style="width: 100%" 
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="footer">
        还没有账号？<el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
      </div>
      
      <el-divider />
      
      <div class="quick-links">
        <el-button text @click="$router.push('/detect')">
          跳过登录，直接使用快速检测
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  emailOrUsername: '',
  password: '',
})

const rules = {
  emailOrUsername: [
    { required: true, message: '请输入邮箱或用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.loginAction(form.emailOrUsername, form.password)
    ElMessage.success('登录成功')
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/home')
  } catch (error: any) {
    ElMessage.error(error?.detail || '登录失败，请检查邮箱/用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
}

.footer {
  text-align: center;
  margin-top: 20px;
}

.quick-links {
  text-align: center;
}
</style>
