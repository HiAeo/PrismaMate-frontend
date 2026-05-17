<template>
  <Layout>
    <div class="health-check-templates-page">
      <!-- 页面标题 -->
      <div class="header">
        <h1>我的模板</h1>
        <p class="subtitle">管理体检模板，快速发起重复检测</p>
      </div>

      <!-- 模板列表 -->
      <div class="templates-section">
        <el-row :gutter="16" v-if="templates.length > 0">
          <el-col :span="8" v-for="template in templates" :key="template.template_id">
            <div class="dash-card template-card">
              <div class="card-header">
                <span class="template-name">{{ template.name }}</span>
                <el-dropdown @command="(cmd: string) => handleCommand(cmd, template)">
                  <el-icon class="more-icon"><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="run">
                        一键检测
                      </el-dropdown-item>
                      <el-dropdown-item command="edit">
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>

              <div class="template-info">
                <div class="info-item">
                  <span class="info-label">品牌</span>
                  <span class="info-value">{{ template.brands?.length || 0 }} 个</span>
                </div>
                <div class="info-item">
                  <span class="info-label">关键词</span>
                  <span class="info-value">{{ template.keywords?.length || 0 }} 个</span>
                </div>
                <div class="info-item">
                  <span class="info-label">平台</span>
                  <span class="info-value">{{ template.platforms?.join(', ') }}</span>
                </div>
                <div class="info-item" v-if="template.last_used_at">
                  <span class="info-label">上次使用</span>
                  <span class="info-value muted">{{ formatTime(template.last_used_at) }}</span>
                </div>
                <div class="info-item" v-else>
                  <span class="info-label">上次使用</span>
                  <span class="info-value muted">从未使用</span>
                </div>
              </div>

              <div class="template-actions">
                <el-button type="primary" size="small" @click="runTemplate(template)">
                  一键检测
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-empty v-else description="暂无保存的模板">
          <el-button type="primary" @click="$router.push('/health-check/new')">
            新建体检
          </el-button>
        </el-empty>
      </div>

      <!-- 编辑模板对话框 -->
      <el-dialog
        v-model="editDialogVisible"
        title="编辑模板"
        width="500px"
      >
        <el-form :model="editingTemplate" label-position="top">
          <el-form-item label="模板名称">
            <el-input v-model="editingTemplate.name" placeholder="输入模板名称" />
          </el-form-item>
          <el-form-item label="关键词">
            <el-input
              v-model="editingTemplate.keywordsInput"
              type="textarea"
              :rows="3"
              placeholder="多个关键词用换行分隔"
            />
          </el-form-item>
          <el-form-item label="平台">
            <el-select v-model="editingTemplate.platforms" multiple style="width: 100%">
              <el-option label="DeepSeek" value="DeepSeek" />
              <el-option label="Kimi" value="Kimi" />
              <el-option label="豆包" value="Doubao" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate" :loading="saving">保存</el-button>
        </template>
      </el-dialog>

      <!-- 删除确认对话框 -->
      <el-dialog
        v-model="deleteDialogVisible"
        title="删除模板"
        width="400px"
      >
        <p>确定要删除模板「{{ deletingTemplate?.name }}」吗？</p>
        <p class="delete-hint">删除后无法恢复，但不影响已生成的报告。</p>
        <template #footer>
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleting">删除</el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import api from '@/api/axios'

const router = useRouter()

const templates = ref<any[]>([])

const editDialogVisible = ref(false)
const editingTemplate = reactive({
  template_id: '',
  name: '',
  keywords: [] as string[],
  keywordsInput: '',
  platforms: [] as string[]
})
const saving = ref(false)

const deleteDialogVisible = ref(false)
const deletingTemplate = ref<any>(null)
const deleting = ref(false)

const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleDateString('zh-CN')
}

const loadTemplates = async () => {
  try {
    const data = await api.get(`/templates`)
    templates.value = data || []
  } catch (err: any) {
    console.error('加载模板失败', err)
    ElMessage.error('加载模板失败')
  }
}

const handleCommand = (command: string, template: any) => {
  switch (command) {
    case 'run': runTemplate(template); break
    case 'edit': openEditDialog(template); break
    case 'delete': openDeleteDialog(template); break
  }
}

const runTemplate = async (template: any) => {
  try {
    const data = await api.post(`/templates/${template.template_id}/run`)
    const params = data.detection_params

    router.push({
      path: '/health-check/new',
      query: {
        template_id: template.template_id,
        keywords: params.keywords?.join('\n'),
        platforms: params.platforms?.join(','),
        brands: params.brands?.map((b: any) => b.full_name).join(',')
      }
    })
  } catch (err: any) {
    console.error('使用模板失败', err)
    ElMessage.error('使用模板失败')
  }
}

const openEditDialog = (template: any) => {
  editingTemplate.template_id = template.template_id
  editingTemplate.name = template.name
  editingTemplate.keywords = template.keywords || []
  editingTemplate.keywordsInput = (template.keywords || []).join('\n')
  editingTemplate.platforms = template.platforms || []
  editDialogVisible.value = true
}

const saveTemplate = async () => {
  if (!editingTemplate.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }

  const keywords = editingTemplate.keywordsInput
    .split(/[\n,]/)
    .map(k => k.trim())
    .filter(k => k.length > 0)

  if (keywords.length === 0) {
    ElMessage.warning('请输入至少一个关键词')
    return
  }

  saving.value = true
  try {
    await api.put(`/templates/${editingTemplate.template_id}`, {
      name: editingTemplate.name.trim(),
      keywords,
      platforms: editingTemplate.platforms
    })
    ElMessage.success('模板已保存')
    editDialogVisible.value = false
    loadTemplates()
  } catch (err: any) {
    console.error('保存模板失败', err)
    ElMessage.error('保存模板失败')
  } finally {
    saving.value = false
  }
}

const openDeleteDialog = (template: any) => {
  deletingTemplate.value = template
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!deletingTemplate.value) return

  deleting.value = true
  try {
    await api.delete(`/templates/${deletingTemplate.value.template_id}`)
    ElMessage.success('模板已删除')
    deleteDialogVisible.value = false
    loadTemplates()
  } catch (err: any) {
    console.error('删除模板失败', err)
    ElMessage.error('删除模板失败')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.health-check-templates-page {
  max-width: 100%;
}

.header {
  margin-bottom: 24px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #FFFFFF;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
}

.templates-section {
  min-height: 300px;
}

/* 通用卡片 */
.dash-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  margin-bottom: 16px;
}

.dash-card:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.18);
}

.template-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
}

.more-icon {
  cursor: pointer;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.45);
  transition: color 0.2s;
}

.more-icon:hover {
  color: #FFFFFF;
}

.template-info {
  flex: 1;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 14px;
}

.info-label {
  color: rgba(255, 255, 255, 0.45);
  min-width: 56px;
}

.info-value {
  color: rgba(255, 255, 255, 0.85);
}

.info-value.muted {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

.template-actions {
  display: flex;
  justify-content: center;
}

.delete-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
}
</style>
