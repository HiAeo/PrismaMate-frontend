<template>
  <div class="report-detail-container">
    <el-page-header @back="$router.push('/reports')" :content="reportId" />
    
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="report" class="report-content">
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>报告信息</span>
            <el-button v-if="report.pdf_url" type="primary" :href="report.pdf_url" target="_blank">
              下载 PDF
            </el-button>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报告编号">{{ report.report_id }}</el-descriptions-item>
          <el-descriptions-item label="验证码">{{ report.verification_code }}</el-descriptions-item>
          <el-descriptions-item label="生成时间">{{ formatDate(report.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="报告哈希">
            <el-tooltip :content="report.report_hash">
              <code>{{ report.report_hash.substring(0, 24) }}...</code>
            </el-tooltip>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="verify-card">
        <template #header>
          <span>防篡改验证</span>
        </template>
        <el-button type="primary" @click="verifyReportAction">验证报告真伪</el-button>
        
        <div v-if="verifyResult" class="verify-result">
          <el-alert :type="verifyResult.is_valid ? 'success' : 'error'" :title="verifyResult.message" show-icon style="margin-top: 20px" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReport, verifyReport as verifyApi, VerifyResult, Report } from '@/api/report'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const reportId = route.params.id as string

const report = ref<Report | null>(null)
const verifyResult = ref<VerifyResult | null>(null)
const loading = ref(false)

async function fetchReport() {
  loading.value = true
  try {
    report.value = await getReport(reportId)
  } finally {
    loading.value = false
  }
}

async function verifyReportAction() {
  if (!report.value) return
  try {
    verifyResult.value = await verifyApi(report.value.verification_code)
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
.report-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 100px;
}

.report-content {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
