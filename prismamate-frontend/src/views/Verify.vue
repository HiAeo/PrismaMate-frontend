<template>
  <Layout>
    <div class="page-container verify-wrapper">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>PrismaMate 棱镜报告防篡改验真</h1>
        <p class="subtitle">每一份由 PrismaMate 生成的报告，都附带唯一的 12 位验证码和 SHA-256 哈希值。</p>
      </div>

      <el-card class="verify-card">
        <template #header>
          <div class="card-header">
            <span>报告验真</span>
          </div>
        </template>

        <el-form @submit.prevent="handleVerify" class="verify-form">
          <el-form-item label="验证码">
            <div class="verify-input-row">
              <el-input
                v-model="code"
                placeholder="请输入 12 位验证码"
                maxlength="12"
                @input="handleInput"
              />
              <el-button
                type="primary"
                :loading="loading"
                @click="handleVerify"
              >
                验证
              </el-button>
            </div>
          </el-form-item>
        </el-form>

        <!-- 验证结果 -->
        <div v-if="result" class="result">
          <el-alert
            :type="result.is_valid ? 'success' : 'error'"
            :title="result.message"
            show-icon
            :description="result.is_valid ? '此报告由 PrismaMate 出具且未被篡改' : '此报告可能已被篡改'"
          />

          <el-descriptions :column="1" border class="result-details" v-if="result.is_valid">
            <el-descriptions-item label="报告编号">{{ result.report_id }}</el-descriptions-item>
            <el-descriptions-item label="检测品牌">{{ result.brand_names?.join('、') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="检测关键词">{{ result.keywords?.join('、') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="检测平台">{{ result.platforms?.join('、') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="检测时间">{{ result.detection_time }}</el-descriptions-item>
            <el-descriptions-item label="报告哈希">
              <code class="hash-code">{{ (result.report_hash || '').substring(0, 24) }}...</code>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 错误结果 -->
        <div v-if="errorMessage" class="error-result">
          <el-alert type="error" :title="errorMessage" show-icon />
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'

const route = useRoute()

const code = ref('')
const loading = ref(false)
const result = ref<any>(null)
const errorMessage = ref('')

function handleInput() {
  code.value = code.value.toUpperCase()
  errorMessage.value = ''
}

async function handleVerify() {
  const inputCode = code.value.trim().toUpperCase()

  if (!inputCode) {
    errorMessage.value = '请输入验证码'
    result.value = null
    return
  }

  if (inputCode.length !== 12) {
    errorMessage.value = '验证码长度不正确，应为 12 位'
    result.value = null
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const res = await api.get(`/reports/verify/${inputCode}`)
    result.value = res.data
  } catch (error: any) {
    result.value = null
    const status = error.response?.status
    if (status === 429) {
      errorMessage.value = '验证请求过于频繁，请稍后再试'
    } else if (status === 404) {
      errorMessage.value = '报告未找到或验证码无效'
    } else {
      errorMessage.value = error.response?.data?.detail?.message || '验证失败，请稍后再试'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const queryCode = route.query.code as string
  const paramsCode = route.params.code as string

  if (queryCode) {
    code.value = queryCode.toUpperCase()
  } else if (paramsCode) {
    code.value = paramsCode.toUpperCase()
  }

  if (code.value) {
    handleVerify()
  }
})
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--foreground);
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.subtitle {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
}

.verify-card {
  /* 内部 el-card，与外层 page-container 配合使用 */
}

.verify-card :deep(.el-card__header) {
  padding: 20px 24px !important;
}

.verify-card :deep(.el-card__body) {
  padding: var(--card-padding) !important;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--foreground-secondary);
}

.verify-form {
  width: 100%;
}

.verify-form :deep(.el-form-item__label) {
  width: 120px !important;
  color: var(--text-label);
  font-size: 14px;
}

.verify-form :deep(.el-form-item__content) {
  justify-content: center;
}

.verify-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 420px;
}

.verify-input-row .el-input {
  flex: 1;
}

.result {
  margin-top: 20px;
}

.result :deep(.el-descriptions) {
  margin-top: 16px;
}

.result-details {
  margin-top: 20px;
}

.hash-code {
  font-family: var(--font-mono);
  font-size: 12px;
  background: var(--card-bg);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  color: var(--foreground);
}

.error-result {
  margin-top: 20px;
}

/* Alert 深色适配 */
:deep(.el-alert--success) {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
:deep(.el-alert--error) {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
}
</style>
