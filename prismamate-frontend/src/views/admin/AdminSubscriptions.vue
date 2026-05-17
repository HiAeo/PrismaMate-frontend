<template>
  <Layout>
    <div class="admin-subs-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>PrismaMate 棱镜订阅记录</h1>
        <p class="subtitle">查看所有用户的订阅和充值订单</p>
      </div>

      <div class="table-card">
        <el-table :data="orders" v-loading="loading" stripe>
          <el-table-column prop="order_id" label="订单号" min-width="180" />
          <el-table-column prop="user_email" label="用户邮箱" min-width="160" />
          <el-table-column prop="username" label="用户名" min-width="100" />
          <el-table-column label="订单类型" min-width="100">
            <template #default="{ row }">
              <el-tag :type="row.order_type === 'subscription' ? 'primary' : 'success'" size="small">
                {{ row.order_type === 'subscription' ? '订阅' : '积分' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="金额" min-width="100">
            <template #default="{ row }">
              <span class="amount">¥{{ row.amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" min-width="140">
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
            @size-change="loadOrders"
            @current-change="loadOrders"
          />
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSubscriptions } from '@/api/admin'
import Layout from '@/components/Layout.vue'

const loading = ref(false)
const orders = ref<any[]>([])
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const getStatusType = (status: string) => {
  const map: Record<string, any> = { pending: 'warning', paid: 'success', refunded: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: '待支付', paid: '已支付', refunded: '已退款' }
  return map[status] || status
}

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString('zh-CN')

const loadOrders = async () => {
  loading.value = true
  try {
    const res: any = await getSubscriptions({ page: pagination.page, page_size: pagination.page_size })
    const data = res.data
    if (data.status === 'ok') { orders.value = data.orders; pagination.total = data.total }
  } catch (error) { ElMessage.error('获取订阅记录失败') }
  finally { loading.value = false }
}

onMounted(() => { loadOrders() })
</script>

<style scoped>
.admin-subs-container { max-width: 100%; }

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

.amount { color: #3B82F6; font-weight: 500; }

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
