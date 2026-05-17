<template>
  <Layout>
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>PrismaMate 棱镜管理后台</h1>
      <p class="subtitle">系统数据概览</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users">
          <el-icon :size="20"><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon detections">
          <el-icon :size="20"><Search /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.today_detections || 0 }}</div>
          <div class="stat-label">今日检测</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon paid">
          <el-icon :size="20"><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ stats.mrr || 0 }}</div>
          <div class="stat-label">MRR</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rate">
          <el-icon :size="20"><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.paid_rate || 0 }}%</div>
          <div class="stat-label">付费率</div>
        </div>
      </div>
    </div>

    <!-- 套餐分布 -->
    <div class="card">
      <div class="card-title flex-between">
        <span>套餐分布</span>
        <span class="card-total">{{ stats.total_users || 0 }} 人</span>
      </div>
      <div class="plan-grid">
        <div
          v-for="(item, key) in stats.plan_distribution"
          :key="key"
          class="plan-item"
        >
          <div class="plan-top">
            <span class="plan-name">{{ item.name }}</span>
            <span class="plan-pct">{{ getPlanPercentage(item.count) }}%</span>
          </div>
          <div class="plan-count">{{ item.count }} 人</div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: getPlanPercentage(item.count) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时数据 -->
    <div class="card">
      <div class="card-title flex-between">
        <span>实时数据</span>
        <a class="link-text" @click="loadStats">
          <el-icon :size="12"><Refresh /></el-icon>
          刷新
        </a>
      </div>
      <div class="data-grid">
        <div class="data-item">
          <div class="data-value">{{ stats.today_new_users || 0 }}</div>
          <div class="data-label">今日新增用户</div>
        </div>
        <div class="data-item">
          <div class="data-value">{{ stats.active_users || 0 }}</div>
          <div class="data-label">活跃用户</div>
        </div>
        <div class="data-item">
          <div class="data-value">{{ stats.total_detections || 0 }}</div>
          <div class="data-label">总检测次数</div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Search, Money, TrendCharts, Refresh } from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/admin'
import Layout from '@/components/Layout.vue'

const stats = reactive<any>({})

const loadStats = async () => {
  try {
    const res: any = await getDashboardStats()
    const data = res.data
    if (data.status === 'ok') {
      Object.assign(stats, data)
    }
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

const getPlanPercentage = (count: number) => {
  if (!stats.total_users) return 0
  return Math.round((count / stats.total_users) * 100)
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
/* 页面头部 */
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 22px; font-weight: 600; color: #FFFFFF; margin: 0 0 8px 0; line-height: 1.3; }
.subtitle { font-size: 14px; color: #9CA3AF; margin: 0; }

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 18px 20px;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}
.stat-card:hover {
  border-color: #3B82F6;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-icon.users { color: #3B82F6; background: rgba(59, 130, 246, 0.12); }
.stat-icon.detections { color: #1783FF; background: rgba(23, 131, 255, 0.12); }
.stat-icon.paid { color: #F59E0B; background: rgba(245, 158, 11, 0.12); }
.stat-icon.rate { color: #10B981; background: rgba(16, 185, 129, 0.12); }

.stat-value { font-size: 22px; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; line-height: 1.2; }
.stat-label { font-size: 13px; color: #9CA3AF; }

/* 通用卡片 */
.card {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  transition: border-color 0.25s ease;
}
.card:hover { border-color: #3B82F6; }
.card:last-child { margin-bottom: 0; }

.card-title {
  font-size: 15px;
  font-weight: 500;
  color: #E5E5E5;
  margin-bottom: 20px;
}
.card-title.flex-between { display: flex; justify-content: space-between; align-items: center; }

.card-total { font-size: 13px; color: #9CA3AF; font-weight: 400; }

/* 套餐分布 - 三列并排 */
.plan-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.plan-item {
  background: #141414;
  border: 1px solid #2A2A2A;
  border-radius: 10px;
  padding: 18px 20px;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}
.plan-item:hover {
  border-color: #3B82F6;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.12);
}

.plan-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.plan-name { font-size: 14px; font-weight: 500; color: #E5E5E5; }
.plan-pct { font-size: 18px; font-weight: 700; color: #3B82F6; }
.plan-count { font-size: 13px; color: #9CA3AF; margin-bottom: 12px; }

.progress-bar {
  height: 4px;
  background: #2D2D2D;
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3B82F6, #1783FF);
  border-radius: 2px;
  transition: width 0.6s ease;
}

/* 通用按钮 hover 交互 */
:deep(.el-button) {
  border-color: #2D2D2D;
  background: #1A1A1A;
  color: #D1D5DB;
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}
:deep(.el-button:hover),
:deep(.el-button:focus) {
  border-color: #3B82F6;
  color: #FFFFFF;
  background: #1A1A1A;
}
:deep(.el-button--primary) {
  border-color: #3B82F6;
  background: #3B82F6;
  color: #FFFFFF;
}
:deep(.el-button--primary:hover),
:deep(.el-button--primary:focus) {
  border-color: #2563EB;
  background: #2563EB;
  color: #FFFFFF;
}

/* 链接文字 */
.link-text {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #9CA3AF;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s ease;
}
.link-text:hover { color: #FFFFFF; }

/* 实时数据 */
.data-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.data-item {
  padding: 16px;
  background: #141414;
  border: 1px solid #2A2A2A;
  border-radius: 10px;
  text-align: center;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}
.data-item:hover {
  border-color: #3B82F6;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.12);
}

.data-value { font-size: 26px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; }
.data-label { font-size: 13px; color: #9CA3AF; }

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 900px) {
  .plan-grid { grid-template-columns: 1fr; }
  .data-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
