<template>
  <Layout>
    <div class="points-container">
      <div class="header">
        <h1>积分中心</h1>
      </div>

      <!-- 积分余额卡片 -->
      <el-card class="balance-card" v-loading="loading">
        <el-row :gutter="20" align="middle">
          <el-col :span="12">
            <div class="balance-info">
              <span class="balance-label">当前积分余额</span>
              <span class="balance-value">{{ balance }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="recharge-section">
              <el-button type="primary" size="large" @click="showRecharge = true">
                积分充值
              </el-button>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="recharge-tips">
          <h4>充值说明</h4>
          <ul>
            <li>100 积分 = ¥10</li>
            <li>充值必须是 100 的倍数</li>
            <li>积分永不过期，可累积使用</li>
          </ul>
        </div>
      </el-card>

      <!-- 充值弹窗 -->
      <el-dialog v-model="showRecharge" title="积分充值" width="400px">
        <el-form :model="rechargeForm" label-width="100px">
          <el-form-item label="充值数量">
            <el-input-number
              v-model="rechargeForm.amount"
              :min="100"
              :step="100"
              :precision="0"
            />
          </el-form-item>
          <el-form-item label="所需金额">
            <span class="price">¥{{ (rechargeForm.amount / 100) * 10 }}</span>
          </el-form-item>
          <el-alert type="info" :closable="false">
            当前为演示模式，将直接增加积分。
          </el-alert>
        </el-form>
        <template #footer>
          <el-button @click="showRecharge = false">取消</el-button>
          <el-button type="primary" :loading="recharging" @click="confirmRecharge">
            确认充值
          </el-button>
        </template>
      </el-dialog>

      <!-- 积分流水 -->
      <el-card class="history-card">
        <template #header>
          <span>积分流水</span>
        </template>

        <el-table :data="history" v-loading="historyLoading" stripe>
          <el-table-column label="变动" width="100">
            <template #default="{ row }">
              <span :class="row.amount > 0 ? 'positive' : 'negative'">
                {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="余额" width="100">
            <template #default="{ row }">
              <span class="balance">{{ row.balance_after }}</span>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.type)" size="small">
                {{ getTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" />
          <el-table-column label="时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyPlan, getPointsHistory, purchasePoints } from '@/api/subscription'
import Layout from '@/components/Layout.vue'

const loading = ref(false)
const historyLoading = ref(false)
const recharging = ref(false)
const balance = ref(0)
const history = ref<any[]>([])
const showRecharge = ref(false)
const rechargeForm = reactive({ amount: 100 })

const getTypeTag = (type: string) => {
  const map: Record<string, any> = {
    detection: 'warning',
    purchase: 'success',
    gift: 'primary',
    admin_adjust: 'danger',
    subscription_grant: 'info'
  }
  return map[type] || 'info'
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    detection: '检测消耗',
    purchase: '充值',
    gift: '赠送',
    admin_adjust: '管理员调整',
    subscription_grant: '订阅赠送'
  }
  return map[type] || type
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const planRes: any = await getMyPlan()
    balance.value = planRes.plan?.points_balance || 0
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const res: any = await getPointsHistory(50)
    history.value = res.history || []
  } catch (error) {
    ElMessage.error('获取流水失败')
  } finally {
    historyLoading.value = false
  }
}

const confirmRecharge = async () => {
  if (rechargeForm.amount < 100) {
    ElMessage.warning('充值数量至少为 100')
    return
  }

  recharging.value = true
  try {
    const res: any = await purchasePoints(rechargeForm.amount)
    if (res.status === 'ok') {
      ElMessage.success(`充值成功！+${rechargeForm.amount} 积分`)
      balance.value = res.new_balance
      showRecharge.value = false
      loadHistory()
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '充值失败')
  } finally {
    recharging.value = false
  }
}

onMounted(() => {
  loadData()
  loadHistory()
})
</script>

<style scoped>
.points-container {
  max-width: 100%;
}

.header h1 {
  margin: 0 0 24px 0;
  font-size: 24px;
  color: #FFFFFF;
}

.balance-card {
  margin-bottom: 20px;
}

.balance-info {
  display: flex;
  flex-direction: column;
}

.balance-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.45);
}

.balance-value {
  font-size: 36px;
  font-weight: bold;
  color: #FFFFFF;
}

.recharge-section {
  display: flex;
  justify-content: flex-end;
}

.recharge-tips {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.recharge-tips h4 {
  margin: 0 0 8px 0;
  color: #FFFFFF;
  font-weight: 600;
}

.recharge-tips ul {
  margin: 0;
  padding-left: 20px;
}

.recharge-tips li {
  margin: 4px 0;
  color: rgba(255, 255, 255, 0.55);
}

.price {
  font-size: 20px;
  font-weight: bold;
  color: #FFFFFF;
}

.positive {
  color: #10B981;
  font-weight: 500;
}

.negative {
  color: #EF4444;
  font-weight: 500;
}

.balance {
  color: #FFFFFF;
  font-weight: 500;
}
</style>
