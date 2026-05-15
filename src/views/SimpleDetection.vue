<template>
  <div class="simple-detection">
    <!-- 导航栏 -->
    <el-menu mode="horizontal" :ellipsis="false" class="nav-menu">
      <el-menu-item index="0" @click="$router.push('/')">
        <el-icon><Monitor /></el-icon>
        <span>PrismaMate 棱镜</span>
      </el-menu-item>
      <div class="flex-grow" />

      <!-- 已登录用户 -->
      <template v-if="userStore.isLoggedIn">
        <el-menu-item index="user-info">
          <el-icon><User /></el-icon>
          {{ userStore.user?.username || userStore.user?.email }}
        </el-menu-item>
        <el-menu-item index="logout" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-menu-item>
      </template>

      <!-- 未登录用户 -->
      <template v-else>
        <el-menu-item index="login" @click="$router.push('/login')">
          <el-icon><User /></el-icon>
          登录
        </el-menu-item>
        <el-menu-item index="register" @click="$router.push('/register')">
          <el-button type="primary" size="small">注册</el-button>
        </el-menu-item>
      </template>

      <el-menu-item index="history" @click="showHistory = !showHistory">
        <el-icon><Clock /></el-icon>
        检测历史
      </el-menu-item>
    </el-menu>

    <div class="container">
      <!-- 登录提示 -->
      <el-alert
        v-if="!userStore.isLoggedIn && !loginTipDismissed"
        title="登录后可保存检测记录到您的账户"
        type="info"
        show-icon
        :closable="true"
        class="login-tip"
        @close="loginTipDismissed = true"
      >
        <template #default>
          <el-button type="primary" size="small" @click="$router.push('/login')">
            登录
          </el-button>
          <el-button size="small" @click="$router.push('/register')">
            注册
          </el-button>
          <el-button text size="small" @click="loginTipDismissed = true">
            跳过
          </el-button>
        </template>
      </el-alert>

      <!-- 输入区域 -->
      <div class="input-section">
        <h1 class="title">品牌检测</h1>
        <p class="subtitle">输入关键词，检测 AI 搜索中的品牌提及情况</p>

        <el-form :model="form" label-position="top" class="detection-form">
          <!-- 品牌输入 -->
          <el-form-item label="品牌名称（可选，不填则使用默认品牌列表）">
            <el-select
              v-model="form.brands"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入品牌名，按回车添加"
              style="width: 100%"
            >
              <el-option
                v-for="brand in availableBrands"
                :key="brand"
                :label="brand"
                :value="brand"
              />
            </el-select>
          </el-form-item>

          <!-- 关键词输入 -->
          <el-form-item label="检测关键词（必填）" required>
            <el-input
              v-model="form.keywordsInput"
              type="textarea"
              :rows="2"
              placeholder="输入检测关键词，多个关键词用换行分隔"
            />
          </el-form-item>

          <!-- AI 平台 -->
          <el-form-item label="AI 平台">
            <el-select v-model="form.platform" style="width: 100%">
              <el-option label="DeepSeek (深度求索)" value="DeepSeek" />
              <el-option label="Kimi (Moonshot AI)" value="Kimi" />
              <el-option label="豆包 (Doubao)" value="Doubao" />
            </el-select>
            <div class="platform-hint" v-if="platformInfo">
              <el-tag size="small" :type="platformInfo.mode === 'api' ? 'success' : 'warning'">
                {{ platformInfo.mode === 'api' ? 'API模式' : 'Browser模式' }}
              </el-tag>
              <span class="platform-status" v-if="platformInfo.status === 'production'">
                生产可用
              </span>
              <span class="platform-status beta" v-else>
                测试版
              </span>
            </div>
          </el-form-item>

          <!-- 开始检测按钮 -->
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="isDetecting"
              @click="startDetection"
              style="width: 100%"
            >
              <el-icon v-if="!isDetecting"><Search /></el-icon>
              {{ isDetecting ? '检测中...' : '开始检测' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 结果区域 -->
      <div v-if="report" class="result-section">
        <el-divider content-position="center">
          <el-icon><Document /></el-icon>
          检测结果
        </el-divider>

        <!-- 报告概览 -->
        <el-card class="report-overview" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>报告概览</span>
              <div>
                <el-tag v-if="report.task_id" type="info" size="small">
                  已关联账户
                </el-tag>
                <el-tag type="success">已生成</el-tag>
              </div>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="报告编号">
              {{ report.report_id }}
            </el-descriptions-item>
            <el-descriptions-item label="检测时间">
              {{ formatTime(report.detection_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="品牌提及数">
              {{ report.total_mentions }}
            </el-descriptions-item>
            <el-descriptions-item label="引用来源">
              {{ report.total_citations }}
            </el-descriptions-item>
            <el-descriptions-item label="验证码">
              <el-tag type="warning">{{ report.verification_code }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="报告哈希">
              <el-tooltip :content="report.report_hash" placement="top">
                <span class="hash-preview">{{ report.report_hash.substring(0, 16) }}...</span>
              </el-tooltip>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 品牌提及详情 -->
        <el-card class="brand-mentions" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>品牌提及详情</span>
              <el-tag>{{ report.brand_mentions?.length || 0 }} 条提及</el-tag>
            </div>
          </template>

          <el-table
            v-if="report.brand_mentions?.length > 0"
            :data="report.brand_mentions"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="brand_name" label="品牌" width="120" />
            <el-table-column prop="context" label="上下文" min-width="300">
              <template #default="{ row }">
                <span class="context-text">{{ row.context }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="sentiment" label="情感" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="getSentimentType(row.sentiment)"
                  size="small"
                >
                  {{ row.sentiment }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else description="未检测到品牌提及" />
        </el-card>

        <!-- 操作按钮 -->
        <div class="actions">
          <el-button type="primary" @click="downloadReport">
            <el-icon><Download /></el-icon>
            下载报告
          </el-button>
          <el-button @click="verifyReport">
            <el-icon><Stamp /></el-icon>
            验证报告
          </el-button>
          <el-button @click="resetForm">
            <el-icon><Refresh /></el-icon>
            重新检测
          </el-button>
        </div>
      </div>

      <!-- 检测历史 -->
      <div v-if="showHistory && history.length > 0" class="history-section">
        <el-divider content-position="center">
          <el-icon><Clock /></el-icon>
          检测历史
        </el-divider>

        <el-timeline>
          <el-timeline-item
            v-for="item in history"
            :key="item.report_id"
            :timestamp="formatTime(item.detection_time)"
            placement="top"
          >
            <el-card shadow="hover">
              <h4>{{ item.report_id }}</h4>
              <p>关键词: {{ item.keywords?.join(', ') }}</p>
              <p>品牌提及: {{ item.total_mentions }} 条</p>
              <el-button
                link
                type="primary"
                @click="loadReport(item)"
              >
                查看详情
              </el-button>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="error = ''"
      class="error-alert"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, Search, Document, Download, Clock, Refresh, Stamp, User, SwitchButton } from '@element-plus/icons-vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import api from '@/api/axios'

const router = useRouter()
const userStore = useUserStore()

// API 基础地址
const API_BASE = '/api/v1'

// 表单数据
const form = reactive({
  brands: [] as string[],
  keywordsInput: '',
  platform: 'DeepSeek'
})

// 状态
const isDetecting = ref(false)
const report = ref<any>(null)
const error = ref('')
const showHistory = ref(false)
const history = ref<any[]>([])
const loginTipDismissed = ref(false)

// 可用品牌列表
const availableBrands = ref<string[]>([
  '华为', '腾讯', '阿里巴巴', '百度', '字节跳动',
  '小米', '京东', '美团', '拼多多', '网易',
  'Google', 'Microsoft', 'Apple', 'Samsung', 'Meta'
])

// 平台信息
const platformInfo = ref<any>(null)

// 获取平台信息
const loadPlatformInfo = async () => {
  try {
    const res = await axios.get(`${API_BASE}/detect/platforms`)
    if (res.data?.platforms?.[form.platform]) {
      platformInfo.value = res.data.platforms[form.platform]
    }
  } catch (err) {
    console.error('加载平台信息失败', err)
  }
}

// 创建带认证的 axios 实例
const createAuthAxios = () => {
  const instance = axios.create({
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })
  if (userStore.token) {
    instance.defaults.headers.common['Authorization'] = `Bearer ${userStore.token}`
  }
  return instance
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 获取情感标签类型
const getSentimentType = (sentiment: string) => {
  switch (sentiment) {
    case 'positive': return 'success'
    case 'negative': return 'danger'
    case 'neutral': return 'info'
    default: return 'info'
  }
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/')
}

// 开始检测
const startDetection = async () => {
  // 解析关键词
  const keywords = form.keywordsInput
    .split(/[\n,]/)
    .map(k => k.trim())
    .filter(k => k.length > 0)

  if (keywords.length === 0) {
    error.value = '请输入至少一个检测关键词'
    return
  }

  isDetecting.value = true
  error.value = ''

  try {
    const authApi = createAuthAxios()
    const response = await authApi.post(`${API_BASE}/detect/detect`, {
      keywords,
      brands: form.brands,
      platform: form.platform
    })

    report.value = response.data

    // 添加到历史记录
    history.value.unshift({
      report_id: report.value.report_id,
      detection_time: report.value.detection_time,
      keywords,
      total_mentions: report.value.total_mentions,
      brand_mentions: report.value.brand_mentions
    })

    // 保存到 localStorage
    localStorage.setItem('detection_history', JSON.stringify(history.value))

    ElMessage.success('检测完成！')
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '检测失败'
    ElMessage.error(error.value)
  } finally {
    isDetecting.value = false
  }
}

// 下载报告
const downloadReport = () => {
  if (!report.value?.report_html) {
    ElMessage.warning('报告 HTML 未生成')
    return
  }

  // 创建下载
  const blob = new Blob([report.value.report_html], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${report.value.report_id}.html`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('报告已下载')
}

// 验证报告
const verifyReport = () => {
  if (!report.value) return
  // 跳转到验证页面
  window.open(`/verify/${report.value.verification_code}`, '_blank')
}

// 重新检测
const resetForm = () => {
  report.value = null
  form.keywordsInput = ''
  error.value = ''
}

// 加载历史报告
const loadReport = (item: any) => {
  report.value = item
  showHistory.value = false
}

// 初始化
onMounted(() => {
  // 加载历史记录
  const savedHistory = localStorage.getItem('detection_history')
  if (savedHistory) {
    try {
      history.value = JSON.parse(savedHistory)
    } catch (e) {
      console.error('加载历史记录失败', e)
    }
  }

  // 加载默认品牌列表
  axios.get(`${API_BASE}/detect/brands`).then(res => {
    if (res.data.brands) {
      availableBrands.value = res.data.brands
    }
  }).catch(err => {
    console.error('加载品牌列表失败', err)
  })

  // 加载平台信息
  loadPlatformInfo()
})

// 监听平台变化
watch(() => form.platform, () => {
  loadPlatformInfo()
})
</script>

<style scoped>
.simple-detection {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.nav-menu {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.flex-grow {
  flex-grow: 1;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.login-tip {
  margin-bottom: 24px;
}

.title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  text-align: center;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 16px;
  color: #909399;
  text-align: center;
  margin-bottom: 40px;
}

.input-section {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.detection-form {
  max-width: 600px;
  margin: 0 auto;
}

.result-section {
  margin-top: 40px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-overview {
  margin-bottom: 20px;
}

.brand-mentions {
  margin-bottom: 20px;
}

.context-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.hash-preview {
  font-family: monospace;
  color: #909399;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.history-section {
  margin-top: 40px;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-alert {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  max-width: 600px;
}

::deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
