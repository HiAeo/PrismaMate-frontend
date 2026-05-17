<template>
  <Layout>
    <div class="page-container reports-container">
      <div class="header">
        <h1>PrismaMate 棱镜GEO 生成式引擎优化效果监测</h1>
        <p class="subtitle">输入优化关键词和目标平台，PrismaMate 将实时检测并生成独立报告，同时支持上传 GEO 机构的交付数据，进行逐项差异对比，标注"一致/有差异/超出覆盖范围"，让乙方承诺的效果一目了然。</p>
      </div>

      <div class="dash-card list-card">
        <div class="card-header-bar flex-between">
          <span>检测报告</span>
          <el-button type="primary" size="small" @click="$router.push('/detection')">
            新建检测
          </el-button>
        </div>

        <el-table :data="reports" v-loading="loading" :header-cell-style="headerStyle">
          <el-table-column prop="report_id" label="报告编号" min-width="180">
            <template #default="{ row }">
              <span class="report-id">{{ row.report_id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="生成时间" min-width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="verification_code" label="验证码" min-width="150">
            <template #default="{ row }">
              <code class="verify-code">{{ row.verification_code }}</code>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="100">
            <template #default="{ row }">
              <span class="status-tag" :class="row.pdf_url ? 'tag-green' : 'tag-blue'">
                {{ row.pdf_url ? '已完成' : '生成中' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="200" fixed="right">
            <template #default="{ row }">
              <a class="link-text" @click="viewReport(row.report_id)">查看详情</a>
              <a v-if="row.pdf_url" class="link-text" :href="row.pdf_url" target="_blank">下载 PDF</a>
              <a class="link-text" @click="copyVerifyLink(row.verification_code)">复制验证链接</a>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-if="total > 0"
          layout="total, prev, pager, next"
          :total="total"
          :page-size="20"
          v-model:current-page="currentPage"
          @current-change="fetchReports"
          style="margin-top: 20px; justify-content: center"
        />
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listReports, Report } from '@/api/report'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'

const router = useRouter()

const reports = ref<Report[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)

const headerStyle = () => ({
  background: 'transparent',
  color: '#9CA3AF',
  fontWeight: 500,
  fontSize: '14px',
  borderBottom: '1px solid #2D2D2D'
})

async function fetchReports() {
  loading.value = true
  try {
    const data = await listReports((currentPage.value - 1) * 20, 20)
    reports.value = data.reports || data || []
    total.value = data.total || data.length || 0
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function viewReport(reportId: string) {
  router.push(`/reports/${reportId}`)
}

function copyVerifyLink(code: string) {
  const url = `${window.location.origin}/verify/${code}`
  navigator.clipboard.writeText(url)
  ElMessage.success('验证链接已复制到剪贴板')
}

onMounted(fetchReports)
</script>

<style scoped>
/* .reports-container 容器样式已移至 global.css .page-container */

.header {
  margin-bottom: 24px;
}

.header h1 {
  margin: 0 0 8px 0;
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--foreground);
  line-height: 1.3;
}

.subtitle {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* 通用卡片 */
.dash-card {
  background: var(--card-bg);
  border: var(--card-border);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
}

.list-card {
  margin-bottom: 20px;
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

.report-id {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.verify-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--foreground);
  background: var(--hover-bg);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.link-text {
  color: var(--text-muted);
  font-size: var(--text-base);
  cursor: pointer;
  transition: color var(--transition-fast);
  margin-right: 12px;
}

.link-text:hover {
  color: var(--primary);
}

.status-tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 500;
}

.tag-green {
  background: rgba(16, 185, 129, 0.12);
  color: var(--success);
}

.tag-blue {
  background: rgba(59, 130, 246, 0.12);
  color: var(--primary);
}
</style>
