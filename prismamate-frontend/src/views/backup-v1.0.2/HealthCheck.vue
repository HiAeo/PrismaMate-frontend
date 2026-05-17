<template>
  <Layout>
    <div class="health-check-page">
      <!-- 页面标题 -->
      <div class="header">
        <h1>品牌体检中心</h1>
        <p class="subtitle">定期体检，发现 AI 可见度变化趋势</p>
      </div>

      <!-- 功能入口卡片 -->
      <div class="entry-cards">
        <div class="dash-card entry-card entry-blue" @click="$router.push('/health-check/new')">
          <div class="entry-icon">
            <el-icon :size="32"><Plus /></el-icon>
          </div>
          <div class="entry-content">
            <h3>新建体检</h3>
            <p>开始一次品牌 AI 可见度检测</p>
          </div>
        </div>
        <div class="dash-card entry-card entry-green" @click="$router.push('/health-check/templates')">
          <div class="entry-icon">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="entry-content">
            <h3>我的模板</h3>
            <p>管理体检模板，快速复用</p>
          </div>
        </div>
      </div>

      <!-- 最近体检报告 -->
      <div class="dash-card recent-reports-card">
        <div class="card-header-bar flex-between">
          <span>最近体检报告</span>
          <a class="link-text" @click="$router.push('/reports')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </a>
        </div>

        <el-table
          v-if="recentReports.length > 0"
          :data="recentReports"
          style="width: 100%"
          :header-cell-style="headerStyle"
        >
          <el-table-column prop="report_id" label="报告编号" width="180">
            <template #default="{ row }">
              <a class="link-text" @click="$router.push(`/reports/${row.report_id}`)">
                {{ row.report_id }}
              </a>
            </template>
          </el-table-column>
          <el-table-column prop="report_type" label="类型" width="120">
            <template #default="{ row }">
              <span class="status-tag" :class="row.report_type === 'health_check' ? 'tag-green' : 'tag-blue'">
                {{ row.report_type === 'health_check' ? '体检报告' : 'GEO验证' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="platforms" label="检测平台" min-width="200">
            <template #default="{ row }">
              {{ row.platforms?.join(', ') || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="total_mentions" label="提及数" width="100" align="center" />
          <el-table-column prop="created_at" label="检测时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <a class="link-text" @click="$router.push(`/reports/${row.report_id}`)">查看</a>
              <a
                v-if="row.parent_report_id"
                class="link-text"
                @click="$router.push(`/reports/${row.report_id}/comparison`)"
              >
                对比
              </a>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-else description="暂无体检报告">
          <el-button type="primary" @click="$router.push('/health-check/new')">
            立即体检
          </el-button>
        </el-empty>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, ArrowRight } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import api from '@/api/axios'

const router = useRouter()
const recentReports = ref<any[]>([])

const headerStyle = () => ({
  background: 'transparent',
  color: 'rgba(255,255,255,0.5)',
  fontWeight: 600,
  fontSize: '13px',
  borderBottom: '1px solid rgba(255,255,255,0.1)'
})

const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const loadRecentReports = async () => {
  try {
    const data = await api.get('/reports?limit=5')
    if (data?.reports) {
      recentReports.value = data.reports.filter((r: any) =>
        r.report_type === 'health_check' || !r.report_type
      )
    }
  } catch (err: any) {
    console.error('加载报告失败', err)
  }
}

onMounted(() => {
  loadRecentReports()
})
</script>

<style scoped>
.health-check-page {
  max-width: 100%;
}

.header {
  margin-bottom: 24px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #FFFFFF;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
}

/* 通用卡片 */
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

/* 入口卡片 */
.entry-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.entry-card {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 16px;
}

.entry-card:hover {
  transform: translateY(-2px);
}

.entry-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.entry-blue .entry-icon {
  background: rgba(77, 107, 254, 0.12);
  border-color: rgba(77, 107, 254, 0.25);
  color: #4D6BFE;
}

.entry-green .entry-icon {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.25);
  color: #10B981;
}

.entry-content h3 {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
}

.entry-content p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
}

/* 最近报告 */
.recent-reports-card {
  margin-bottom: 20px;
}

.link-text {
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s ease;
  margin-right: 12px;
}

.link-text:hover {
  color: #FFFFFF;
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.tag-green {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
}

.tag-blue {
  background: rgba(77, 107, 254, 0.15);
  color: #4D6BFE;
}

/* 响应式 */
@media (max-width: 768px) {
  .entry-cards {
    grid-template-columns: 1fr;
  }
}
</style>
