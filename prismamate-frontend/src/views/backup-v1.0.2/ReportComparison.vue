<template>
  <Layout>
    <div class="report-comparison-page">
      <!-- 页面标题 -->
      <div class="header">
        <h1>报告对比</h1>
        <p class="subtitle">{{ comparison?.summary_text || '查看两次体检的变化趋势' }}</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 对比数据 -->
      <div v-else-if="comparison" class="comparison-content">
        <!-- 报告基本信息对比 -->
        <div class="dash-card report-comparison-header">
          <div class="card-header-bar">报告信息对比</div>
          <el-row :gutter="24">
            <el-col :span="12">
              <div class="report-card parent">
                <h4>上次体检</h4>
                <el-descriptions :column="1" size="small">
                  <el-descriptions-item label="报告编号">
                    <a class="link-text" @click="$router.push(`/reports/${comparison.parent_report?.report_id}`)">
                      {{ comparison.parent_report?.report_id }}
                    </a>
                  </el-descriptions-item>
                  <el-descriptions-item label="检测时间">
                    {{ formatTime(comparison.parent_report?.created_at) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="平台">
                    {{ comparison.parent_report?.platforms?.join(', ') }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="report-card current">
                <h4>本次体检</h4>
                <el-descriptions :column="1" size="small">
                  <el-descriptions-item label="报告编号">
                    <a class="link-text" @click="$router.push(`/reports/${comparison.current_report?.report_id}`)">
                      {{ comparison.current_report?.report_id }}
                    </a>
                  </el-descriptions-item>
                  <el-descriptions-item label="检测时间">
                    {{ formatTime(comparison.current_report?.created_at) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="平台">
                    {{ comparison.current_report?.platforms?.join(', ') }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 变化摘要 -->
        <div class="dash-card summary-card">
          <div class="card-header-bar flex-between">
            <span>变化摘要</span>
            <span class="time-gap">间隔 {{ comparison.comparison_time_gap_days }} 天</span>
          </div>
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="summary-item new">
                <div class="summary-value">{{ comparison.summary?.total_new_mentions || 0 }}</div>
                <div class="summary-label">新增提及</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item lost">
                <div class="summary-value">{{ comparison.summary?.total_lost_mentions || 0 }}</div>
                <div class="summary-label">消失提及</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item improved">
                <div class="summary-value">{{ comparison.summary?.total_ranking_improved || 0 }}</div>
                <div class="summary-label">位次提升</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item declined">
                <div class="summary-value">{{ comparison.summary?.total_ranking_declined || 0 }}</div>
                <div class="summary-label">位次下降</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 新增提及 -->
        <div v-if="comparison.new_mentions?.length > 0" class="dash-card changes-card new">
          <div class="card-header-bar">
            <span>
              <el-icon class="header-icon new"><CirclePlus /></el-icon>
              新增提及 ({{ comparison.new_mentions.length }})
            </span>
          </div>
          <el-table :data="comparison.new_mentions" style="width: 100%" :header-cell-style="headerStyle">
            <el-table-column prop="brand" label="品牌" width="120" />
            <el-table-column prop="keyword" label="关键词" min-width="150" />
            <el-table-column prop="platform" label="平台" width="120" />
            <el-table-column prop="current_position" label="当前位次" width="100" align="center">
              <template #default="{ row }">
                <span class="status-tag tag-green">第 {{ row.current_position }} 位</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 消失提及 -->
        <div v-if="comparison.lost_mentions?.length > 0" class="dash-card changes-card lost">
          <div class="card-header-bar">
            <span>
              <el-icon class="header-icon lost"><Remove /></el-icon>
              消失提及 ({{ comparison.lost_mentions.length }})
            </span>
          </div>
          <el-table :data="comparison.lost_mentions" style="width: 100%" :header-cell-style="headerStyle">
            <el-table-column prop="brand" label="品牌" width="120" />
            <el-table-column prop="keyword" label="关键词" min-width="150" />
            <el-table-column prop="platform" label="平台" width="120" />
            <el-table-column prop="previous_position" label="上次位次" width="100" align="center">
              <template #default="{ row }">
                <span class="status-tag tag-red">第 {{ row.previous_position }} 位</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 位次变化 -->
        <div v-if="comparison.ranking_changes?.length > 0" class="dash-card changes-card ranking">
          <div class="card-header-bar">
            <span>
              <el-icon class="header-icon ranking"><Top /></el-icon>
              位次变化 ({{ comparison.ranking_changes.length }})
            </span>
          </div>
          <el-table :data="comparison.ranking_changes" style="width: 100%" :header-cell-style="headerStyle">
            <el-table-column prop="brand" label="品牌" width="120" />
            <el-table-column prop="keyword" label="关键词" min-width="150" />
            <el-table-column prop="platform" label="平台" width="120" />
            <el-table-column prop="previous_position" label="上次位次" width="100" align="center">
              <template #default="{ row }">
                {{ row.previous_position || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="current_position" label="当前位次" width="100" align="center">
              <template #default="{ row }">
                {{ row.current_position || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="change" label="变化" width="100" align="center">
              <template #default="{ row }">
                <span class="status-tag" :class="row.trend === 'improved' ? 'tag-green' : 'tag-red'">
                  {{ row.change > 0 ? '+' : '' }}{{ row.change }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 无变化提示 -->
        <el-empty
          v-if="!comparison.new_mentions?.length && !comparison.lost_mentions?.length && !comparison.ranking_changes?.length"
          description="较上次体检无变化"
        />
      </div>

      <!-- 错误状态 -->
      <el-result
        v-else-if="error"
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="loadComparison">重试</el-button>
          <el-button @click="$router.back()">返回</el-button>
        </template>
      </el-result>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CirclePlus, Remove, Top } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import api from '@/api/axios'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const comparison = ref<any>(null)

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

const loadComparison = async () => {
  const reportId = route.params.id as string
  if (!reportId) {
    error.value = '报告ID无效'
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await api.get(`/reports/${reportId}/comparison`)
    comparison.value = response
  } catch (err: any) {
    console.error('加载对比数据失败', err)
    const detail = err.response?.data?.detail
    if (detail) {
      error.value = typeof detail === 'string' ? detail : '加载失败'
    } else {
      error.value = '加载对比数据失败'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadComparison()
})
</script>

<style scoped>
.report-comparison-page {
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

.loading-state {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 40px;
}

.comparison-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.report-comparison-header {
  border-left: 4px solid #4D6BFE;
}

.report-card h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #FFFFFF;
}

.report-card.current {
  border-left: 2px dashed rgba(255, 255, 255, 0.12);
  padding-left: 20px;
}

.link-text {
  color: #4D6BFE;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
}

.link-text:hover {
  color: #6B85FF;
}

.summary-card {
  border-left: 4px solid #10B981;
}

.time-gap {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

.summary-item {
  text-align: center;
  padding: 20px;
}

.summary-value {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 8px;
}

.summary-item.new .summary-value {
  color: #10B981;
}

.summary-item.lost .summary-value {
  color: #EF4444;
}

.summary-item.improved .summary-value {
  color: #4D6BFE;
}

.summary-item.declined .summary-value {
  color: #F59E0B;
}

.summary-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.45);
}

.changes-card {
  border-left: 4px solid;
}

.changes-card.new {
  border-left-color: #10B981;
}

.changes-card.lost {
  border-left-color: #EF4444;
}

.changes-card.ranking {
  border-left-color: #4D6BFE;
}

.header-icon {
  margin-right: 8px;
  vertical-align: middle;
}

.header-icon.new {
  color: #10B981;
}

.header-icon.lost {
  color: #EF4444;
}

.header-icon.ranking {
  color: #4D6BFE;
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

.tag-red {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}
</style>
