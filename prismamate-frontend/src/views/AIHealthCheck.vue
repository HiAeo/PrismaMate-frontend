<template>
  <Layout>
    <div class="page-container ai-health-check">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>PrismaMate 棱镜AI品牌可见度体检</h1>
      <p class="subtitle">一键检测在 DeepSeek、豆包等主流 AI 平台上的自然可见度，并获取包含提及率、引用位次、信源分析等维度的完整报告。支持创建体检模板，定期复查，自动与历史报告对比，发现趋势变化。</p>
    </div>

    <!-- 检测表单 -->
    <div v-if="!report" class="check-form">
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>{{ t('aiHealthCheck.formTitle') }}</span>
          </div>
        </template>

        <!-- 品牌选择 -->
        <el-form :model="form" label-width="120px">
          <el-form-item :label="t('aiHealthCheck.selectBrand')">
            <el-select
              v-model="selectedProfileId"
              :placeholder="t('aiHealthCheck.selectBrandPlaceholder')"
              filterable
              style="width: 100%"
              @change="onProfileChange"
            >
              <el-option
                v-for="profile in profiles"
                :key="profile.id"
                :label="profile.company_name"
                :value="profile.id"
              />
            </el-select>
          </el-form-item>

          <!-- 已选品牌信息预览 -->
          <div v-if="selectedProfile" class="profile-preview">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item :label="t('brandHub.brandNames')">
                {{ selectedProfile.brand_names.join(', ') }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('brandHub.website')">
                <a :href="selectedProfile.website" target="_blank" class="link">
                  {{ selectedProfile.website }}
                </a>
              </el-descriptions-item>
              <el-descriptions-item :label="t('brandHub.keywords')" :span="2">
                <el-tag
                  v-for="kw in selectedProfile.keywords"
                  :key="kw"
                  size="small"
                  type="info"
                  class="mr-1"
                >
                  {{ kw }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 关键词选择 -->
          <el-form-item :label="t('aiHealthCheck.keywords')">
            <div class="keywords-section">
              <el-tag
                v-for="kw in selectedKeywords"
                :key="kw"
                closable
                @close="removeKeyword(kw)"
                class="keyword-tag"
              >
                {{ kw }}
              </el-tag>
              <el-select
                v-model="keywordInput"
                :placeholder="t('aiHealthCheck.addKeywordPlaceholder')"
                filterable
                allow-create
                default-first-option
                class="keyword-select"
                @change="addKeyword"
              >
                <el-option
                  v-for="kw in availableKeywords"
                  :key="kw"
                  :label="kw"
                  :value="kw"
                  :disabled="selectedKeywords.includes(kw)"
                />
              </el-select>
            </div>
          </el-form-item>

          <!-- 平台选择 -->
          <el-form-item :label="t('aiHealthCheck.platforms')">
            <el-checkbox-group v-model="selectedPlatforms">
              <el-checkbox label="DeepSeek">{{ t('platforms.deepseek') }}</el-checkbox>
              <el-checkbox label="Kimi">{{ t('platforms.kimi') }}</el-checkbox>
              <el-checkbox label="Doubao">{{ t('platforms.doubao') }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <el-button class="btn-secondary-action" @click="$router.push('/brand-hub')">
            <el-icon><Edit /></el-icon>
            {{ t('aiHealthCheck.goToBrandHub') }}
          </el-button>
          <el-button
            type="primary"
            :loading="detecting"
            :disabled="!canStartDetection"
            @click="startDetection"
          >
            {{ t('aiHealthCheck.startCheck') }}
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 检测进度 -->
    <div v-if="detecting" class="detecting-section">
      <el-card>
        <div class="detecting-content">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <span>{{ t('aiHealthCheck.detecting') }}...</span>
          <p class="current-keyword" v-if="currentKeyword">
            {{ t('aiHealthCheck.currentKeyword') }}: {{ currentKeyword }}
          </p>
        </div>
      </el-card>
    </div>

    <!-- 报告展示 -->
    <div v-if="report" class="report-section">
      <el-card>
        <template #header>
          <div class="report-header">
            <span>{{ t('aiHealthCheck.reportTitle') }}</span>
            <el-button @click="resetForm">
              {{ t('aiHealthCheck.newCheck') }}
            </el-button>
          </div>
        </template>

        <!-- 报告摘要 -->
        <div class="report-summary">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ report.total_mentions }}</div>
                <div class="metric-label">{{ t('aiHealthCheck.totalMentions') }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ report.total_citations }}</div>
                <div class="metric-label">{{ t('aiHealthCheck.totalCitations') }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ report.keywords.length }}</div>
                <div class="metric-label">{{ t('aiHealthCheck.keywordsCount') }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ report.platforms.join(', ') }}</div>
                <div class="metric-label">{{ t('aiHealthCheck.platforms') }}</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 品牌提及列表 -->
        <div class="mentions-section">
          <h3>{{ t('aiHealthCheck.brandMentions') }}</h3>
          <el-table :data="report.brand_mentions" stripe style="width: 100%">
            <el-table-column prop="brand_name" :label="t('aiHealthCheck.brandName')" min-width="120" />
            <el-table-column prop="canonical_name" :label="t('aiHealthCheck.canonicalName')" min-width="120" />
            <el-table-column prop="context" :label="t('aiHealthCheck.context')" min-width="200">
              <template #default="{ row }">
                <span class="context-text">{{ row.context }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="sentiment" :label="t('aiHealthCheck.sentiment')" min-width="100">
              <template #default="{ row }">
                <el-tag :type="getSentimentType(row.sentiment)" size="small">
                  {{ row.sentiment }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 报告信息 -->
        <div class="report-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item :label="t('aiHealthCheck.reportId')">
              {{ report.report_id }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('aiHealthCheck.verificationCode')">
              {{ report.verification_code }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>
    </div>

    <!-- 无品牌提示 -->
    <div v-if="!loading && profiles.length === 0 && !report" class="no-profile">
      <el-empty :description="t('aiHealthCheck.noBrandProfile')">
        <el-button type="primary" @click="$router.push('/brand-hub')">
          {{ t('aiHealthCheck.createBrandFirst') }}
        </el-button>
      </el-empty>
    </div>
  </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Edit } from '@element-plus/icons-vue'
import { useI18n } from '@/composables/useI18n'
import Layout from '@/components/Layout.vue'
import { brandHubApi, BrandProfile } from '@/api/brandHub'
import { detectApi } from '@/api/detect'

const { t } = useI18n()

// 数据
const loading = ref(false)
const detecting = ref(false)
const profiles = ref<BrandProfile[]>([])
const selectedProfileId = ref<number | null>(null)
const selectedProfile = ref<BrandProfile | null>(null)
const selectedKeywords = ref<string[]>([])
const keywordInput = ref('')
const selectedPlatforms = ref<string[]>(['DeepSeek'])
const currentKeyword = ref('')
const report = ref<any>(null)

// 表单
const form = reactive({
  keywords: [] as string[],
  brands: [] as string[],
  platform: 'DeepSeek'
})

// 计算属性
const availableKeywords = computed(() => {
  if (!selectedProfile.value) return []
  return selectedProfile.value.keywords.filter(k => !selectedKeywords.value.includes(k))
})

const canStartDetection = computed(() => {
  return selectedProfileId.value && selectedKeywords.value.length > 0 && selectedPlatforms.value.length > 0
})

// 方法
function onProfileChange(profileId: number) {
  selectedProfile.value = profiles.value.find(p => p.id === profileId) || null
  selectedKeywords.value = selectedProfile.value?.keywords.slice(0, 3) || []
}

function addKeyword(keyword: string) {
  if (keyword && !selectedKeywords.value.includes(keyword)) {
    selectedKeywords.value.push(keyword)
  }
  keywordInput.value = ''
}

function removeKeyword(keyword: string) {
  const index = selectedKeywords.value.indexOf(keyword)
  if (index > -1) {
    selectedKeywords.value.splice(index, 1)
  }
}

async function startDetection() {
  if (!canStartDetection.value) return

  detecting.value = true
  report.value = null

  try {
    const response = await detectApi.detect({
      keywords: selectedKeywords.value,
      brands: selectedProfile.value?.brand_names || [],
      platform: selectedPlatforms.value[0]
    })
    report.value = response.data
    ElMessage.success(t('aiHealthCheck.checkComplete'))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || t('aiHealthCheck.checkFailed'))
  } finally {
    detecting.value = false
    currentKeyword.value = ''
  }
}

function resetForm() {
  report.value = null
  selectedProfileId.value = null
  selectedProfile.value = null
  selectedKeywords.value = []
  keywordInput.value = ''
  selectedPlatforms.value = ['DeepSeek']
}

function getSentimentType(sentiment: string) {
  switch (sentiment.toLowerCase()) {
    case 'positive': return 'success'
    case 'negative': return 'danger'
    case 'neutral': return 'info'
    default: return 'info'
  }
}

// 加载品牌数据
async function loadProfiles() {
  loading.value = true
  try {
    const res = await brandHubApi.list()
    profiles.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('Failed to load profiles:', error)
    profiles.value = []
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadProfiles()
})
</script>

<style scoped>
/* .ai-health-check 容器样式已移至 global.css .page-container */

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
}

.form-card {
  width: 100%;
}

.form-card :deep(.el-card__header) {
  font-weight: 500;
  font-size: var(--text-lg);
  color: var(--foreground-secondary);
}

.profile-preview {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--hover-bg);
  border-radius: var(--input-radius);
}

.link {
  color: var(--primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.keywords-section {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-height: var(--input-height);
}

.keyword-tag {
  margin: 0;
}

.keyword-select {
  width: 160px;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.btn-secondary-action {
  height: var(--input-height) !important;
  background: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  border-radius: var(--input-radius) !important;
  color: var(--text-label) !important;
  font-size: var(--text-base) !important;
  font-weight: 500 !important;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 24px !important;
  transition: all var(--transition-fast) !important;
}

.btn-secondary-action:hover {
  border-color: var(--primary) !important;
  color: var(--primary) !important;
}

.detecting-section {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.detecting-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  text-align: center;
}

.current-keyword {
  margin-top: 16px;
  color: var(--text-muted);
}

.report-section {
  width: 100%;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
  font-weight: 500;
  font-size: var(--text-lg);
  color: var(--foreground-secondary);
}

.report-summary {
  margin-bottom: 32px;
}

.metric-card {
  background: var(--hover-bg);
  border-radius: var(--input-radius);
  padding: 20px;
  text-align: center;
}

.metric-value {
  font-size: var(--text-4xl);
  font-weight: 600;
  color: var(--foreground);
  margin-bottom: 8px;
}

.metric-label {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.mentions-section {
  margin-bottom: 24px;
}

.mentions-section h3 {
  margin-bottom: 16px;
  font-size: var(--text-lg);
  font-weight: 500;
}

.context-text {
  display: inline-block;
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.report-info {
  margin-top: 24px;
}

.no-profile {
  padding: 80px 0;
}
</style>
