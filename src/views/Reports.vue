<template>
  <div class="reports-container">
    <el-page-header @back="$router.push('/home')" content="报告列表" />
    
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>检测报告</span>
          <el-button type="primary" @click="$router.push('/detection')">
            <el-icon><Plus /></el-icon>
            新建检测
          </el-button>
        </div>
      </template>

      <el-table :data="reports" v-loading="loading">
        <el-table-column prop="report_id" label="报告编号" width="180" />
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="verification_code" label="验证码" width="150">
          <template #default="{ row }">
            <el-tooltip :content="row.verification_code">
              <code>{{ row.verification_code }}</code>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.pdf_url ? 'success' : 'info'">
              {{ row.pdf_url ? '已完成' : '生成中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewReport(row.report_id)">
              查看详情
            </el-button>
            <el-button v-if="row.pdf_url" type="primary" link :href="row.pdf_url" target="_blank">
              下载 PDF
            </el-button>
            <el-button type="primary" link @click="copyVerifyLink(row.verification_code)">
              复制验证链接
            </el-button>
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listReports, Report } from '@/api/report'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const reports = ref<Report[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)

async function fetchReports() {
  loading.value = true
  try {
    const data = await listReports((currentPage.value - 1) * 20, 20)
    // 后端返回分页对象 {reports: [...], total: N}，提取数组
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
.reports-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
