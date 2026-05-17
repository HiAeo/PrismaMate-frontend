<template>
  <Layout>
    <div class="admin-points-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>PrismaMate 棱镜积分流水</h1>
        <p class="subtitle">查看所有用户的积分变动记录</p>
      </div>

      <div class="table-card">
        <el-table :data="transactions" v-loading="loading" stripe>
          <el-table-column prop="transaction_id" label="流水号" min-width="160" />
          <el-table-column prop="user_email" label="用户邮箱" min-width="160" />
          <el-table-column prop="username" label="用户名" min-width="100" />
          <el-table-column label="变动" min-width="100">
            <template #default="{ row }">
              <span :class="row.amount > 0 ? 'positive' : 'negative'">
                {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="余额" min-width="100">
            <template #default="{ row }">
              <span class="balance">{{ row.balance_after }}</span>
            </template>
          </el-table-column>
          <el-table-column label="类型" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.type)" size="small">{{ getTypeText(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="180" />
          <el-table-column label="时间" min-width="140">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadTransactions"
            @current-change="loadTransactions"
          />
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPointsTransactions } from '@/api/admin'
import Layout from '@/components/Layout.vue'

const loading = ref(false)
const transactions = ref<any[]>([])
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const getTypeTag = (type: string) => {
  const map: Record<string, any> = { detection: 'warning', purchase: 'success', gift: 'primary', admin_adjust: 'danger', subscription_grant: 'info' }
  return map[type] || 'info'
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = { detection: '检测消耗', purchase: '充值', gift: '赠送', admin_adjust: '管理员调整', subscription_grant: '订阅赠送' }
  return map[type] || type
}

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString('zh-CN')

const loadTransactions = async () => {
  loading.value = true
  try {
    const res: any = await getPointsTransactions({ page: pagination.page, page_size: pagination.page_size })
    const data = res.data
    if (data.status === 'ok') { transactions.value = data.transactions; pagination.total = data.total }
  } catch (error) { ElMessage.error('获取积分流水失败') }
  finally { loading.value = false }
}

onMounted(() => { loadTransactions() })
</script>

<style scoped>
.admin-points-container { max-width: 100%; }

/* 页面头部 */
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 22px; font-weight: 600; color: #FFFFFF; margin: 0 0 8px 0; line-height: 1.3; }
.subtitle { font-size: 14px; color: #9CA3AF; margin: 0; }

/* 表格卡片 */
.table-card {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 20px;
  transition: border-color 0.25s ease;
}
.table-card:hover { border-color: #3B82F6; }

.positive { color: #10B981; font-weight: 500; }
.negative { color: #EF4444; font-weight: 500; }
.balance { color: #3B82F6; font-weight: 500; }

.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }

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
</style>
