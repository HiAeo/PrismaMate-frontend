<template>
  <div class="profile-container">
    <el-page-header @back="$router.push('/home')" content="用户中心" />
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>账户信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="邮箱">{{ userStore.user?.email }}</el-descriptions-item>
            <el-descriptions-item label="公司">
              {{ userStore.user?.company_name || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              {{ userStore.user?.role === 'client' ? '品牌方' : userStore.user?.role }}
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ formatDate(userStore.user?.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>用量统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value">{{ usage.total_tasks }}</div>
                <div class="stat-label">总任务数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value">{{ usage.completed_tasks }}</div>
                <div class="stat-label">已完成任务</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value">{{ usage.total_reports }}</div>
                <div class="stat-label">生成报告</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>操作</span>
          </template>
          <el-button type="primary" @click="$router.push('/detection')">创建检测任务</el-button>
          <el-button @click="$router.push('/reports')">查看报告</el-button>
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api/axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const usage = ref({
  total_tasks: 0,
  completed_tasks: 0,
  total_reports: 0,
})

async function fetchUsage() {
  try {
    const data = await api.get('/user/usage')
    usage.value = data
  } catch {
    // ignore
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/home')
}

onMounted(fetchUsage)
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  margin-top: 10px;
  color: #666;
}
</style>
