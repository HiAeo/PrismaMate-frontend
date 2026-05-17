<template>
  <Layout>
    <div class="page-container report-detail-container">
      <div class="header">
        <el-button @click="$router.push('/reports')">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1>报告详情</h1>
      </div>

      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="report" class="report-content">
        <div class="dash-card info-card">
          <div class="card-header-bar flex-between">
            <span>报告信息</span>
            <el-button v-if="report.pdf_url" type="primary" size="small" :href="report.pdf_url" target="_blank">
              下载 PDF
            </el-button>
          </div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="报告编号">{{ report.report_id }}</el-descriptions-item>
            <el-descriptions-item label="验证码">
              <span class="status-tag tag-orange">{{ report.verification_code }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="生成时间">{{ formatDate(report.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="报告哈希">
              <code class="hash-code">{{ (report.report_hash || '').substring(0, 24) }}...</code>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="dash-card verify-card">
          <div class="card-header-bar">
            <span>防篡改验证</span>
          </div>
          <el-button type="primary" @click="verifyReportAction">报告验真</el-button>

          <div v-if="verifyResult" class="verify-result">
            <div class="status-box" :class="verifyResult.is_valid ? 'success' : 'danger'">
              <div class="status-label">{{ verifyResult.is_valid ? '验证通过' : '验证失败' }}</div>
              <div class="status-desc">{{ verifyResult.message }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReport, verifyReport as verifyApi, VerifyResult, Report } from '@/api/report'
import { Loading, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'

const route = useRoute()
const reportId = route.params.id as string

const report = ref<Report | null>(null)
const verifyResult = ref<VerifyResult | null>(null)
const loading = ref(false)

async function fetchReport() {
  loading.value = true
  try {
    const res = await getReport(reportId)
    report.value = res.data
  } finally {
    loading.value = false
  }
}

async function verifyReportAction() {
  if (!report.value) return
  try {
    const res = await verifyApi(report.value.verification_code)
    verifyResult.value = res.data
  } catch {
    ElMessage.error('验证失败')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(fetchReport)
</script>

<style scoped>
/* .report-detail-container 容器样式已移至 global.css .page-container */


.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--foreground);
  line-height: 1.3;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 100px;
  color: var(--text-muted);
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 通用卡片 */
.dash-card {
  background: var(--card-bg);
  border: var(--card-border);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
}

.card-header-bar {
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--foreground-secondary);
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.card-header-bar.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hash-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--hover-bg);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  color: var(--foreground);
}

.verify-result {
  margin-top: 16px;
}

.status-box {
  padding: 14px;
  border-radius: var(--input-radius);
  border: 1px solid var(--border);
  background: var(--hover-bg);
}

.status-box.success {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.06);
}

.status-box.danger {
  border-color: rgba(220, 38, 38, 0.3);
  background: rgba(220, 38, 38, 0.06);
}

.status-label {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--foreground);
  margin-bottom: 4px;
}

.status-desc {
  font-size: var(--text-base);
  color: var(--text-muted);
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 500;
}

.tag-orange {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}
</style>
