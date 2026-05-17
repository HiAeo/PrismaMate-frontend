<template>
  <Layout>
    <div class="page-container geo-verification">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>PrismaMate 棱镜GEO 生成式引擎优化效果监测</h1>
      <p class="subtitle">输入优化关键词和目标平台，PrismaMate 将实时检测并生成独立报告，同时支持上传 GEO 机构的交付数据，进行逐项差异对比，标注"一致/有差异/超出覆盖范围"，让乙方承诺的效果一目了然。</p>
    </div>

    <!-- 检测表单 -->
    <div v-if="!report" class="verification-form">
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>{{ t('geoVerification.formTitle') }}</span>
          </div>
        </template>

        <el-form :model="form" label-width="120px">
          <!-- 场景选择 -->
          <el-form-item :label="t('geoVerification.scenario')">
            <el-radio-group v-model="form.scenario">
              <el-radio label="progress">{{ t('geoVerification.scenarioProgress') }}</el-radio>
              <el-radio label="delivery">{{ t('geoVerification.scenarioDelivery') }}</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 品牌选择 -->
          <el-form-item :label="t('geoVerification.selectBrand')">
            <el-select
              v-model="selectedProfileId"
              :placeholder="t('geoVerification.selectBrandPlaceholder')"
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

          <!-- 核心语义词 -->
          <el-form-item :label="t('geoVerification.keywords')">
            <div class="keywords-section">
              <el-tag
                v-for="kw in selectedKeywords"
                :key="kw"
                closable
                @close="removeKeyword(kw)"
                type="info"
                class="keyword-tag"
              >
                {{ kw }}
              </el-tag>
              <el-select
                v-model="keywordInput"
                :placeholder="t('geoVerification.addKeywordPlaceholder')"
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

          <!-- GEO数据输入 -->
          <el-form-item :label="t('geoVerification.geoData')">
            <el-input
              v-model="form.geoData"
              type="textarea"
              :rows="6"
              :placeholder="t('geoVerification.geoDataPlaceholder')"
            />
            <div class="form-tip">
              {{ t('geoVerification.geoDataTip') }}
            </div>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <el-button class="btn-secondary-action" @click="$router.push('/brand-hub')">
            <el-icon><Edit /></el-icon>
            {{ t('geoVerification.goToBrandHub') }}
          </el-button>
          <el-button
            type="primary"
            :loading="verifying"
            :disabled="!canStartVerification"
            @click="startVerification"
          >
            {{ t('geoVerification.startVerify') }}
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 验证进度 -->
    <div v-if="verifying" class="verifying-section">
      <el-card>
        <div class="verifying-content">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <span>{{ t('geoVerification.verifying') }}...</span>
        </div>
      </el-card>
    </div>

    <!-- 报告展示 -->
    <div v-if="report" class="report-section">
      <el-card>
        <template #header>
          <div class="report-header">
            <span>{{ t('geoVerification.reportTitle') }}</span>
            <el-button @click="resetForm">
              {{ t('geoVerification.newVerification') }}
            </el-button>
          </div>
        </template>

        <!-- 验证结果汇总 -->
        <div class="result-summary">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="result-card">
                <div class="result-value" style="color: #67C23A;">{{ report.match_count || 0 }}</div>
                <div class="result-label">{{ t('geoVerification.matchCount') }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-card">
                <div class="result-value" style="color: #E6A23C;">{{ report.diff_count || 0 }}</div>
                <div class="result-label">{{ t('geoVerification.diffCount') }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-card">
                <div class="result-value" style="color: #909399;">{{ report.out_of_range_count || 0 }}</div>
                <div class="result-label">{{ t('geoVerification.outOfRangeCount') }}</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 详细对比 -->
        <div class="comparison-section">
          <h3>{{ t('geoVerification.comparisonDetails') }}</h3>
          <el-table :data="report.items || []" stripe style="width: 100%">
            <el-table-column prop="keyword" :label="t('geoVerification.keyword')" width="120" />
            <el-table-column prop="platform" :label="t('geoVerification.platform')" width="100" />
            <el-table-column prop="expected" :label="t('geoVerification.expected')" width="120">
              <template #default="{ row }">
                {{ row.expected ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual" :label="t('geoVerification.actual')" width="120">
              <template #default="{ row }">
                {{ row.actual ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="t('geoVerification.status')" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" :label="t('geoVerification.notes')">
              <template #default="{ row }">
                {{ row.notes || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 无品牌提示 -->
    <div v-if="!loading && profiles.length === 0 && !report" class="no-profile">
      <el-empty :description="t('geoVerification.noBrandProfile')">
        <el-button type="primary" @click="$router.push('/brand-hub')">
          {{ t('geoVerification.createBrandFirst') }}
        </el-button>
      </el-empty>
    </div>
  </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Edit } from '@element-plus/icons-vue'
import { useI18n } from '@/composables/useI18n'
import Layout from '@/components/Layout.vue'
import { brandHubApi, BrandProfile } from '@/api/brandHub'

const { t } = useI18n()

// 数据
const loading = ref(false)
const verifying = ref(false)
const profiles = ref<BrandProfile[]>([])
const selectedProfileId = ref<number | null>(null)
const selectedProfile = ref<BrandProfile | null>(null)
const selectedKeywords = ref<string[]>([])
const keywordInput = ref('')
const report = ref<any>(null)

// 表单
const form = reactive({
  scenario: 'progress',
  geoData: ''
})

// 计算属性
const availableKeywords = computed(() => {
  if (!selectedProfile.value) return []
  return selectedProfile.value.keywords.filter(k => !selectedKeywords.value.includes(k))
})

const canStartVerification = computed(() => {
  return selectedProfileId.value && selectedKeywords.value.length > 0 && form.geoData.trim().length > 0
})

// 方法
function onProfileChange(profileId: number) {
  selectedProfile.value = profiles.value.find(p => p.id === profileId) || null
  selectedKeywords.value = selectedProfile.value?.keywords.slice(0, 5) || []
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

async function startVerification() {
  if (!canStartVerification.value) return

  verifying.value = true
  report.value = null

  try {
    // TODO: 调用 GEO 验证 API
    // 这里模拟一个报告结果
    report.value = {
      match_count: 3,
      diff_count: 2,
      out_of_range_count: 1,
      items: selectedKeywords.value.map((kw, index) => ({
        keyword: kw,
        platform: 'DeepSeek',
        expected: `提及率 ${(Math.random() * 30 + 10).toFixed(1)}%`,
        actual: `提及率 ${(Math.random() * 30 + 10).toFixed(1)}%`,
        status: index % 3 === 0 ? 'match' : index % 3 === 1 ? 'diff' : 'out_of_range',
        notes: index % 3 === 0 ? '' : '实际检测结果与声称数据存在差异'
      }))
    }
    ElMessage.success(t('geoVerification.verifyComplete'))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || t('geoVerification.verifyFailed'))
  } finally {
    verifying.value = false
  }
}

function resetForm() {
  report.value = null
  selectedProfileId.value = null
  selectedProfile.value = null
  selectedKeywords.value = []
  keywordInput.value = ''
  form.geoData = ''
  form.scenario = 'progress'
}

function getStatusType(status: string) {
  switch (status) {
    case 'match': return 'success'
    case 'diff': return 'warning'
    case 'out_of_range': return 'info'
    default: return 'info'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'match': return t('geoVerification.statusMatch')
    case 'diff': return t('geoVerification.statusDiff')
    case 'out_of_range': return t('geoVerification.statusOutOfRange')
    default: return status
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
/* .geo-verification 容器样式已移至 global.css .page-container */

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

.form-tip {
  margin-top: 8px;
  font-size: var(--text-sm);
  color: var(--text-muted);
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

.verifying-section {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.verifying-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  text-align: center;
  gap: 16px;
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

.result-summary {
  margin-bottom: 32px;
}

.result-card {
  background: var(--hover-bg);
  border-radius: var(--input-radius);
  padding: 20px;
  text-align: center;
}

.result-value {
  font-size: var(--text-4xl);
  font-weight: 600;
  margin-bottom: 8px;
}

.result-label {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.comparison-section {
  margin-bottom: 24px;
}

.comparison-section h3 {
  margin-bottom: 16px;
  font-size: var(--text-lg);
  font-weight: 500;
}

.no-profile {
  padding: 80px 0;
}
</style>
