<template>
  <Layout>
    <div class="page-container profile-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>PrismaMate 棱镜个人中心</h1>
        <p class="subtitle">PrismaMate 的使命，就是成为这个行业的"查博士"——一把公认的、独立的尺子。我们提供的是客观、不可篡改的第三方检测报告，让品牌方能真正看清自己在 AI 大模型中的真实表现，让 GEO 服务商的交付成果可以被量化、被验证。</p>
      </div>

      <el-tabs v-model="activeTab" class="profile-tabs">
        <!-- 我的报告 -->
        <el-tab-pane :label="t('profile.tabs.reports')" name="reports">
          <div class="tab-content">
            <div class="tab-header">
              <el-input
                v-model="reportSearch"
                :placeholder="t('profile.searchPlaceholder')"
                style="width: 300px"
                clearable
              />
            </div>
            <el-table :data="filteredReports" stripe style="width: 100%" v-loading="reportsLoading">
              <el-table-column prop="report_id" :label="t('profile.reportId')" min-width="120" />
              <el-table-column prop="keywords" :label="t('profile.keywords')" min-width="150">
                <template #default="{ row }">
                  {{ row.keywords?.join(', ') || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="platforms" :label="t('profile.platforms')" min-width="120">
                <template #default="{ row }">
                  {{ row.platforms?.join(', ') }}
                </template>
              </el-table-column>
              <el-table-column prop="total_mentions" :label="t('profile.mentions')" min-width="100" />
              <el-table-column prop="created_at" :label="t('profile.createdAt')" min-width="140">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column :label="t('profile.actions')" min-width="180" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="viewReport(row)">
                    {{ t('profile.view') }}
                  </el-button>
                  <el-button size="small" type="primary" @click="compareReport(row)">
                    {{ t('profile.compare') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 品牌管理 -->
        <el-tab-pane :label="t('profile.tabs.brands')" name="brands">
          <div class="tab-content">
            <div class="tab-header">
              <el-button type="primary" @click="$router.push('/brand-hub')">
                {{ t('profile.manageBrands') }}
              </el-button>
            </div>
            <el-table :data="brandProfiles" stripe style="width: 100%" v-loading="brandsLoading">
              <el-table-column prop="company_name" :label="t('brandHub.companyName')" width="150" />
              <el-table-column :label="t('brandHub.brandNames')">
                <template #default="{ row }">
                  <el-tag v-for="name in row.brand_names" :key="name" size="small" class="mr-1">
                    {{ name }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="website" :label="t('brandHub.website')" width="200">
                <template #default="{ row }">
                  <a :href="row.website" target="_blank" class="link">{{ row.website }}</a>
                </template>
              </el-table-column>
              <el-table-column :label="t('brandHub.keywords')">
                <template #default="{ row }">
                  <el-tag v-for="kw in row.keywords.slice(0, 3)" :key="kw" size="small" type="info" class="mr-1">
                    {{ kw }}
                  </el-tag>
                  <span v-if="row.keywords.length > 3" class="more-count">
                    +{{ row.keywords.length - 3 }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" :label="t('brandHub.updatedAt')" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 我的套餐 -->
        <el-tab-pane :label="t('profile.tabs.subscription')" name="subscription">
          <div class="tab-content">
            <!-- 当前套餐 -->
            <el-card class="current-plan-card" shadow="hover">
              <template #header>
                <span>{{ t('profile.currentPlan') }}</span>
              </template>
              <div class="plan-info" v-if="currentPlan">
                <div class="plan-name">{{ currentPlan.name }}</div>
                <div class="plan-detail">
                  <span>{{ t('profile.monthlyQuota') }}: {{ currentPlan.monthly_quota || '无限制' }}</span>
                  <span>{{ t('profile.dailyPoints') }}: {{ currentPlan.daily_points || 0 }}</span>
                </div>
                <el-button type="primary" @click="$router.push('/pricing')">
                  {{ t('profile.upgradePlan') }}
                </el-button>
              </div>
              <div v-else class="no-plan">
                <p>{{ t('profile.noPlan') }}</p>
                <el-button type="primary" @click="$router.push('/pricing')">
                  {{ t('profile.choosePlan') }}
                </el-button>
              </div>
            </el-card>

            <!-- 用量统计 -->
            <el-card class="usage-card" shadow="hover" style="margin-top: 16px">
              <template #header>
                <span>{{ t('profile.usageStats') }}</span>
              </template>
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="stat-box">
                    <div class="stat-value">{{ usage.monthly_used || 0 }}</div>
                    <div class="stat-label">{{ t('profile.monthlyUsed') }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-box">
                    <div class="stat-value">{{ usage.monthly_remaining || 0 }}</div>
                    <div class="stat-label">{{ t('profile.monthlyRemaining') }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-box">
                    <div class="stat-value">{{ usage.total_reports || 0 }}</div>
                    <div class="stat-label">{{ t('profile.totalReports') }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-box">
                    <div class="stat-value">{{ usage.total_tasks || 0 }}</div>
                    <div class="stat-label">{{ t('profile.totalTasks') }}</div>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 积分中心 -->
        <el-tab-pane :label="t('profile.tabs.points')" name="points">
          <div class="tab-content">
            <el-card class="points-card" shadow="hover">
              <template #header>
                <span>{{ t('profile.pointsBalance') }}</span>
              </template>
              <div class="points-info">
                <div class="points-value">{{ pointsBalance }}</div>
                <el-button type="primary" @click="showPointsDialog = true">
                  {{ t('profile.recharge') }}
                </el-button>
              </div>
            </el-card>

            <!-- 积分流水 -->
            <el-card class="points-history-card" shadow="hover" style="margin-top: 16px">
              <template #header>
                <span>{{ t('profile.pointsHistory') }}</span>
              </template>
              <el-table :data="pointsHistory" stripe style="width: 100%" v-loading="pointsLoading">
                <el-table-column prop="amount" :label="t('profile.amount')" width="120">
                  <template #default="{ row }">
                    <span :class="row.amount > 0 ? 'positive' : 'negative'">
                      {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="balance" :label="t('profile.balance')" width="120" />
                <el-table-column prop="type" :label="t('profile.type')" width="120">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getPointsType(row.type)">
                      {{ getPointsTypeName(row.type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" :label="t('profile.description')" />
                <el-table-column prop="created_at" :label="t('profile.createdAt')" width="160">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 账户设置 -->
        <el-tab-pane :label="t('profile.tabs.settings')" name="settings">
          <div class="tab-content">
            <el-card shadow="hover">
              <template #header>
                <span>{{ t('profile.accountInfo') }}</span>
              </template>
              <el-form :model="accountForm" label-width="120px">
                <el-form-item :label="t('profile.username')">
                  <el-input v-model="accountForm.username" />
                </el-form-item>
                <el-form-item :label="t('profile.email')">
                  <el-input v-model="accountForm.email" disabled />
                </el-form-item>
                <el-form-item :label="t('profile.companyName')">
                  <el-input v-model="accountForm.company_name" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveAccountInfo">
                    {{ t('common.save') }}
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>

            <el-card shadow="hover" style="margin-top: 16px">
              <template #header>
                <span>{{ t('profile.changePassword') }}</span>
              </template>
              <el-form :model="passwordForm" label-width="120px">
                <el-form-item :label="t('profile.oldPassword')">
                  <el-input v-model="passwordForm.old_password" type="password" show-password />
                </el-form-item>
                <el-form-item :label="t('profile.newPassword')">
                  <el-input v-model="passwordForm.new_password" type="password" show-password />
                </el-form-item>
                <el-form-item :label="t('profile.confirmPassword')">
                  <el-input v-model="passwordForm.confirm_password" type="password" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="changePassword">
                    {{ t('profile.changePassword') }}
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 积分充值对话框 -->
    <el-dialog v-model="showPointsDialog" :title="t('profile.rechargePoints')" width="400px">
      <el-form :model="pointsRechargeForm" label-width="100px">
        <el-form-item :label="t('profile.rechargeAmount')">
          <el-input-number v-model="pointsRechargeForm.points" :min="100" :step="100" />
        </el-form-item>
        <el-form-item :label="t('profile.price')">
          <span>¥{{ (pointsRechargeForm.points / 10).toFixed(2) }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPointsDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="rechargePoints" :loading="recharging">
          {{ t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'
import { brandHubApi, BrandProfile } from '@/api/brandHub'
import api from '@/api/axios'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

// Tab 状态
const activeTab = ref('reports')

// 报告相关
const reports = ref<any[]>([])
const reportsLoading = ref(false)
const reportSearch = ref('')

const filteredReports = computed(() => {
  if (!reportSearch.value) return reports.value
  return reports.value.filter(r =>
    r.report_id?.includes(reportSearch.value) ||
    r.keywords?.some((k: string) => k.includes(reportSearch.value))
  )
})

// 品牌相关
const brandProfiles = ref<BrandProfile[]>([])
const brandsLoading = ref(false)

// 套餐相关
const currentPlan = ref<any>(null)
const usage = ref<any>({})

// 积分相关
const pointsBalance = ref(0)
const pointsHistory = ref<any[]>([])
const pointsLoading = ref(false)
const showPointsDialog = ref(false)
const recharging = ref(false)

const pointsRechargeForm = reactive({
  points: 100
})

// 账户设置
const accountForm = reactive({
  username: '',
  email: '',
  company_name: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 加载报告列表
async function loadReports() {
  reportsLoading.value = true
  try {
    const res = await api.get('/reports')
    reports.value = Array.isArray(res.data?.reports) ? res.data.reports : []
  } catch {
    reports.value = []
  } finally {
    reportsLoading.value = false
  }
}

// 加载品牌列表
async function loadBrands() {
  brandsLoading.value = true
  try {
    const res = await brandHubApi.list()
    brandProfiles.value = Array.isArray(res.data) ? res.data : []
  } catch {
    brandProfiles.value = []
  } finally {
    brandsLoading.value = false
  }
}

// 加载套餐信息
async function loadSubscription() {
  try {
    const res = await api.get('/subscription/my-plan')
    currentPlan.value = res.data?.plan ?? null
  } catch (error) {
    console.error('Failed to load subscription:', error)
  }
}

// 加载用量统计
async function loadUsage() {
  try {
    const res = await api.get('/user/usage')
    usage.value = res.data || {}
  } catch (error) {
    console.error('Failed to load usage:', error)
  }
}

// 加载积分
async function loadPoints() {
  pointsLoading.value = true
  try {
    const balanceRes = await api.get('/subscription/points')
    pointsBalance.value = balanceRes.data?.balance ?? 0
  } catch {
    pointsBalance.value = 0
  }

  try {
    const historyRes = await api.get('/subscription/points-history')
    pointsHistory.value = Array.isArray(historyRes.data?.history) ? historyRes.data.history : []
  } catch {
    pointsHistory.value = []
  } finally {
    pointsLoading.value = false
  }
}

// 加载账户信息
function loadAccountInfo() {
  accountForm.username = userStore.user?.username || ''
  accountForm.email = userStore.user?.email || ''
  accountForm.company_name = userStore.user?.company_name || ''
}

// 查看报告
function viewReport(row: any) {
  router.push(`/reports/${row.report_id}`)
}

// 对比报告
function compareReport(row: any) {
  router.push(`/reports/${row.report_id}/comparison`)
}

// 格式化日期
function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

// 积分类型
function getPointsType(type: string) {
  switch (type) {
    case 'detection': return 'warning'
    case 'recharge': return 'success'
    case 'bonus': return 'info'
    case 'deduction': return 'danger'
    default: return 'info'
  }
}

function getPointsTypeName(type: string) {
  switch (type) {
    case 'detection': return t('profile.pointsTypeDetection')
    case 'recharge': return t('profile.pointsTypeRecharge')
    case 'bonus': return t('profile.pointsTypeBonus')
    case 'deduction': return t('profile.pointsTypeDeduction')
    default: return type
  }
}

// 保存账户信息
async function saveAccountInfo() {
  try {
    await api.put('/user/profile', {
      username: accountForm.username,
      company_name: accountForm.company_name
    })
    ElMessage.success(t('common.success'))
    await userStore.fetchUserInfo()
  } catch (error) {
    ElMessage.error(t('common.error'))
  }
}

// 修改密码
async function changePassword() {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error(t('profile.passwordMismatch'))
    return
  }
  try {
    await api.post('/auth/change-password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success(t('profile.passwordChanged'))
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    ElMessage.error(t('common.error'))
  }
}

// 充值积分
async function rechargePoints() {
  recharging.value = true
  try {
    await api.post('/subscription/recharge', {
      points: pointsRechargeForm.points
    })
    ElMessage.success(t('profile.rechargeSuccess'))
    showPointsDialog.value = false
    loadPoints()
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    recharging.value = false
  }
}

// 初始化
onMounted(() => {
  loadReports()
  loadBrands()
  loadSubscription()
  loadUsage()
  loadPoints()
  loadAccountInfo()
})
</script>

<style scoped>
/* .profile-container 容器样式已移至 global.css .page-container */

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--foreground);
}

.page-header .subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
}

.profile-tabs {
  /* card 样式已移至 .profile-container，此处仅保留标签结构 */
}

.tab-content {
  padding: 16px 0;
}

.tab-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.tab-header .el-input {
  width: 320px;
  height: var(--input-height);
}

.tab-header .el-input :deep(.el-input__wrapper) {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--input-radius);
  box-shadow: none;
}

.tab-header .el-input :deep(.el-input__inner) {
  color: var(--input-text);
}

.tab-header .el-input :deep(.el-input__inner::placeholder) {
  color: var(--input-placeholder);
}

.link {
  color: var(--primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.mr-1 {
  margin-right: 4px;
}

.more-count {
  color: var(--muted);
  font-size: 12px;
}

/* 套餐卡片 */
.current-plan-card :deep(.el-card__header) {
  font-weight: 600;
}

.plan-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--foreground);
}

.plan-detail {
  display: flex;
  gap: 24px;
  color: var(--muted);
}

.no-plan {
  text-align: center;
  padding: 20px;
}

/* 用量统计 */
.usage-card :deep(.el-card__header) {
  font-weight: 600;
}

.stat-box {
  background: var(--hover-bg);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--foreground);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--muted);
}

/* 积分卡片 */
.points-card :deep(.el-card__header) {
  font-weight: 600;
}

.points-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.points-value {
  font-size: 36px;
  font-weight: 600;
  color: var(--primary);
}

.points-history-card :deep(.el-card__header) {
  font-weight: 600;
}

.positive {
  color: var(--success);
  font-weight: 600;
}

.negative {
  color: var(--danger);
  font-weight: 600;
}

/* ========== 表格空数据与加载状态 ========== */
:deep(.el-table__empty-block) {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-table__empty-text) {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.6;
  text-align: center;
}

:deep(.el-loading-mask) {
  background: rgba(15, 15, 15, 0.6);
}

:deep(.el-loading-spinner) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

:deep(.el-loading-spinner .circular) {
  width: 32px;
  height: 32px;
}
</style>
