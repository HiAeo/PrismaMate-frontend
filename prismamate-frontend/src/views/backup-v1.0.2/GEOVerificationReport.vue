<template>
  <Layout>
    <div class="geo-verification-report-container">
      <div class="header">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1>GEO验证报告</h1>
      </div>

    <div v-loading="loading">
      <!-- 验证概要 -->
      <div class="dash-card summary-card">
        <div class="card-header-bar">验证概要</div>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="验证ID">
            {{ report.verification_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="验证场景">
            <span class="status-tag" :class="report.scenario === 'delivery' ? 'tag-green' : 'tag-blue'">
              {{ report.scenario === 'delivery' ? '交付验证' : '进度验证' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="GEO 机构">
            {{ report.geo_plan?.geo_company || '未指定' }}
          </el-descriptions-item>
          <el-descriptions-item label="关键词">
            {{ report.geo_plan?.keywords?.join('、') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="平台">
            {{ report.geo_plan?.platforms?.join('、') || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="检测时间">
            {{ formatDate(report.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 差异汇总卡片 -->
      <div class="summary-cards">
        <div class="dash-card summary-card-item summary-green">
          <div class="summary-content">
            <el-icon class="summary-icon"><CircleCheck /></el-icon>
            <div class="summary-info">
              <div class="summary-value">{{ summary.consistent }}</div>
              <div class="summary-label">一致</div>
            </div>
          </div>
        </div>

        <div class="dash-card summary-card-item summary-orange">
          <div class="summary-content">
            <el-icon class="summary-icon"><Warning /></el-icon>
            <div class="summary-info">
              <div class="summary-value">{{ summary.different }}</div>
              <div class="summary-label">有差异</div>
            </div>
          </div>
        </div>

        <div class="dash-card summary-card-item summary-gray">
          <div class="summary-content">
            <el-icon class="summary-icon"><CircleClose /></el-icon>
            <div class="summary-info">
              <div class="summary-value">{{ summary.out_of_coverage }}</div>
              <div class="summary-label">超出覆盖</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 差异列表 -->
      <div class="dash-card differences-card">
        <div class="card-header-bar flex-between">
          <span>差异详情</span>
          <span class="status-tag tag-blue" v-if="summary.total_items > 0">
            共 {{ summary.total_items }} 项
          </span>
        </div>

        <el-table
          v-if="report.differences && report.differences.length > 0"
          :data="report.differences"
          style="width: 100%"
          :row-class-name="getRowClassName"
          :header-cell-style="headerStyle"
        >
          <el-table-column prop="brand" label="品牌" width="120" />
          <el-table-column prop="keyword" label="关键词" width="150" />
          <el-table-column prop="platform" label="平台" width="100">
            <template #default="{ row }">
              <span class="status-tag tag-gray">{{ row.platform }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="field" label="对比字段" width="120">
            <template #default="{ row }">
              {{ getFieldLabel(row.field) }}
            </template>
          </el-table-column>
          <el-table-column label="乙方声称" width="150">
            <template #default="{ row }">
              <span class="claimed-value">{{ formatFieldValue(row.field, row.claimed_value) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="PrismaMate 实测" width="150">
            <template #default="{ row }">
              <span class="detected-value">{{ formatFieldValue(row.field, row.detected_value) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="结论" width="140">
            <template #default="{ row }">
              <span class="status-tag" :class="getVerdictClass(row.verdict)">
                {{ row.verdict }}
              </span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-else
          description="暂无差异数据"
        />
      </div>

      <!-- 乙方声称数据 vs PrismaMate 实测数据 -->
      <div v-if="report.geo_claimed_data && report.geo_claimed_data.length > 0" class="dash-card data-comparison-card">
        <div class="card-header-bar">数据对比表</div>

        <el-table
          :data="report.geo_claimed_data"
          style="width: 100%"
          :header-cell-style="headerStyle"
        >
          <el-table-column prop="brand" label="品牌" width="100" />
          <el-table-column prop="keyword" label="关键词" width="120" />
          <el-table-column prop="platform" label="平台" width="100">
            <template #default="{ row }">
              <span class="status-tag tag-gray">{{ row.platform }}</span>
            </template>
          </el-table-column>
          <el-table-column label="乙方声称" width="200">
            <template #default="{ row }">
              <div class="claimed-data">
                <span>提及: {{ row.is_mentioned ? '是' : '否' }}</span>
                <span v-if="row.mention_position">位次: {{ row.mention_position }}</span>
                <span v-if="row.mention_rate">提及率: {{ row.mention_rate }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="结论" width="120">
            <template #default="{ row }">
              <span class="status-tag" :class="getItemVerdictClass(row)">
                {{ getItemVerdict(row) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, CircleCheck, Warning, CircleClose } from '@element-plus/icons-vue'
import api from '@/api/axios'
import Layout from '@/components/Layout.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const report = reactive({
  verification_id: '',
  scenario: '',
  geo_plan: {},
  geo_claimed_data: [],
  differences: [],
  summary: {},
  created_at: ''
})

const summary = computed(() => {
  const s = report.summary || {}
  return {
    consistent: s.consistent || 0,
    different: s.different || 0,
    out_of_coverage: s.out_of_coverage || 0,
    total_items: s.total_items || 0
  }
})

const headerStyle = () => ({
  background: 'transparent',
  color: 'rgba(255,255,255,0.5)',
  fontWeight: 600,
  fontSize: '13px',
  borderBottom: '1px solid rgba(255,255,255,0.1)'
})

// 加载报告
const loadReport = async () => {
  const verificationId = route.params.id
  if (!verificationId) {
    ElMessage.error('缺少验证ID')
    router.push({ name: 'GEOVerification' })
    return
  }

  loading.value = true
  try {
    const data = await api.get(`/geo-verification/${verificationId}/report`)
    Object.assign(report, data)
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败')
  } finally {
    loading.value = false
  }
}

// 获取字段标签
const getFieldLabel = (field) => {
  const labels = {
    'is_mentioned': '是否提及',
    'mention_position': '提及位次',
    'mention_rate': '提及率'
  }
  return labels[field] || field
}

// 格式化字段值
const formatFieldValue = (field, value) => {
  if (value === null || value === undefined) return '-'
  if (field === 'is_mentioned') return value ? '是' : '否'
  if (field === 'mention_rate') return `${value}%`
  return value
}

// 获取判决样式类
const getVerdictClass = (verdict) => {
  const map = {
    '一致': 'tag-green',
    '有差异': 'tag-orange',
    '超出覆盖范围': 'tag-gray'
  }
  return map[verdict] || 'tag-gray'
}

// 获取行样式类
const getRowClassName = ({ row }) => {
  if (row.verdict === '有差异') return 'diff-row'
  if (row.verdict === '超出覆盖范围') return 'out-of-coverage-row'
  return ''
}

// 获取单项判决
const getItemVerdict = (item) => {
  if (!report.differences || report.differences.length === 0) return '待检测'

  const relatedDiffs = report.differences.filter(
    d => d.brand === item.brand &&
         d.keyword === item.keyword &&
         d.platform === item.platform
  )

  if (relatedDiffs.some(d => d.verdict === '超出覆盖范围')) {
    return '超出覆盖'
  }
  if (relatedDiffs.some(d => d.verdict === '有差异')) {
    return '有差异'
  }
  if (relatedDiffs.length > 0) {
    return '一致'
  }
  return '待检测'
}

// 获取单项判决样式类
const getItemVerdictClass = (item) => {
  const verdict = getItemVerdict(item)
  const map = {
    '一致': 'tag-green',
    '有差异': 'tag-orange',
    '超出覆盖': 'tag-gray',
    '待检测': 'tag-blue'
  }
  return map[verdict] || 'tag-gray'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 返回
const goBack = () => {
  router.push({ name: 'GEOVerification' })
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.geo-verification-report-container {
  max-width: 100%;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #FFFFFF;
}

/* 通用卡片 */
.dash-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  margin-bottom: 20px;
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

/* 汇总卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card-item {
  text-align: center;
  padding: 20px;
}

.summary-card-item.summary-green {
  border-left: 4px solid #10B981;
}

.summary-card-item.summary-orange {
  border-left: 4px solid #F59E0B;
}

.summary-card-item.summary-gray {
  border-left: 4px solid rgba(255, 255, 255, 0.2);
}

.summary-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.summary-icon {
  font-size: 36px;
}

.summary-green .summary-icon {
  color: #10B981;
}

.summary-orange .summary-icon {
  color: #F59E0B;
}

.summary-gray .summary-icon {
  color: rgba(255, 255, 255, 0.4);
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
  color: #FFFFFF;
}

.summary-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.45);
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

.tag-orange {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}

.tag-blue {
  background: rgba(77, 107, 254, 0.15);
  color: #4D6BFE;
}

.tag-gray {
  background: rgba(148, 163, 184, 0.15);
  color: #94A3B8;
}

.claimed-value,
.detected-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

:deep(.diff-row) {
  background: rgba(245, 158, 11, 0.04) !important;
}

:deep(.out-of-coverage-row) {
  background: rgba(148, 163, 184, 0.04) !important;
  color: rgba(255, 255, 255, 0.5);
}

.claimed-data {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

/* 响应式 */
@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
