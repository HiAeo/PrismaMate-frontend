<template>
  <Layout>
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1>欢迎回来，{{ userStore.user?.username || userStore.user?.email || '用户' }}</h1>
      <p class="subtitle">这里是您的品牌健康管理控制台</p>
    </div>

    <!-- 核心数据卡片 -->
    <div class="stats-grid">
      <div class="dash-card stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><Ticket /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">当前套餐</div>
          <div class="stat-value">
            <span class="plan-tag" :class="getPlanTagClass(currentPlan?.plan_id)">
              {{ currentPlan?.name || '加载中...' }}
            </span>
          </div>
          <div class="stat-desc" v-if="currentPlan">
            {{ currentPlan.monthly_quota }}次/月
          </div>
        </div>
      </div>

      <div class="dash-card stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><Coin /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">剩余积分</div>
          <div class="stat-value highlight">{{ currentPlan?.points_balance || 0 }}</div>
          <div class="stat-desc">
            <span v-if="currentPlan?.monthly_remaining > 0">
              本月剩余 {{ currentPlan.monthly_remaining }} 次检测
            </span>
            <span v-else class="text-warning">本月额度已用完</span>
          </div>
        </div>
      </div>

      <div class="dash-card stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">本月检测</div>
          <div class="stat-value">{{ currentPlan?.monthly_usage || 0 }}</div>
          <div class="stat-desc">
            共 {{ currentPlan?.monthly_usage || 0 }} / {{ currentPlan?.monthly_quota || 0 }} 次
          </div>
        </div>
      </div>

      <div class="dash-card stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">报告总数</div>
          <div class="stat-value">{{ reportsCount }}</div>
          <div class="stat-desc">
            <span v-if="latestReport" class="latest-report">
              最新: {{ formatDate(latestReport.created_at) }}
            </span>
            <span v-else>暂无报告</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 + 套餐状态 -->
    <div class="two-col-grid">
      <div class="dash-card action-card">
        <div class="card-header-bar">
          <span>快速开始</span>
        </div>
        <div class="quick-actions">
          <a class="hero-btn" @click="$router.push('/health-check')">
            品牌体检
          </a>
          <a class="hero-btn" @click="$router.push('/geo-verification')" v-if="hasAdvancedFeatures">
            GEO验证
          </a>
          <a class="hero-btn" @click="$router.push('/reports')">
            我的报告
          </a>
          <a class="hero-btn" @click="$router.push('/dashboard/subscription')" v-if="!hasAdvancedFeatures">
            升级套餐
          </a>
        </div>
      </div>

      <div class="dash-card tips-card" v-if="currentPlan">
        <div class="card-header-bar">
          <span>套餐状态</span>
        </div>
        <div class="tips-content">
          <template v-if="isMiniPlan">
            <div class="status-box">
              <div class="status-label">您正在使用免费版</div>
              <div class="status-desc">每月 {{ currentPlan.monthly_quota }} 次检测额度</div>
            </div>
            <a class="hero-btn primary" @click="$router.push('/dashboard/subscription')">
              升级到高级版
            </a>
          </template>
          <template v-else>
            <div class="status-box success">
              <div class="status-label">套餐使用正常</div>
              <div class="status-desc">本月剩余 {{ currentPlan.monthly_remaining }} 次检测</div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 最新报告列表 -->
    <div class="dash-card table-card" v-if="recentReports.length > 0">
      <div class="card-header-bar flex-between">
        <span>最新报告</span>
        <a class="link-text" @click="$router.push('/reports')">查看全部</a>
      </div>
      <div class="table-wrap">
        <el-table :data="recentReports" style="width: 100%" :header-cell-style="headerStyle">
          <el-table-column label="报告ID" width="200">
            <template #default="{ row }">
              <span class="report-id">{{ row.report_id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="template_name" label="模板名称" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span class="status-tag" :class="getStatusClass(row.status)">
                {{ row.status }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <a class="link-text" @click="viewReport(row)">查看</a>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 功能特性说明 -->
    <div class="dash-card features-card">
      <div class="card-header-bar">
        <span>功能概览</span>
      </div>
      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">
            <el-icon :size="28"><FirstAidKit /></el-icon>
          </div>
          <h3>品牌体检</h3>
          <p>定期检测品牌形象在搜索引擎的表现，追踪品牌知名度变化</p>
        </div>
        <div class="feature-item" v-if="hasAdvancedFeatures">
          <div class="feature-icon">
            <el-icon :size="28"><DataLine /></el-icon>
          </div>
          <h3>GEO验证</h3>
          <p>验证GEO内容在不同AI搜索引擎中的表现，评估内容影响力</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <h3>历史对比</h3>
          <p>对比不同时间段的检测结果，分析品牌排名变化趋势</p>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Ticket, Coin, DataAnalysis, Document, FirstAidKit, DataLine } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'
import { getMyPlan } from '@/api/subscription'
import { getReports } from '@/api/report'

const router = useRouter()
const userStore = useUserStore()

const currentPlan = ref<any>(null)
const reportsCount = ref(0)
const latestReport = ref<any>(null)
const recentReports = ref<any[]>([])

const isMiniPlan = computed(() => {
  return currentPlan.value?.plan_id === 'plan_mini'
})

const hasAdvancedFeatures = computed(() => {
  return currentPlan.value?.plan_id !== 'plan_mini'
})

const getPlanTagClass = (planId: string) => {
  const map: Record<string, string> = {
    plan_mini: 'tag-info',
    plan_max: 'tag-warning',
    plan_plus: 'tag-danger'
  }
  return map[planId] || 'tag-info'
}

const getStatusClass = (status: string) => {
  const map: Record<string, string> = {
    completed: 'status-success',
    pending: 'status-warning',
    failed: 'status-danger',
    processing: 'status-primary'
  }
  return map[status] || 'status-info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewReport = (report: any) => {
  router.push(`/reports/${report.report_id}`)
}

const headerStyle = () => ({
  background: 'transparent',
  color: 'rgba(255,255,255,0.5)',
  fontWeight: 600,
  fontSize: '13px',
  borderBottom: '1px solid rgba(255,255,255,0.1)'
})

const loadData = async () => {
  try {
    const planRes = await getMyPlan()
    currentPlan.value = planRes.plan

    const reportsRes = await getReports()
    const reports = reportsRes.reports || []
    reportsCount.value = reports.length
    latestReport.value = reports[0] || null
    recentReports.value = reports.slice(0, 5)
  } catch (error: any) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* 欢迎区域 */
.welcome-section {
  margin-bottom: 28px;
}

.welcome-section h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #FFFFFF;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

/* 通用卡片 - 与首页llm-card风格一致 */
.dash-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.dash-card:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.18);
}

.card-header-bar {
  font-size: 15px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.card-header-bar.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 统计卡片 */
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 4px;
}

.stat-value.highlight {
  color: #F59E0B;
}

.stat-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.text-warning {
  color: #EF4444;
}

.latest-report {
  color: #10B981;
}

/* 套餐标签 */
.plan-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.tag-info {
  background: rgba(148, 163, 184, 0.15);
  color: #94A3B8;
}

.tag-warning {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}

.tag-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

/* 两列布局 */
.two-col-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

/* 按钮 - 与首页hero-btn一致 */
.hero-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  font-weight: 400;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  text-decoration: none;
  transition: all 0.25s ease;
  cursor: pointer;
}

.hero-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
  transform: translateX(4px);
}

.hero-btn.primary {
  background: rgba(77, 107, 254, 0.15);
  border-color: rgba(77, 107, 254, 0.3);
  color: #4D6BFE;
}

.hero-btn.primary:hover {
  background: rgba(77, 107, 254, 0.25);
  border-color: rgba(77, 107, 254, 0.5);
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 状态盒子 */
.tips-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.status-box {
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
}

.status-box.success {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.06);
}

.status-label {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 4px;
}

.status-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 链接文字 */
.link-text {
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.link-text:hover {
  color: #FFFFFF;
}

/* 表格卡片 */
.table-card {
  margin-bottom: 20px;
}

.table-wrap :deep(.el-table) {
  background: transparent;
}

.table-wrap :deep(.el-table__header-wrapper th) {
  background: transparent !important;
}

.table-wrap :deep(.el-table tr) {
  background: transparent;
}

.table-wrap :deep(.el-table td) {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.table-wrap :deep(.el-table__body tr:hover > td) {
  background: rgba(255, 255, 255, 0.04) !important;
}

.report-id {
  font-family: var(--font-mono);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
}

.status-warning {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}

.status-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

.status-primary {
  background: rgba(77, 107, 254, 0.15);
  color: #4D6BFE;
}

.status-info {
  background: rgba(148, 163, 184, 0.15);
  color: #94A3B8;
}

/* 功能特性 */
.features-card {
  margin-bottom: 20px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-item {
  text-align: center;
  padding: 16px;
}

.feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.6);
}

.feature-item h3 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #FFFFFF;
}

.feature-item p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .two-col-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
