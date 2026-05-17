<template>
  <Layout>
    <div class="admin-users-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>用户管理</h1>
        <p class="subtitle">共 {{ pagination.total }} 位注册用户</p>
      </div>

      <!-- 筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.search"
          placeholder="搜索邮箱/用户名"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        <el-select v-model="filters.plan_id" placeholder="全部套餐" clearable @change="handleSearch">
          <el-option label="单棱MINI版" value="plan_mini" />
          <el-option label="复棱MAX版" value="plan_max" />
          <el-option label="晶曜PLUS版" value="plan_plus" />
        </el-select>
        <el-select v-model="filters.is_active" placeholder="全部状态" clearable @change="handleSearch">
          <el-option label="正常" :value="true" />
          <el-option label="已封禁" :value="false" />
        </el-select>
      </div>

      <!-- 用户列表 -->
      <div class="table-card">
        <el-table :data="users" v-loading="loading" stripe>
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="username" label="用户名" min-width="100" />
          <el-table-column label="套餐" min-width="110">
            <template #default="{ row }">
              <span class="plan-tag" :class="row.plan_id">{{ row.plan_name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="积分" min-width="80">
            <template #default="{ row }">
              <span class="points">{{ row.points_balance }}</span>
            </template>
          </el-table-column>
          <el-table-column label="本月" min-width="90">
            <template #default="{ row }">
              {{ row.monthly_usage }}/{{ row.monthly_quota }}
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="90">
            <template #default="{ row }">
              <span class="status-badge" :class="row.is_active ? 'active' : 'banned'">
                {{ row.is_active ? '正常' : '封禁' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="100" fixed="right">
            <template #default="{ row }">
              <el-dropdown trigger="click" size="small">
                <el-button size="small">操作</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="viewUser(row)">查看详情</el-dropdown-item>
                    <el-dropdown-item @click="adjustPoints(row)">调整积分</el-dropdown-item>
                    <el-dropdown-item @click="adjustPlan(row)">调整套餐</el-dropdown-item>
                    <el-dropdown-item divided @click="toggleBan(row)">
                      <span :class="row.is_active ? 'text-danger' : ''">{{ row.is_active ? '封禁' : '解封' }}</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadUsers"
            @current-change="loadUsers"
          />
        </div>
      </div>

      <!-- 用户详情弹窗 -->
      <el-dialog v-model="detailVisible" title="用户详情" width="600px">
        <el-descriptions v-if="currentUser" :column="2" border>
          <el-descriptions-item label="用户ID">{{ currentUser.user_id }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
          <el-descriptions-item label="当前套餐">
            <span class="plan-tag" :class="currentUser.plan_id">{{ currentUser.plan_name }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="积分余额">{{ currentUser.points_balance }}</el-descriptions-item>
          <el-descriptions-item label="本月用量">{{ currentUser.monthly_usage }} / {{ currentUser.plan?.monthly_quota }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <span class="status-badge" :class="currentUser.is_active ? 'active' : 'banned'">
              {{ currentUser.is_active ? '正常' : '已封禁' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(currentUser.created_at) }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>

      <!-- 调整积分弹窗 -->
      <el-dialog v-model="pointsVisible" title="调整积分" width="400px">
        <el-form :model="pointsForm" label-width="80px">
          <el-form-item label="用户"><span>{{ currentUser?.email }}</span></el-form-item>
          <el-form-item label="当前积分"><span>{{ currentUser?.points_balance }}</span></el-form-item>
          <el-form-item label="调整数量" required>
            <el-input-number v-model="pointsForm.amount" :step="10" :min="-1000" />
          </el-form-item>
          <el-form-item label="原因" required>
            <el-input v-model="pointsForm.reason" type="textarea" rows="2" placeholder="请输入调整原因" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="pointsVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitPoints">确认</el-button>
        </template>
      </el-dialog>

      <!-- 调整套餐弹窗 -->
      <el-dialog v-model="planVisible" title="调整套餐" width="400px">
        <el-form :model="planForm" label-width="80px">
          <el-form-item label="用户"><span>{{ currentUser?.email }}</span></el-form-item>
          <el-form-item label="当前套餐">
            <span class="plan-tag" :class="currentUser?.plan_id">{{ currentUser?.plan_name }}</span>
          </el-form-item>
          <el-form-item label="目标套餐" required>
            <el-select v-model="planForm.plan_id">
              <el-option label="单棱MINI版" value="plan_mini" />
              <el-option label="复棱MAX版" value="plan_max" />
              <el-option label="晶曜PLUS版" value="plan_plus" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="planVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitPlan">确认</el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminUsers, getAdminUserDetail, adjustUserPoints, adjustUserPlan, toggleUserBan } from '@/api/admin'
import Layout from '@/components/Layout.vue'

const loading = ref(false)
const submitting = ref(false)

const users = ref<any[]>([])
const filters = reactive({
  search: '',
  plan_id: '',
  is_active: null as boolean | null
})
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const detailVisible = ref(false)
const pointsVisible = ref(false)
const planVisible = ref(false)
const currentUser = ref<any>(null)
const pointsForm = reactive({ amount: 0, reason: '' })
const planForm = reactive({ plan_id: '' })

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString('zh-CN')

const loadUsers = async () => {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.page_size }
    if (filters.search) params.search = filters.search
    if (filters.plan_id) params.plan_id = filters.plan_id
    if (filters.is_active !== null) params.is_active = filters.is_active

    const res: any = await getAdminUsers(params)
    const data = res.data
    if (data.status === 'ok') {
      users.value = data.users
      pagination.total = data.total
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; loadUsers() }

const viewUser = async (row: any) => {
  try {
    const res: any = await getAdminUserDetail(row.user_id)
    const data = res.data
    if (data.status === 'ok') { currentUser.value = data.user; detailVisible.value = true }
  } catch (error) { ElMessage.error('获取用户详情失败') }
}

const adjustPoints = (row: any) => { currentUser.value = row; pointsForm.amount = 0; pointsForm.reason = ''; pointsVisible.value = true }

const submitPoints = async () => {
  if (!pointsForm.reason) { ElMessage.warning('请输入调整原因'); return }
  submitting.value = true
  try {
    const res: any = await adjustUserPoints(currentUser.value.user_id, pointsForm.amount, pointsForm.reason)
    const data = res.data
    if (data.status === 'ok') { ElMessage.success(data.message); pointsVisible.value = false; loadUsers() }
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '调整失败') }
  finally { submitting.value = false }
}

const adjustPlan = (row: any) => { currentUser.value = row; planForm.plan_id = ''; planVisible.value = true }

const submitPlan = async () => {
  if (!planForm.plan_id) { ElMessage.warning('请选择目标套餐'); return }
  submitting.value = true
  try {
    const res: any = await adjustUserPlan(currentUser.value.user_id, planForm.plan_id)
    const data = res.data
    if (data.status === 'ok') { ElMessage.success(data.message); planVisible.value = false; loadUsers() }
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '调整失败') }
  finally { submitting.value = false }
}

const toggleBan = async (row: any) => {
  const action = row.is_active ? '封禁' : '解封'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${row.email} 吗？`, '确认操作', { type: 'warning' })
    const res: any = await toggleUserBan(row.user_id, !row.is_active)
    const data = res.data
    if (data.status === 'ok') { ElMessage.success(data.message); loadUsers() }
  } catch (error: any) { if (error !== 'cancel') ElMessage.error(error?.response?.data?.detail || '操作失败') }
}

onMounted(() => { loadUsers() })
</script>

<style scoped>
.admin-users-container { max-width: 100%; }

/* 页面头部 */
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 22px; font-weight: 600; color: #FFFFFF; margin: 0 0 8px 0; line-height: 1.3; }
.subtitle { font-size: 14px; color: #9CA3AF; margin: 0; }

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-bar .el-input { width: 240px; }
.filter-bar .el-select { width: 140px; }

/* 表格卡片 */
.table-card {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 20px;
  transition: border-color 0.25s ease;
}
.table-card:hover { border-color: #3B82F6; }

/* 自定义标签 */
.plan-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: #9CA3AF;
  background: #272727;
  white-space: nowrap;
}
.plan-tag.plan_mini { color: #9CA3AF; background: #272727; }
.plan-tag.plan_max { color: #F59E0B; background: rgba(245, 158, 11, 0.12); }
.plan-tag.plan_plus { color: #3B82F6; background: rgba(59, 130, 246, 0.12); }

.points { color: #3B82F6; font-weight: 600; }

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.status-badge.active { color: #10B981; background: rgba(16, 185, 129, 0.12); }
.status-badge.banned { color: #EF4444; background: rgba(239, 68, 68, 0.12); }

.text-danger { color: #EF4444; }

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
