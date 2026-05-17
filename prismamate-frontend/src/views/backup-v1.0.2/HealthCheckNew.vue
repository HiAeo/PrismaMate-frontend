<template>
  <Layout>
    <div class="health-check-new-page">
      <!-- 页面标题 -->
      <div class="header">
        <h1>新建体检</h1>
        <p class="subtitle">配置检测参数，开始品牌 AI 可见度体检</p>
      </div>

      <!-- 检测表单 -->
      <div class="dash-card form-card">
        <el-form :model="form" label-position="top" class="detection-form">
          <!-- 品牌输入 -->
          <el-form-item label="品牌名称">
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
            <div class="form-hint">留空将使用默认品牌列表</div>
          </el-form-item>

          <!-- 关键词输入 -->
          <el-form-item label="检测关键词" required>
            <el-input
              v-model="form.keywordsInput"
              type="textarea"
              :rows="3"
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
          </el-form-item>

          <!-- 模板保存（可选） -->
          <el-form-item>
            <el-checkbox v-model="form.saveAsTemplate">保存为模板</el-checkbox>
          </el-form-item>

          <el-form-item v-if="form.saveAsTemplate" label="模板名称" required>
            <el-input
              v-model="form.templateName"
              placeholder="输入模板名称，如：华为月度体检"
              maxlength="100"
            />
            <div class="form-hint">保存后可在"我的模板"中快速复用</div>
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
              {{ isDetecting ? '检测中...' : '开始体检' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 结果区域 -->
      <div v-if="report" class="result-section">
        <el-divider content-position="center">
          <span style="color: rgba(255,255,255,0.4)">体检报告</span>
        </el-divider>

        <!-- 报告概览 -->
        <div class="dash-card report-overview">
          <div class="card-header-bar flex-between">
            <span>报告概览</span>
            <span class="status-tag tag-green">已生成</span>
          </div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="报告编号">
              {{ report.report_id }}
            </el-descriptions-item>
            <el-descriptions-item label="检测时间">
              {{ formatTime(report.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="品牌提及数">
              {{ report.total_mentions }}
            </el-descriptions-item>
            <el-descriptions-item label="引用来源">
              {{ report.total_citations }}
            </el-descriptions-item>
            <el-descriptions-item label="验证码">
              <span class="status-tag tag-orange">{{ report.verification_code }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="报告类型">
              <span class="status-tag tag-green">体检报告</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 对比提示（如果有历史报告） -->
        <div v-if="report.parent_report_id" class="dash-card comparison-hint">
          <div class="hint-content">
            <el-icon class="hint-icon"><Connection /></el-icon>
            <div class="hint-text">
              <h4>发现历史对比数据</h4>
              <p>本次体检已自动关联上一次同模板体检，可查看变化趋势</p>
            </div>
            <el-button type="primary" @click="$router.push(`/reports/${report.report_id}/comparison`)">
              查看对比
            </el-button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="actions">
          <el-button type="primary" @click="viewReport">
            查看详情
          </el-button>
          <el-button @click="resetForm">
            继续体检
          </el-button>
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
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import api from '@/api/axios'

const router = useRouter()

const form = reactive({
  brands: [] as string[],
  keywordsInput: '',
  platform: 'DeepSeek',
  saveAsTemplate: false,
  templateName: ''
})

const isDetecting = ref(false)
const report = ref<any>(null)
const error = ref('')

const availableBrands = ref<string[]>([
  '华为', '腾讯', '阿里巴巴', '百度', '字节跳动',
  '小米', '京东', '美团', '拼多多', '网易',
  'Google', 'Microsoft', 'Apple', 'Samsung', 'Meta'
])

const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const startDetection = async () => {
  const keywords = form.keywordsInput
    .split(/[\n,]/)
    .map(k => k.trim())
    .filter(k => k.length > 0)

  if (keywords.length === 0) {
    error.value = '请输入至少一个检测关键词'
    return
  }

  if (form.saveAsTemplate && !form.templateName.trim()) {
    error.value = '请输入模板名称'
    return
  }

  isDetecting.value = true
  error.value = ''

  try {
    let templateId: string | null = null
    if (form.saveAsTemplate) {
      const brandConfigs = form.brands.map(b => ({
        full_name: b,
        short_names: [b]
      }))

      const templateRes = await api.post(`/templates`, {
        name: form.templateName.trim(),
        brands: brandConfigs,
        keywords: keywords,
        platforms: [form.platform]
      })
      templateId = templateRes.template_id
      ElMessage.success('模板已保存')
    }

    const brandConfigs = form.brands.length > 0
      ? form.brands.map(b => ({ full_name: b, short_names: [b] }))
      : []

    const response = await api.post(`/detect/detect`, {
      keywords,
      brands: form.brands,
      platforms: [form.platform],
      report_type: 'health_check',
      template_id: templateId,
      save_as_template: false,
      brands_config: brandConfigs
    })

    report.value = response
    ElMessage.success('体检完成！')

  } catch (err: any) {
    const detail = err.response?.data?.detail
    if (detail && typeof detail === 'object') {
      error.value = detail.message || detail.error || '体检失败'
    } else {
      error.value = detail || err.message || '体检失败'
    }
    ElMessage.error(error.value)
  } finally {
    isDetecting.value = false
  }
}

const viewReport = () => {
  if (report.value?.report_id) {
    router.push(`/reports/${report.value.report_id}`)
  }
}

const resetForm = () => {
  report.value = null
  form.keywordsInput = ''
  error.value = ''
}

onMounted(() => {
  api.get(`/detect/brands`).then((data: any) => {
    if (data && data.brands) {
      availableBrands.value = data.brands
    }
  }).catch(err => {
    console.error('加载品牌列表失败', err)
  })
})
</script>

<style scoped>
.health-check-new-page {
  max-width: 800px;
  margin: 0 auto;
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

.form-card {
  margin-bottom: 20px;
}

.detection-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.result-section {
  margin-top: 20px;
}

.report-overview {
  margin-bottom: 20px;
}

.comparison-hint {
  margin-bottom: 20px;
  border-left: 4px solid #10B981;
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hint-icon {
  font-size: 32px;
  color: #10B981;
}

.hint-text {
  flex: 1;
}

.hint-text h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #FFFFFF;
}

.hint-text p {
  margin: 0;
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.error-alert {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  max-width: 600px;
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
</style>
