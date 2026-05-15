<template>
  <div class="home">
    <!-- 导航栏 -->
    <el-menu mode="horizontal" :ellipsis="false">
      <el-menu-item index="0">
        <el-icon><Monitor /></el-icon>
        <span>PrismaMate 棱镜</span>
      </el-menu-item>
      <div class="flex-grow" />
      <el-menu-item v-if="!userStore.isLoggedIn" index="1" @click="$router.push('/login')">
        登录
      </el-menu-item>
      <el-menu-item v-if="!userStore.isLoggedIn" index="2" @click="$router.push('/register')">
        注册
      </el-menu-item>
      <el-menu-item v-if="userStore.isLoggedIn" index="3" @click="$router.push('/detection')">
        创建检测
      </el-menu-item>
      <el-menu-item v-if="userStore.isLoggedIn" index="4" @click="$router.push('/reports')">
        报告列表
      </el-menu-item>
      <el-menu-item v-if="userStore.isLoggedIn" index="5" @click="$router.push('/profile')">
        {{ userStore.user?.email }}
      </el-menu-item>
    </el-menu>

    <!-- 主页内容 -->
    <div class="hero">
      <h1>独立的第三方 GEO 效果检测认证平台</h1>
      <p class="subtitle">检测品牌在 AI 搜索中的真实表现，生成标准化、可溯源、不可篡改的检测报告</p>
      
      <div class="actions">
        <el-button type="primary" size="large" @click="$router.push('/detect')">
          <el-icon><Search /></el-icon>
          快速检测
        </el-button>
        <el-button type="info" size="large" @click="$router.push('/verify')">
          <el-icon><Stamp /></el-icon>
          验证报告
        </el-button>
        <el-button v-if="userStore.isLoggedIn" type="default" size="large" @click="$router.push('/detection')">
          创建检测任务
        </el-button>
        <el-button v-if="!userStore.isLoggedIn" type="default" size="large" @click="$router.push('/register')">
          注册账号
        </el-button>
      </div>
    </div>

    <!-- 功能特性 -->
    <div class="features">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon size="24"><DataAnalysis /></el-icon>
                <span>AI 平台覆盖</span>
              </div>
            </template>
            <p>支持 DeepSeek、豆包、Kimi 等主流 AI 平台的全量检测</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon size="24"><Document /></el-icon>
                <span>标准化报告</span>
              </div>
            </template>
            <p>生成专业级检测报告，包含品牌提及率、引用位次、信源分析</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon size="24"><Stamp /></el-icon>
                <span>防篡改验证</span>
              </div>
            </template>
            <p>报告哈希值验证，确保数据完整性，报告真实可信</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 底部 -->
    <footer>
      <p>© 2026 PrismaMate 棱镜 - GEO 效果检测平台</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { Monitor, Search, DataAnalysis, Document, Stamp } from '@element-plus/icons-vue'

const userStore = useUserStore()
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.flex-grow {
  flex-grow: 1;
}

.hero {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 80px 20px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.hero .subtitle {
  font-size: 20px;
  opacity: 0.9;
  max-width: 600px;
  margin-bottom: 40px;
}

.actions {
  display: flex;
  gap: 20px;
}

.features {
  padding: 60px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.features .card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

footer {
  padding: 20px;
  text-align: center;
  color: #666;
  border-top: 1px solid #eee;
}
</style>
