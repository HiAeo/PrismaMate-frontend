<template>
  <Layout>
    <div class="admin-plans-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>套餐配置</h1>
        <p class="subtitle">调整各套餐的月付/年付价格</p>
      </div>

      <!-- 套餐价格卡片 -->
      <div class="plans-grid">
        <div v-for="plan in plans" :key="plan.id" class="plan-card">
          <div class="plan-header">
            <span class="plan-name">{{ plan.name }}</span>
          </div>

          <div class="plan-fields">
            <div class="field-row">
              <span class="field-label">月付价格</span>
              <el-input-number
                v-model="plan.monthly_price"
                :min="0"
                :step="10"
                controls-position="right"
                class="price-input"
              />
            </div>
            <div class="field-row">
              <span class="field-label">年付价格</span>
              <el-input-number
                v-model="plan.yearly_price"
                :min="0"
                :step="100"
                controls-position="right"
                class="price-input"
              />
            </div>
          </div>

          <el-button
            type="primary"
            :loading="savingId === plan.id"
            class="save-btn"
            @click="savePlan(plan)"
          >
            保存
          </el-button>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPlans, updatePlan } from '@/api/admin'
import Layout from '@/components/Layout.vue'

const plans = ref<any[]>([])
const savingId = ref<string | null>(null)

const loadPlans = async () => {
  try {
    const res: any = await getPlans()
    const data = res.data
    if (data.status === 'ok') { plans.value = data.plans }
  } catch (error) { ElMessage.error('获取套餐列表失败') }
}

const savePlan = async (plan: any) => {
  savingId.value = plan.id
  try {
    const res: any = await updatePlan(plan.id, {
      monthly_price: plan.monthly_price,
      yearly_price: plan.yearly_price
    })
    const data = res.data
    if (data.status === 'ok') { ElMessage.success(data.message) }
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '保存失败') }
  finally { savingId.value = null }
}

onMounted(() => { loadPlans() })
</script>

<style scoped>
.admin-plans-container { max-width: 100%; }

/* 页面头部 */
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 22px; font-weight: 600; color: #FFFFFF; margin: 0 0 8px 0; line-height: 1.3; }
.subtitle { font-size: 14px; color: #9CA3AF; margin: 0; }

/* 三列网格 */
.plans-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.plan-card {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 24px;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}
.plan-card:hover {
  border-color: #3B82F6;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
}

.plan-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.plan-name { font-size: 16px; font-weight: 600; color: #FFFFFF; }

.plan-fields {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 20px;
}

.field-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-label {
  font-size: 14px;
  color: #D1D5DB;
  width: 70px;
  flex-shrink: 0;
}

.price-input { flex: 1; }

.save-btn {
  width: 100%;
  height: 42px;
}

/* 通用按钮 hover 交互 */
:deep(.el-button) {
  border-color: #2D2D2D;
  background: #1A1A1A;
  color: #D1D5DB;
  transition: border-color 0.2s ease, color 0.2s ease;
}
:deep(.el-button:hover),
:deep(.el-button:focus) {
  border-color: #3B82F6;
  color: #FFFFFF;
  background: #1A1A1A;
}
:deep(.el-button--primary) {
  border-color: #3B82F6;
  background: #3B82F6;
  color: #FFFFFF;
}
:deep(.el-button--primary:hover),
:deep(.el-button--primary:focus) {
  border-color: #2563EB;
  background: #2563EB;
  color: #FFFFFF;
}

/* 响应式 */
@media (max-width: 900px) {
  .plans-grid { grid-template-columns: 1fr; }
}
</style>
