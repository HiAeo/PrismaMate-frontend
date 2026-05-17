<template>
  <Layout>
    <div class="subscription-container">
      <div class="header">
        <h1>我的订阅</h1>
      </div>

      <!-- 当前套餐卡片 -->
      <el-card class="current-plan-card" v-loading="loading">
        <el-row :gutter="20">
          <el-col :span="16">
            <div class="plan-info">
              <el-tag :type="getPlanTagType(currentPlan?.plan_id)" size="large">
                {{ currentPlan?.name }}
              </el-tag>
              <div class="plan-stats">
                <div class="stat-item">
                  <span class="label">积分余额</span>
                  <span class="value">{{ currentPlan?.points_balance }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">本月用量</span>
                  <span class="value">
                    {{ currentPlan?.monthly_usage }} / {{ currentPlan?.monthly_quota }}
                  </span>
                </div>
                <div class="stat-item">
                  <span class="label">剩余次数</span>
                  <span class="value highlight">{{ currentPlan?.monthly_remaining }}</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="upgrade-section">
              <el-button type="primary" size="large" @click="showUpgrade = true">
                升级套餐
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 套餐对比表 -->
      <el-card class="plans-card">
        <template #header>
          <span>套餐对比</span>
        </template>
        <el-table :data="plans" border stripe>
          <el-table-column prop="name" label="套餐" width="140">
            <template #default="{ row }">
              <el-tag :type="getPlanTagType(row.id)">{{ row.name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="月付" width="120">
            <template #default="{ row }">
              <span v-if="row.monthly_price > 0">¥{{ row.monthly_price }}</span>
              <span v-else class="free">免费</span>
            </template>
          </el-table-column>
          <el-table-column label="年付" width="120">
            <template #default="{ row }">
              <span v-if="row.yearly_price > 0">¥{{ row.yearly_price }}</span>
              <span v-else class="free">免费</span>
            </template>
          </el-table-column>
          <el-table-column label="每月检测次数" width="120">
            <template #default="{ row }">
              {{ row.monthly_quota }}
            </template>
          </el-table-column>
          <el-table-column label="每日积分" width="100">
            <template #default="{ row }">
              {{ row.monthly_points }}
            </template>
          </el-table-column>
          <el-table-column label="关键词上限" width="100">
            <template #default="{ row }">
              {{ row.max_keywords === 999 ? '无限' : row.max_keywords }}
            </template>
          </el-table-column>
          <el-table-column label="平台数" width="80">
            <template #default="{ row }">
              {{ row.max_platforms }}
            </template>
          </el-table-column>
          <el-table-column label="竞品数" width="80">
            <template #default="{ row }">
              {{ row.max_competitors === 999 ? '无限' : row.max_competitors }}
            </template>
          </el-table-column>
          <el-table-column label="PDF下载" width="100">
            <template #default="{ row }">
              <el-icon v-if="row.has_pdf_download" color="var(--success)"><CircleCheck /></el-icon>
              <el-icon v-else color="var(--muted)"><Close /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="API访问" width="100">
            <template #default="{ row }">
              <el-icon v-if="row.has_api_access" color="var(--success)"><CircleCheck /></el-icon>
              <el-icon v-else color="var(--muted)"><Close /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="数据保留" width="100">
            <template #default="{ row }">
              {{ row.data_retention_days }}天
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="!row.is_current"
                type="primary"
                size="small"
                @click="handleUpgrade(row)"
              >
                升级
              </el-button>
              <el-tag v-else type="info" size="small">当前</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 升级确认弹窗 -->
      <el-dialog v-model="showUpgrade" title="升级套餐" width="400px">
        <div v-if="selectedPlan" class="upgrade-confirm">
          <p>确定要升级到 <strong>{{ selectedPlan.name }}</strong> 吗？</p>
          <p>月付价格：<strong>¥{{ selectedPlan.monthly_price }}</strong></p>
          <el-alert type="info" :closable="false">
            实际支付将通过支付网关完成，当前为演示模式将直接生效。
          </el-alert>
        </div>
        <template #footer>
          <el-button @click="showUpgrade = false">取消</el-button>
          <el-button type="primary" :loading="upgrading" @click="confirmUpgrade">
            确认升级
          </el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck, Close } from '@element-plus/icons-vue'
import { getMyPlan, getPlans, upgradePlan } from '@/api/subscription'
import Layout from '@/components/Layout.vue'

const loading = ref(false)
const upgrading = ref(false)
const currentPlan = ref<any>(null)
const plans = ref<any[]>([])
const showUpgrade = ref(false)
const selectedPlan = ref<any>(null)

const getPlanTagType = (planId: string) => {
  const map: Record<string, any> = {
    plan_mini: 'info',
    plan_max: 'warning',
    plan_plus: 'danger'
  }
  return map[planId] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const [planRes, plansRes] = await Promise.all([
      getMyPlan(),
      getPlans()
    ])
    currentPlan.value = planRes.plan
    plans.value = plansRes.plans
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleUpgrade = (plan: any) => {
  selectedPlan.value = plan
  showUpgrade.value = true
}

const confirmUpgrade = async () => {
  if (!selectedPlan.value) return

  upgrading.value = true
  try {
    const res: any = await upgradePlan(selectedPlan.value.plan_id)
    if (res.status === 'ok') {
      ElMessage.success(res.message)
      showUpgrade.value = false
      loadData()
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '升级失败')
  } finally {
    upgrading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.subscription-container {
  max-width: 100%;
}

.header h1 {
  margin: 0 0 24px 0;
  font-size: 24px;
  color: #FFFFFF;
}

.current-plan-card {
  margin-bottom: 20px;
}

.plan-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.plan-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item .label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

.stat-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #FFFFFF;
}

.stat-item .value.highlight {
  color: #4D6BFE;
}

.upgrade-section {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.free {
  color: #10B981;
}

.upgrade-confirm p {
  margin: 8px 0;
  color: rgba(255, 255, 255, 0.7);
}
</style>
