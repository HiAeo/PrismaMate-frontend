<template>
  <Layout>
    <div class="page-container brand-hub">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>PrismaMate 棱镜AI品牌智库</h1>
        <p class="subtitle">创建您的企业品牌信息，作为所有检测报告的数据依据，让报告更准确。我们相信，只有真实的数据，才能推动行业走向透明和健康。PrismaMate 棱镜报告，坚持不做 GEO 优化，只做 GEO 的镜子。</p>
      </div>

      <!-- ====== 列表视图 ====== -->
      <div v-if="viewMode === 'list'" class="brand-list" v-loading="loading">
        <!-- 空状态 -->
        <div v-if="!loading && profiles.length === 0" class="empty-state">
          <el-empty :description="t('brandHub.empty')">
            <el-button type="primary" @click="enterCreateMode">
              {{ t('brandHub.createFirst') }}
            </el-button>
          </el-empty>
        </div>

        <!-- 有数据：标题行 + 品牌卡片 -->
        <template v-else>
          <div class="list-toolbar">
            <span class="list-count">共 {{ profiles.length }} 个品牌档案</span>
            <el-button type="primary" @click="enterCreateMode">
              <el-icon><Plus /></el-icon>
              {{ t('brandHub.addNew') }}
            </el-button>
          </div>

          <div class="brand-cards">
            <div v-for="profile in profiles" :key="profile.id" class="brand-card">
              <div class="card-header">
                <h3>{{ profile.company_name }}</h3>
                <div class="card-actions">
                  <el-button text @click="enterEditMode(profile)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button text type="danger" @click="handleDelete(profile.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>

              <div class="card-body">
                <div class="info-item">
                  <span class="label">{{ t('brandHub.brandNames') }}:</span>
                  <el-tag v-for="name in profile.brand_names" :key="name" size="small" class="mx-1">
                    {{ name }}
                  </el-tag>
                </div>
                <div class="info-item">
                  <span class="label">{{ t('brandHub.website') }}:</span>
                  <a :href="profile.website" target="_blank" class="link">{{ profile.website }}</a>
                </div>
                <div class="info-item">
                  <span class="label">{{ t('brandHub.products') }}:</span>
                  <span>{{ profile.products }}</span>
                </div>
                <div class="info-item" v-if="profile.keywords.length">
                  <span class="label">{{ t('brandHub.keywords') }}:</span>
                  <div class="keywords-wrap">
                    <el-tag v-for="kw in profile.keywords" :key="kw" size="small" type="info">
                      {{ kw }}
                    </el-tag>
                  </div>
                </div>
                <div class="info-item" v-if="profile.competitors.length">
                  <span class="label">{{ t('brandHub.competitors') }}:</span>
                  <el-tag v-for="cp in profile.competitors" :key="cp" size="small" type="warning">
                    {{ cp }}
                  </el-tag>
                </div>
              </div>

              <div class="card-footer">
                <span class="update-time">
                  {{ t('brandHub.updatedAt') }}: {{ formatDate(profile.updated_at) }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- ====== 表单视图（新建/编辑）====== -->
      <div v-else class="brand-form-wrapper">
        <div class="form-header">
          <h2>{{ isEditing ? t('brandHub.editTitle') : t('brandHub.createTitle') }}</h2>
          <el-button text @click="backToList">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>

        <el-form ref="formRef" :model="form" label-width="120px" label-position="left" class="brand-form">
          <el-form-item :label="t('brandHub.companyName')">
            <el-input v-model="form.company_name" :placeholder="t('brandHub.companyNamePlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('brandHub.brandNames')">
            <div class="dynamic-input-list">
              <div v-for="(name, index) in form.brand_names" :key="index" class="dynamic-input-row">
                <el-input v-model="form.brand_names[index]" :placeholder="t('brandHub.addBrandName')" />
                <el-button text class="remove-btn" @click="removeBrandName(index)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <el-button class="add-input-btn" @click="addBrandName">
                <el-icon><Plus /></el-icon>
                {{ t('common.add') }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item :label="t('brandHub.website')">
            <el-input v-model="form.website" placeholder="https://example.com" />
          </el-form-item>

          <el-form-item :label="t('brandHub.products')">
            <el-input v-model="form.products" type="textarea" :rows="2" :placeholder="t('brandHub.productsPlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('brandHub.description')">
            <el-input v-model="form.description" type="textarea" :rows="3" :placeholder="t('brandHub.descriptionPlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('brandHub.keywords')">
            <div class="dynamic-input-list">
              <div v-for="(kw, index) in form.keywords" :key="index" class="dynamic-input-row">
                <el-input v-model="form.keywords[index]" :placeholder="t('brandHub.addKeyword')" />
                <el-button text class="remove-btn" @click="removeKeyword(index)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <el-button class="add-input-btn" @click="addKeyword">
                <el-icon><Plus /></el-icon>
                {{ t('common.add') }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item :label="t('brandHub.competitors')">
            <div class="dynamic-input-list">
              <div v-for="(cp, index) in form.competitors" :key="index" class="dynamic-input-row">
                <el-input v-model="form.competitors[index]" :placeholder="t('brandHub.addCompetitor')" />
                <el-button text class="remove-btn" @click="removeCompetitor(index)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <el-button class="add-input-btn" @click="addCompetitor">
                <el-icon><Plus /></el-icon>
                {{ t('common.add') }}
              </el-button>
            </div>
          </el-form-item>

          <div class="form-actions">
            <el-button @click="backToList">{{ t('common.cancel') }}</el-button>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">
              {{ t('common.save') }}
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete, ArrowLeft, Close } from '@element-plus/icons-vue'
import { useI18n } from '@/composables/useI18n'
import Layout from '@/components/Layout.vue'
import { brandHubApi, BrandProfile, CreateBrandProfile } from '@/api/brandHub'

const { t } = useI18n()

// 视图模式：list | form
const viewMode = ref<'list' | 'form'>('list')

// 数据
const loading = ref(false)
const submitting = ref(false)
const profiles = ref<BrandProfile[]>([])
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

// 表单
const form = reactive<CreateBrandProfile>({
  company_name: '',
  brand_names: [''],
  website: '',
  products: '',
  description: '',
  keywords: [''],
  competitors: ['']
})

// 加载数据
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

// 进入创建模式
function enterCreateMode() {
  resetForm()
  viewMode.value = 'form'
}

// 进入编辑模式
function enterEditMode(profile: BrandProfile) {
  isEditing.value = true
  editingId.value = profile.id
  form.company_name = profile.company_name
  form.brand_names = profile.brand_names.length ? [...profile.brand_names] : ['']
  form.website = profile.website
  form.products = profile.products
  form.description = profile.description || ''
  form.keywords = profile.keywords.length ? [...profile.keywords] : ['']
  form.competitors = profile.competitors.length ? [...profile.competitors] : ['']
  viewMode.value = 'form'
}

// 返回列表
function backToList() {
  viewMode.value = 'list'
  resetForm()
}

// 动态添加方法
function addBrandName() {
  form.brand_names.push('')
}

function removeBrandName(index: number) {
  form.brand_names.splice(index, 1)
}

function addKeyword() {
  form.keywords.push('')
}

function removeKeyword(index: number) {
  form.keywords.splice(index, 1)
}

function addCompetitor() {
  form.competitors.push('')
}

function removeCompetitor(index: number) {
  form.competitors.splice(index, 1)
}

// 重置表单
function resetForm() {
  form.company_name = ''
  form.brand_names = ['']
  form.website = ''
  form.products = ''
  form.description = ''
  form.keywords = ['']
  form.competitors = ['']
  editingId.value = null
  isEditing.value = false
}

// 删除
async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm(
      t('brandHub.deleteConfirm'),
      t('common.warning'),
      { type: 'warning' }
    )
    await brandHubApi.delete(id)
    ElMessage.success(t('brandHub.deleteSuccess'))
    loadProfiles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(t('brandHub.deleteFailed'))
    }
  }
}

// 提交
async function handleSubmit() {
  submitting.value = true
  try {
    const payload = {
      ...form,
      brand_names: form.brand_names.filter((s: string) => s.trim() !== ''),
      keywords: form.keywords.filter((s: string) => s.trim() !== ''),
      competitors: form.competitors.filter((s: string) => s.trim() !== ''),
    }
    if (isEditing.value && editingId.value) {
      await brandHubApi.update(editingId.value, payload)
      ElMessage.success(t('brandHub.updateSuccess'))
    } else {
      await brandHubApi.create(payload)
      ElMessage.success(t('brandHub.createSuccess'))
    }
    backToList()
    loadProfiles()
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    submitting.value = false
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

// 初始化
onMounted(() => {
  loadProfiles()
})
</script>

<style scoped>
/* 全局容器样式已移至 global.css .page-container，后续新增页面自动复用，无需在此重复定义 */

/* ========== 页面标题 ========== */
.page-header,
.header {
  margin-bottom: 24px;
}

.page-header h1,
.header h1 {
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

/* ========== 通用卡片规范 ========== */
.dash-card,
.brand-form,
.form-card,
.verify-card,
.info-card {
  background: var(--card-bg);
  border: var(--card-border);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
}

/* ========== 列表视图 ========== */
.list-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-count {
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.brand-list {
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.brand-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.brand-card {
  background: var(--card-bg);
  border: var(--card-border);
  border-radius: var(--card-radius);
  padding: 24px 28px;
  transition: all 0.3s;
  min-height: 200px;
}

.brand-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* ========== 卡片头部 ========== */
.card-header,
.card-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.card-header-bar {
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--foreground-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* ========== 卡片内容 ========== */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: var(--text-base);
}

.info-item .label {
  color: var(--text-label);
  min-width: 120px;
  flex-shrink: 0;
  font-size: 14px;
  text-align: left;
  white-space: nowrap;
}

.info-item span:not(.label):not(.link) {
  color: var(--foreground);
}

.link {
  color: var(--primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.keywords-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.card-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.update-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* ========== 表单视图 ========== */
.brand-form-wrapper {
  max-width: var(--card-width);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-header h2 {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--foreground);
  margin: 0;
}

.brand-form {
  width: 100%;
}

.dynamic-input-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dynamic-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.dynamic-input-row .el-input {
  flex: 1;
  min-width: 0;
}

.remove-btn {
  flex-shrink: 0;
  width: var(--input-height);
  height: var(--input-height);
  padding: 0 !important;
  background: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  border-radius: var(--input-radius) !important;
  color: var(--text-muted) !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  color: var(--danger) !important;
  border-color: var(--danger) !important;
}

.add-input-btn {
  width: auto;
  align-self: flex-start;
  height: 32px;
  padding: 0 16px;
  background: transparent !important;
  border: 1px solid var(--input-border) !important;
  border-radius: 6px !important;
  color: var(--danger) !important;
  font-size: var(--text-base) !important;
  font-weight: 500 !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all var(--transition-fast) !important;
}

.add-input-btn:hover {
  border-color: var(--danger) !important;
  background: rgba(220, 38, 38, 0.08) !important;
}

/* ========== 表单底部按钮 ========== */
.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .brand-cards {
    grid-template-columns: 1fr;
  }
  .brand-card {
    padding: 20px;
  }
  .brand-form {
    padding: 20px;
  }
}
</style>
