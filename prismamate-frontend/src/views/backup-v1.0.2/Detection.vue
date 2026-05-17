<template>
  <Layout>
    <div class="detection-container">
      <div class="page-header">
        <h1>创建检测任务</h1>
        <p class="subtitle">配置检测参数，开始品牌 AI 可见度检测</p>
      </div>
    
      <el-card class="form-card">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <!-- 品牌信息 -->
          <el-form-item label="检测品牌" prop="brands">
          <div v-for="(brand, index) in form.brands" :key="index" class="brand-item">
            <el-input v-model="brand.full_name" placeholder="品牌名称（如：华为）" style="width: 200px" />
            <el-input v-model="brand.short_names" placeholder="别名，逗号分隔（如：华为公司，Huawei）" style="width: 300px" />
            <el-button type="danger" :icon="Delete" circle @click="removeBrand(index)" />
          </div>
          <el-button type="primary" plain :icon="Plus" @click="addBrand">添加品牌</el-button>
          </el-form-item>

          <!-- 关键词 -->
          <el-form-item label="检测关键词" prop="keywords">
          <el-input
            v-model="keywordsInput"
            type="textarea"
            :rows="3"
            placeholder="请输入关键词，每行一个"
          />
          <div class="tip">每行一个关键词，将分别对每个关键词进行检测</div>
          </el-form-item>

          <!-- 平台选择 -->
          <el-form-item label="检测平台" prop="platforms">
          <el-checkbox-group v-model="form.platforms">
            <el-checkbox value="deepseek">DeepSeek</el-checkbox>
            <el-checkbox value="doubao">豆包</el-checkbox>
            <el-checkbox value="kimi">Kimi</el-checkbox>
          </el-checkbox-group>
          </el-form-item>

          <!-- 任务类型 -->
          <el-form-item label="任务类型">
          <el-radio-group v-model="form.task_type">
            <el-radio value="single">单次检测</el-radio>
            <el-radio value="recurring">周期性检测</el-radio>
          </el-radio-group>
          </el-form-item>

          <!-- 提交按钮 -->
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
              提交检测任务
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createTask } from '@/api/task'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'

const router = useRouter()

const formRef = ref()
const loading = ref(false)
const keywordsInput = ref('')

const form = reactive({
  brands: [{ full_name: '', short_names: '' }],
  platforms: ['deepseek'],
  task_type: 'single',
})

const rules = {
  brands: [
    { required: true, message: '请至少添加一个品牌', trigger: 'change' },
    {
      validator: (_rule: any, _value: any, callback: any) => {
        const validBrands = form.brands.filter(b => b.full_name.trim())
        if (validBrands.length === 0) {
          callback(new Error('请至少填写一个品牌名称'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
  platforms: [{ required: true, message: '请至少选择一个平台', trigger: 'change' }],
}

const keywords = computed(() => 
  keywordsInput.value.split('\n').map(k => k.trim()).filter(k => k)
)

function addBrand() {
  form.brands.push({ full_name: '', short_names: '' })
}

function removeBrand(index: number) {
  if (form.brands.length > 1) {
    form.brands.splice(index, 1)
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  if (keywords.value.length === 0) {
    ElMessage.warning('请至少输入一个关键词')
    return
  }

  loading.value = true
  try {
    const brands = form.brands
      .filter(b => b.full_name.trim())
      .map(b => ({
        full_name: b.full_name.trim(),
        short_names: b.short_names.split(',').map(s => s.trim()).filter(s => s),
      }))

    await createTask({
      brands,
      keywords: keywords.value,
      platforms: form.platforms,
      task_type: form.task_type,
    })
    
    ElMessage.success('任务创建成功')
    router.push('/reports')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.detection-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0;
}

.page-header {
  margin-bottom: var(--spacing-lg);
}

.page-header h1 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: 24px;
  color: var(--foreground);
}

.page-header .subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.form-card {
  margin-top: 0;
}

.brand-item {
  display: flex;
  gap: 10px;
  margin-bottom: var(--spacing-sm);
}

.tip {
  font-size: 12px;
  color: var(--muted);
  margin-top: 5px;
}
</style>
