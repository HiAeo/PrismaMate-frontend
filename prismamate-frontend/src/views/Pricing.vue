<template>
  <PublicLayout>
    <div class="pricing-page">
      <!-- Header -->
      <div class="pricing-header">
        <h1>{{ t('pricing.title') }}</h1>
        <p class="subtitle">{{ t('pricing.subtitle') }}</p>
        <div class="billing-toggle">
          <button
            class="toggle-btn"
            :class="{ active: !isYearly }"
            @click="isYearly = false"
          >
            {{ t('pricing.monthly') }}
          </button>
          <button
            class="toggle-btn"
            :class="{ active: isYearly }"
            @click="isYearly = true"
          >
            {{ t('pricing.yearly') }}
            <span class="save-tag" v-if="planPrices.plan_max?.yearly && planPrices.plan_max?.monthly">
              省 {{ Math.round((1 - planPrices.plan_max.yearly / (planPrices.plan_max.monthly * 12)) * 100) }}%
            </span>
          </button>
        </div>
      </div>

    <!-- Cards -->
    <div class="pricing-cards" v-loading="loading">
      <!-- 单棱MINI版 -->
      <el-card class="pricing-card mini" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="badge badge-orange">特惠体验</div>
            <h3 style="margin-top: 4px;">{{ t('pricing.planFree.name') }}</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">{{ isYearly ? planPrices.plan_mini?.yearly : planPrices.plan_mini?.monthly }}</span>
              <span class="period">{{ isYearly ? t('pricing.perYear') : t('pricing.perMonth') }}</span>
            </div>
            <div class="yearly-price" v-if="isYearly && planPrices.plan_mini?.yearly">折合 ¥{{ Math.round(planPrices.plan_mini.yearly / 12) }}/月</div>
          </div>
        </template>
          <ul class="features">
            <li><el-icon><Check /></el-icon> {{ t('pricing.planFree.features.0') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planFree.features.1') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planFree.features.2') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planFree.features.3') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planFree.features.4') }}</li>
            <li><el-icon><Close /></el-icon> <span class="disabled">{{ t('pricing.planFree.disabled.0') }}</span></li>
            <li><el-icon><Close /></el-icon> <span class="disabled">{{ t('pricing.planFree.disabled.1') }}</span></li>
            <li><el-icon><Close /></el-icon> <span class="disabled">{{ t('pricing.planFree.disabled.2') }}</span></li>
          </ul>
          <div class="card-footer">
            <el-button type="primary" size="large" style="width: 100%" @click="handleFreeStart">
              {{ t('pricing.planFree.btn') }}
            </el-button>
          </div>
        </el-card>

        <!-- 复棱MAX版 -->
        <el-card class="pricing-card max featured" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="badge">{{ t('pricing.planMax.badge') }}</div>
              <h3 style="margin-top: 4px;">{{ t('pricing.planMax.name') }}</h3>
              <div class="price">
                <span class="currency">¥</span>
                <span class="amount">{{ isYearly ? planPrices.plan_max?.yearly : planPrices.plan_max?.monthly }}</span>
                <span class="period">{{ isYearly ? t('pricing.perYear') : t('pricing.perMonth') }}</span>
              </div>
              <div class="yearly-price" v-if="isYearly">折合 ¥{{ Math.round(planPrices.plan_max?.yearly / 12) }}/月</div>
            </div>
          </template>
          <ul class="features">
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.0') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.1') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.2') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.3') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.4') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.5') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planMax.features.6') }}</li>
            <li><el-icon><Close /></el-icon> <span class="disabled">{{ t('pricing.planMax.disabled.0') }}</span></li>
          </ul>
          <div class="card-footer">
            <el-button type="primary" size="large" style="width: 100%" @click="handleUpgrade('plan_max')">
              {{ t('pricing.planMax.btn') }}
            </el-button>
          </div>
        </el-card>

        <!-- 晶曜PLUS版 -->
        <el-card class="pricing-card plus" shadow="hover">
          <template #header>
          <div class="card-header">
            <div class="badge badge-red">深度使用</div>
            <h3 style="margin-top: 4px;">{{ t('pricing.planPlus.name') }}</h3>
            <div class="price">
                <span class="currency">¥</span>
                <span class="amount">{{ isYearly ? planPrices.plan_plus?.yearly : planPrices.plan_plus?.monthly }}</span>
                <span class="period">{{ isYearly ? t('pricing.perYear') : t('pricing.perMonth') }}</span>
              </div>
              <div class="yearly-price" v-if="isYearly">折合 ¥{{ Math.round(planPrices.plan_plus?.yearly / 12) }}/月</div>
            </div>
          </template>
          <ul class="features">
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.0') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.1') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.2') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.3') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.4') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.5') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.6') }}</li>
            <li><el-icon><Check /></el-icon> {{ t('pricing.planPlus.features.7') }}</li>
          </ul>
          <div class="card-footer">
            <el-button type="primary" size="large" style="width: 100%" @click="handleUpgrade('plan_plus')">
              {{ t('pricing.planPlus.btn') }}
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- FAQ -->
      <div class="faq-section">
        <h2>{{ t('pricing.faq.title') }}</h2>
        <el-collapse>
          <el-collapse-item :title="t('pricing.faq.q1')" name="1">
            {{ t('pricing.faq.a1') }}
          </el-collapse-item>
          <el-collapse-item :title="t('pricing.faq.q2')" name="2">
            {{ t('pricing.faq.a2') }}
          </el-collapse-item>
          <el-collapse-item :title="t('pricing.faq.q3')" name="3">
            {{ t('pricing.faq.a3') }}
          </el-collapse-item>
          <el-collapse-item :title="t('pricing.faq.q4')" name="4">
            {{ t('pricing.faq.a4') }}
          </el-collapse-item>
          <el-collapse-item :title="t('pricing.faq.q5')" name="5">
            {{ t('pricing.faq.a5') }}
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
import { Check, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PublicLayout from '@/components/PublicLayout.vue'
import { getPlans } from '@/api/subscription'

const router = useRouter()
const userStore = useUserStore()
const isYearly = ref(false)
const plans = ref<any[]>([])
const loading = ref(false)

const planPrices = computed(() => {
  const map: Record<string, { monthly: number; yearly: number }> = {
    plan_free: { monthly: 0, yearly: 0 },
    plan_mini: { monthly: 0, yearly: 0 },
    plan_max: { monthly: 299, yearly: 2999 },
    plan_plus: { monthly: 999, yearly: 9999 }
  }
  for (const p of plans.value) {
    map[p.id] = {
      monthly: p.monthly_price ?? map[p.id]?.monthly ?? 0,
      yearly: p.yearly_price ?? map[p.id]?.yearly ?? 0
    }
  }
  return map
})

const loadPlans = async () => {
  loading.value = true
  try {
    const res: any = await getPlans()
    const data = res.data
    console.log('[Pricing] API /subscription/plans response:', data)
    if (data.status === 'ok') {
      plans.value = data.plans || []
      const maxPlan = plans.value.find((p: any) => p.id === 'plan_max')
      const plusPlan = plans.value.find((p: any) => p.id === 'plan_plus')
      console.log('[Pricing] Loaded MAX monthly:', maxPlan?.monthly_price, 'yearly:', maxPlan?.yearly_price)
      console.log('[Pricing] Loaded PLUS monthly:', plusPlan?.monthly_price, 'yearly:', plusPlan?.yearly_price)
    } else {
      console.warn('[Pricing] API status not ok:', data)
    }
  } catch (err) {
    console.error('[Pricing] Failed to load plans:', err)
    ElMessage.error('价格加载失败，显示默认价格')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadPlans() })

// 页面重新可见时自动刷新价格（防止后台修改后前台tab未刷新）
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) loadPlans()
})

function handleFreeStart() {
  if (userStore.isLoggedIn) {
    router.push('/health-check')
  } else {
    userStore.authDialogTab = 'register'
    userStore.showAuthDialog = true
  }
}

function handleUpgrade(planId: string) {
  if (userStore.isLoggedIn) {
    router.push('/profile')
  } else {
    ElMessage.info('请先登录后再升级套餐')
    userStore.authDialogTab = 'login'
    userStore.showAuthDialog = true
  }
}
</script>

<style scoped>
.pricing-page {
  background: var(--background);
  min-height: 100vh;
}

/* === Header === */
.pricing-header {
  text-align: center;
  padding: 60px 20px 40px;
  background: var(--background);
}

.pricing-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 12px;
}

.pricing-header .subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 24px;
}

.billing-toggle {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  padding: 4px;
  gap: 4px;
}

.toggle-btn {
  position: relative;
  padding: 8px 24px;
  border-radius: 100px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.toggle-btn:hover {
  color: rgba(255, 255, 255, 0.8);
}

.toggle-btn.active {
  background: #FFFFFF;
  color: #000000;
  font-weight: 600;
}

.save-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 8px;
  background: #EF4444;
  color: #FFFFFF;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  vertical-align: middle;
}

/* === Cards Grid - 等高对齐 === */
.pricing-cards {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 24px;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.pricing-card {
  flex: 1;
  max-width: 340px;
  min-width: 280px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  background: rgba(255, 255, 255, 0.03) !important;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  flex-direction: column;
}

::v-deep(.pricing-card .el-card__header) {
  background: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  padding: 20px 24px;
}

.pricing-card:hover {
  transform: translateY(-4px);
  border-color: #3B82F6 !important;
  background: rgba(255, 255, 255, 0.05) !important;
  box-shadow: 0 0 24px rgba(59, 130, 246, 0.25), 0 12px 40px rgba(0, 0, 0, 0.4);
}

/* 单棱MINI版 — 橙色 */
.pricing-card.mini:hover {
  border-color: #F59E0B !important;
  box-shadow: 0 0 24px rgba(245, 158, 11, 0.25), 0 12px 40px rgba(0, 0, 0, 0.4);
}

/* 晶曜PLUS版 — 红色 */
.pricing-card.plus:hover {
  border-color: #EF4444 !important;
  box-shadow: 0 0 24px rgba(239, 68, 68, 0.25), 0 12px 40px rgba(0, 0, 0, 0.4);
}

.pricing-card.featured {
  border: 2px solid rgba(255, 255, 255, 0.25) !important;
  transform: scale(1.02);
  background: rgba(255, 255, 255, 0.04) !important;
}

.pricing-card.featured:hover {
  transform: scale(1.02) translateY(-4px);
  border-color: #3B82F6 !important;
  box-shadow: 0 0 24px rgba(59, 130, 246, 0.3), 0 12px 40px rgba(0, 0, 0, 0.4);
}

.card-header {
  text-align: center;
  position: relative;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #FFFFFF;
}

.badge {
  display: inline-block;
  background: #3B82F6;
  color: #FFFFFF;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}
.badge-orange { background: #F59E0B; }
.badge-red { background: #EF4444; }

.price {
  margin-bottom: 8px;
}

.price .currency {
  font-size: 20px;
  vertical-align: top;
  color: #FFFFFF;
}

.price .amount {
  font-size: 48px;
  font-weight: 700;
  color: #FFFFFF;
}

.price .period {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.yearly-price {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 12px;
  background: #F59E0B;
  color: #FFFFFF;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
}

/* === Features === */
.features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
  flex: 1;
}

.features li {
  padding: 10px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.85);
  border-bottom: 0.5px solid rgba(255, 255, 255, 0.08);
  font-size: 14px;
}

.features li:last-child {
  border-bottom: none;
}

.features li :deep(.el-icon) {
  font-size: 16px;
  flex-shrink: 0;
  color: #FFFFFF;
}

.features li .disabled {
  color: rgba(255, 255, 255, 0.35);
  text-decoration: line-through;
}

::v-deep(.pricing-card) {
  display: flex;
  flex-direction: column;
}

::v-deep(.pricing-card .el-card__body) {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 24px;
  background: transparent !important;
}

/* === Card Footer - 底部对齐 === */
.card-footer {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: auto;
}

/* === 按钮 - 无底色白字 === */
.pricing-card :deep(.el-button) {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  font-weight: 600;
  border-radius: 10px;
  transition: all 0.2s;
}

.pricing-card :deep(.el-button:hover) {
  background: #3B82F6 !important;
  transform: translateY(-1px);
  border-color: #3B82F6 !important;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35);
}

/* 单棱MINI版按钮 — 橙色 */
.pricing-card.mini :deep(.el-button:hover) {
  background: #F59E0B !important;
  border-color: #F59E0B !important;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
}

/* 晶曜PLUS版按钮 — 红色 */
.pricing-card.plus :deep(.el-button:hover) {
  background: #EF4444 !important;
  border-color: #EF4444 !important;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.35);
}

/* === FAQ Section === */
.faq-section {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px 80px;
}

.faq-section h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
  color: #FFFFFF;
}

::v-deep(.faq-section .el-collapse) {
  border: none;
  background: transparent !important;
}

::v-deep(.faq-section .el-collapse-item__header) {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.85) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  font-size: 15px;
  font-weight: 500;
  padding: 16px 0;
}

::v-deep(.faq-section .el-collapse-item__content) {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.6) !important;
  font-size: 14px;
  line-height: 1.7;
  padding: 12px 0 20px;
}

::v-deep(.faq-section .el-collapse-item__wrap) {
  background: transparent !important;
  border-bottom: none !important;
}

::v-deep(.faq-section .el-collapse-item) {
  background: transparent !important;
}

/* === Responsive === */
@media (max-width: 1024px) {
  .pricing-cards {
    flex-wrap: wrap;
  }

  .pricing-card {
    flex: 1 1 calc(50% - 12px);
    max-width: 400px;
  }
}

@media (max-width: 768px) {
  .pricing-header h1 {
    font-size: 26px;
  }

  .pricing-cards {
    flex-direction: column;
    align-items: center;
  }

  .pricing-card {
    width: 100%;
    max-width: 400px;
    flex: none;
  }

  .pricing-card.featured {
    transform: none;
    order: -1;
  }

  .pricing-card.featured:hover {
    transform: translateY(-4px);
  }
}
</style>
