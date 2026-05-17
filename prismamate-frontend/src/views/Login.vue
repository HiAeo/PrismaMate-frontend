<template>
  <PublicLayout>
    <div class="login-wrapper">
      <el-card class="login-card">
        <div class="auth-redirect">
          <p class="auth-tip">正在打开登录窗口...</p>
          <el-button type="primary" size="large" @click="openDialog">
            登录 / 注册
          </el-button>
          <div class="back-home">
            <el-link type="info" @click="$router.push('/home')">返回首页</el-link>
          </div>
        </div>
      </el-card>
    </div>
  </PublicLayout>
</template>

<script setup lang="ts">
import { onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import PublicLayout from '@/components/PublicLayout.vue'

const router = useRouter()
const userStore = useUserStore()

function openDialog() {
  userStore.authDialogTab = 'login'
  userStore.showAuthDialog = true
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    router.replace('/brand-hub')
  } else {
    nextTick(() => {
      openDialog()
    })
  }
})
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
  background: var(--background);
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.auth-redirect {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
}

.auth-tip {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.back-home {
  margin-top: 8px;
}
</style>
