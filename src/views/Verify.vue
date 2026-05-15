<template>
  <div class="verify-container">
    <el-card class="verify-card">
      <template #header>
        <div class="card-header">
          <el-icon><Stamp /></el-icon>
          <span>报告验证</span>
        </div>
      </template>
      
      <el-form @submit.prevent="handleVerify">
        <el-form-item label="验证码">
          <el-input 
            v-model="code" 
            placeholder="请输入 12 位验证码" 
            size="large" 
            maxlength="12"
            @input="handleInput"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            style="width: 100%" 
            @click="handleVerify"
          >
            验证
          </el-button>
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
            <el-tooltip :content="result.report_hash" placement="top">
              <code class="hash-code">{{ result.report_hash?.substring(0, 24) }}...</code>
            </el-tooltip>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 错误结果 -->
      <div v-if="errorMessage" class="error-result">
        <el-alert type="error" :title="errorMessage" show-icon />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'
import { Stamp } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface VerifyResult {
  valid: boolean
  is_valid: boolean
  message: string
  report_id: string
  verification_code: string
  brand_names: string[]
  keywords: string[]
  platforms: string[]
  detection_time: string
  report_hash: string
  hash_verified: boolean
  rate_limit_remaining: number
}

const route = useRoute()
const router = useRouter()

const code = ref('')
const loading = ref(false)
const result = ref<VerifyResult | null>(null)
const errorMessage = ref('')

function handleInput() {
  // 自动将输入转为大写
  code.value = code.value.toUpperCase()
  // 清除错误信息
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
    // axios 拦截器已返回 response.data，直接使用
    const data = await api.get(`/reports/verify/${inputCode}`)
    result.value = data
    errorMessage.value = ''
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

// 监听路由变化（支持 URL 参数变化）
onMounted(() => {
  // 优先使用 query 参数，其次使用 params
  const queryCode = route.query.code as string
  const paramsCode = route.params.code as string
  
  if (queryCode) {
    code.value = queryCode.toUpperCase()
  } else if (paramsCode) {
    code.value = paramsCode.toUpperCase()
  }
  
  // 如果有验证码，自动验证
  if (code.value) {
    handleVerify()
  }
})
</script>

<style scoped>
.verify-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.verify-card {
  width: 100%;
  max-width: 550px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
}

.result {
  margin-top: 20px;
}

.result-details {
  margin-top: 20px;
}

.hash-code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.error-result {
  margin-top: 20px;
}
</style>
