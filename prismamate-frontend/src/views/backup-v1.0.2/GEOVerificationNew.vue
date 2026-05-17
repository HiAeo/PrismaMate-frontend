<template>
  <Layout>
    <div class="geo-verification-new-container">
      <div class="header">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1>新建 GEO 验证</h1>
      </div>

      <div class="dash-card form-card">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="120px"
        >
          <!-- 场景选择 -->
          <el-form-item label="验证场景">
            <el-radio-group v-model="form.scenario">
              <el-radio value="progress">进度验证（优化进行中）</el-radio>
              <el-radio value="delivery">交付验证（优化已完成）</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- GEO 机构名称 -->
          <el-form-item label="GEO 机构名称" prop="geo_company">
            <el-input
              v-model="form.geo_company"
              placeholder="请输入乙方 GEO 服务商名称（可选）"
              clearable
            />
          </el-form-item>

          <!-- 关键词 -->
          <el-form-item label="关键词" prop="keywords">
            <el-input
              v-model="keywordsInput"
              type="textarea"
              :rows="3"
              placeholder="请输入关键词，每行一个"
            />
            <div class="form-tip">多个关键词请用换行分隔</div>
          </el-form-item>

          <!-- 平台选择 -->
          <el-form-item label="优化平台" prop="platforms">
            <el-checkbox-group v-model="form.platforms">
              <el-checkbox value="deepseek">DeepSeek</el-checkbox>
              <el-checkbox value="kimi">Kimi</el-checkbox>
              <el-checkbox value="doubao">豆包</el-checkbox>
            </el-checkbox-group>
            <div class="form-tip">选择乙方优化的平台</div>
          </el-form-item>

          <!-- 交付验证数据上传 -->
          <template v-if="form.scenario === 'delivery'">
            <el-divider content-position="left">
              <span class="divider-title">乙方交付数据</span>
            </el-divider>

            <el-form-item label="数据录入方式">
              <el-radio-group v-model="dataInputMode">
                <el-radio value="manual">手动填写</el-radio>
                <el-radio value="json">粘贴 JSON</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 手动填写模式 -->
            <template v-if="dataInputMode === 'manual'">
              <div class="data-table">
                <el-table :data="claimedData" style="width: 100%" :header-cell-style="headerStyle">
                  <el-table-column label="品牌" width="120">
                    <template #default="{ row }">
                      <el-input v-model="row.brand" placeholder="品牌" />
                    </template>
                  </el-table-column>
                  <el-table-column label="关键词" width="120">
                    <template #default="{ row }">
                      <el-input v-model="row.keyword" placeholder="关键词" />
                    </template>
                  </el-table-column>
                  <el-table-column label="平台" width="120">
                    <template #default="{ row }">
                      <el-select v-model="row.platform" placeholder="平台">
                        <el-option value="deepseek" label="DeepSeek" />
                        <el-option value="kimi" label="Kimi" />
                        <el-option value="doubao" label="豆包" />
                      </el-select>
                    </template>
                  </el-table-column>
                  <el-table-column label="是否提及" width="100">
                    <template #default="{ row }">
                      <el-switch v-model="row.is_mentioned" />
                    </template>
                  </el-table-column>
                  <el-table-column label="位次" width="80">
                    <template #default="{ row }">
                      <el-input-number
                        v-model="row.mention_position"
                        :min="1"
                        :max="100"
                        controls-position="right"
                        style="width: 70px"
                      />
                    </template>
                  </el-table-column>
                  <el-table-column label="提及率%" width="100">
                    <template #default="{ row }">
                      <el-input-number
                        v-model="row.mention_rate"
                        :min="0"
                        :max="100"
                        :precision="1"
                        controls-position="right"
                        style="width: 80px"
                      />
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="60">
                    <template #default="{ $index }">
                      <el-button
                        type="danger"
                        size="small"
                        text
                        @click="removeClaimedData($index)"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-button type="primary" text @click="addClaimedData">
                  添加数据
                </el-button>
              </div>
            </template>

            <!-- JSON 粘贴模式 -->
            <template v-else>
              <el-form-item label="JSON 数据">
                <el-input
                  v-model="jsonInput"
                  type="textarea"
                  :rows="8"
                  placeholder='粘贴 JSON 格式数据，例如：
[
  {
    "brand": "华为",
    "keyword": "手机",
    "platform": "deepseek",
    "is_mentioned": true,
    "mention_position": 3,
    "mention_rate": 85.5
  }
]'
                />
              </el-form-item>
              <el-button type="primary" @click="parseJsonData" :loading="jsonParsing">
                解析 JSON
              </el-button>
            </template>
          </template>

          <!-- 提交按钮 -->
          <el-form-item>
            <el-button type="primary" @click="submitForm" :loading="submitting">
              {{ form.scenario === 'delivery' ? '上传数据并检测' : '提交并开始检测' }}
            </el-button>
            <el-button @click="goBack">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import Layout from '@/components/Layout.vue'
import api from '@/api/axios'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const submitting = ref(false)
const jsonParsing = ref(false)
const dataInputMode = ref('manual')
const keywordsInput = ref('')
const jsonInput = ref('')

const form = reactive({
  scenario: 'progress',
  geo_company: '',
  keywords: [],
  platforms: []
})

const claimedData = ref([])

const rules = {
  scenario: [{ required: true, message: '请选择验证场景', trigger: 'change' }],
  keywords: [{ required: true, message: '请输入关键词', trigger: 'blur' }],
  platforms: [
    { required: true, message: '请选择至少一个平台', trigger: 'change' }
  ]
}

const headerStyle = () => ({
  background: 'transparent',
  color: 'rgba(255,255,255,0.5)',
  fontWeight: 600,
  fontSize: '13px',
  borderBottom: '1px solid rgba(255,255,255,0.1)'
})

const parseKeywords = () => {
  form.keywords = keywordsInput.value
    .split('\n')
    .map(k => k.trim())
    .filter(k => k.length > 0)
}

const addClaimedData = () => {
  claimedData.value.push({
    brand: '',
    keyword: '',
    platform: '',
    is_mentioned: false,
    mention_position: null,
    mention_rate: null
  })
}

const removeClaimedData = (index) => {
  claimedData.value.splice(index, 1)
}

const parseJsonData = () => {
  jsonParsing.value = true
  try {
    const data = JSON.parse(jsonInput.value)
    if (Array.isArray(data)) {
      claimedData.value = data.map(item => ({
        brand: item.brand || '',
        keyword: item.keyword || '',
        platform: item.platform || '',
        is_mentioned: item.is_mentioned ?? false,
        mention_position: item.mention_position || null,
        mention_rate: item.mention_rate || null
      }))
      ElMessage.success(`成功解析 ${data.length} 条数据`)
    } else {
      ElMessage.error('JSON 必须是数组格式')
    }
  } catch (e) {
    ElMessage.error('JSON 解析失败: ' + e.message)
  } finally {
    jsonParsing.value = false
  }
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  parseKeywords()

  if (form.keywords.length === 0) {
    ElMessage.warning('请输入至少一个关键词')
    return
  }

  if (form.platforms.length === 0) {
    ElMessage.warning('请选择至少一个平台')
    return
  }

  submitting.value = true

  try {
    const requestData = {
      scenario: form.scenario,
      geo_plan: {
        keywords: form.keywords,
        platforms: form.platforms,
        geo_company: form.geo_company || null
      },
      geo_claimed_data: form.scenario === 'delivery' ? claimedData.value : null
    }

    const uploadRes = await api.post('/geo-verification/upload', requestData)
    const verificationId = uploadRes.verification_id

    ElMessage.success('数据上传成功，开始检测...')

    await api.post(`/geo-verification/${verificationId}/detect`)

    ElMessage.success('检测完成')

    router.push({ name: 'GEOVerificationReport', params: { id: verificationId } })

  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败: ' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push({ name: 'GEOVerification' })
}

onMounted(() => {
  if (route.query.scenario) {
    form.scenario = route.query.scenario
  }
})
</script>

<style scoped>
.geo-verification-new-container {
  max-width: 100%;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #FFFFFF;
}

/* 通用卡片 */
.dash-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.dash-card:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.18);
}

.form-card {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.data-table {
  padding: 0 0 16px 0;
}

.data-table .el-table {
  margin-bottom: 12px;
}

.divider-title {
  font-weight: 600;
  color: #FFFFFF;
}
</style>
