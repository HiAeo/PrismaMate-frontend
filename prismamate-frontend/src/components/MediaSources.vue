<template>
  <section class="media-sources-section">
    <div class="media-sources-inner">
      <!-- 特别鸣谢 -->
      <div class="section-title">
        <span class="title-dot"></span>
        <h2>{{ t('about.mediaSources.creditTitle') }}</h2>
      </div>

      <div class="media-grid credit-grid">
        <div
          v-for="logo in creditLogos"
          :key="logo.key"
          class="media-item"
        >
          <div class="media-logo">
            <img :src="logo.src" :alt="t('about.mediaSources.names.' + logo.key)" class="media-logo-img" loading="lazy" />
          </div>
          <span class="media-name">{{ t('about.mediaSources.names.' + logo.key) }}</span>
        </div>
      </div>


    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()

interface LogoItem {
  key: string
  src: string
}

const creditLogos: LogoItem[] = [
  { key: 'baiduCloud', src: '/media-logos/百度智能云_wordmark.svg' },
  { key: 'doubao', src: '/media-logos/豆包_wordmark.svg' },
  { key: 'jimeng', src: '/media-logos/即梦.svg' },
  { key: 'tencent', src: '/media-logos/腾讯.svg' },
  { key: 'hunyuan', src: '/media-logos/腾讯混元.svg' },
  { key: 'tongyi', src: '/media-logos/通义千问_wordmark.svg' },
  { key: 'iflytek', src: '/media-logos/讯飞开放平台.svg' },
  { key: 'chatglm', src: '/media-logos/ChatGLM (智谱)_wordmark.svg' },
  { key: 'coze', src: '/media-logos/Coze_wordmark.svg' },
  { key: 'gemini', src: '/media-logos/Gemini_wordmark.svg' },
  { key: 'githubCopilot', src: '/media-logos/Github Copilot_wordmark.svg' },
  { key: 'glama', src: '/media-logos/Glama_wordmark.svg' },
  { key: 'kimi', src: '/media-logos/Kimi.svg' },
  { key: 'meta', src: '/media-logos/Meta_wordmark.svg' },
  { key: 'ollama', src: '/media-logos/Ollama_wordmark.svg' },
  { key: 'openai', src: '/media-logos/OpenAI_wordmark.svg' }
]


</script>

<style scoped>
.media-sources-section {
  background: var(--background);
  padding: 64px 0 80px;
  border-top: 1px solid var(--border);
}

.media-sources-inner {
  max-width: var(--page-width);
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

/* 标题 - 与hero区域保持一致 */
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 48px;
}

.title-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #F59E0B;
  flex-shrink: 0;
}

.title-dot-red {
  background: #EF4444;
}

.section-title h2 {
  font-size: 14px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 0.02em;
  margin: 0;
}

/* 媒体网格 */
.media-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 16px 24px;
}

.media-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 12px 8px;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: default;
}

.media-item:hover {
  transform: translateY(-4px);
}

.media-item:hover .media-logo {
  transform: scale(1.06);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.media-item:hover .media-name {
  color: rgba(255, 255, 255, 0.8);
}

.media-logo {
  width: 100%;
  aspect-ratio: 2.5 / 1;
  max-width: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 10px 14px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.media-logo-img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
}

.media-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  text-align: center;
  line-height: 1.3;
  white-space: nowrap;
  transition: color 0.3s ease;
}

/* 响应式 */
@media (max-width: 1200px) {
  .media-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 900px) {
  .media-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 12px 16px;
  }
}

@media (max-width: 600px) {
  .media-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 10px 12px;
  }
  .section-title h2 {
    font-size: 13px;
  }
  .media-sources-section {
    padding: 40px 0 56px;
  }
}
</style>
