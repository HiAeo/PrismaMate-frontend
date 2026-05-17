<template>
  <div class="admin-login-container">
    <div class="login-card">
      <div class="card-header">
        <el-icon class="admin-icon"><Setting /></el-icon>
        <span>超级管理员登录</span>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" @submit.prevent="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入管理员用户名" :prefix-icon="User" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">登录</el-button>
        </el-form-item>

        <div class="tip-text">
          <el-alert type="info" :closable="false" show-icon>
            <template #title>默认账号：admin / admin123</template>
          </el-alert>
        </div>
      </el-form>
    </div>

    <div class="back-link">
      <el-link type="primary" @click="$router.push('/home')">
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </el-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Setting, ArrowLeft } from '@element-plus/icons-vue'
import { adminLogin } from '@/api/admin'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res: any = await adminLogin(form.username, form.password)
    const data = res.data
    if (data.success) {
      localStorage.setItem('admin_token', data.token)
      localStorage.setItem('admin_info', JSON.stringify(data.admin))
      ElMessage.success('登录成功')
      window.location.href = '/admin/dashboard'
      return
    } else {
      ElMessage.error(data.message || '登录失败')
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0F0F0F;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 32px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 24px;
}

.admin-icon {
  font-size: 24px;
  color: #3B82F6;
}

.login-btn {
  width: 100%;
  height: 42px;
  background: #3B82F6;
  border-color: #3B82F6;
  border-radius: 8px;
  font-size: 15px;
}

.login-btn:hover {
  background: #2563EB;
  border-color: #2563EB;
}

.tip-text {
  margin-top: 16px;
}

.back-link {
  margin-top: 24px;
}

.back-link .el-link {
  color: #9CA3AF;
}

.back-link .el-link:hover {
  color: #FFFFFF;
}
</style>
