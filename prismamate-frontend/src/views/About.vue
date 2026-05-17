<template>
  <PublicLayout>
    <div class="about-page">
      <!-- 区块一：品牌故事 -->
      <section class="about-section">
        <h2 class="section-title">
          <span class="dot dot-red"></span>
          {{ t('about.brandStory.title') }}
        </h2>
        <div class="section-content">
          <h3 class="brand-name">{{ t('about.brandStory.brandName') }}</h3>
          <p class="story-text">
            {{ t('about.brandStory.story1') }}
          </p>
          <p class="story-text">
            {{ t('about.brandStory.story2') }}
          </p>
          <p class="story-highlight">
            {{ t('about.brandStory.highlight') }}
          </p>
        </div>
      </section>

      <!-- 区块二：使命愿景 -->
      <section class="about-section">
        <h2 class="section-title">
          <span class="dot dot-orange"></span>
          {{ t('about.mission.title') }}
        </h2>
        <div class="section-content">
          <h3 class="mission-text">{{ t('about.mission.missionText') }}</h3>
          <p class="story-text">
            {{ t('about.mission.para1') }}
          </p>
          <p class="story-text">
            {{ t('about.mission.para2') }}
          </p>
          <p class="story-text">
            {{ t('about.mission.para3') }}
          </p>
        </div>
      </section>

      <!-- 区块三：核心产品 -->
      <section class="about-section products-section">
        <h2 class="section-title">
          <span class="dot dot-blue"></span>
          {{ t('about.products.title') }}
        </h2>
        <div class="products-grid">
          <!-- 卡片一 -->
          <div class="product-card">
            <h3 class="card-title">{{ t('about.products.card1.title') }}<br><span class="title-line">— {{ t('about.products.card1.subtitle') }} —</span></h3>
            <p class="card-desc">
              {{ t('about.products.card1.desc') }}
            </p>
          </div>

          <!-- 卡片二 -->
          <div class="product-card">
            <h3 class="card-title">{{ t('about.products.card2.title') }}<br><span class="title-line">— {{ t('about.products.card2.subtitle') }} —</span></h3>
            <p class="card-desc">
              {{ t('about.products.card2.desc') }}
            </p>
          </div>

          <!-- 卡片三 -->
          <div class="product-card">
            <h3 class="card-title">{{ t('about.products.card3.title') }}<br><span class="title-line">— {{ t('about.products.card3.subtitle') }} —</span></h3>
            <p class="card-desc">
              {{ t('about.products.card3.desc') }}
            </p>
          </div>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>

<script setup lang="ts">
import PublicLayout from '@/components/PublicLayout.vue'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
</script>

<style scoped>
.about-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 24px 100px;
}

/* 区块通用样式 */
.about-section {
  margin-bottom: 80px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 彩色光圈圆点 */
.dot {
  position: relative;
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 50%;
  animation: pulse-ring 2s ease-out infinite;
}

.dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: currentColor;
}

.dot-red {
  color: #EF4444;
}

.dot-red::before {
  box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
}

.dot-orange {
  color: #F59E0B;
}

.dot-orange::before {
  box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4);
}

.dot-blue {
  color: #3B82F6;
}

.dot-blue::before {
  box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
}

/* 光圈脉冲动画 */
@keyframes pulse-ring {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

/* 品牌故事 */
.brand-name {
  font-size: 28px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 24px;
  letter-spacing: 0.02em;
}

.story-text {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 16px;
}

.story-highlight {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 24px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.04);
  border-left: 3px solid rgba(255, 255, 255, 0.2);
  border-radius: 0 8px 8px 0;
}

/* 使命愿景 */
.mission-text {
  font-size: 22px;
  font-weight: 500;
  color: #FFFFFF;
  margin-bottom: 24px;
  line-height: 1.5;
}

/* 核心产品 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.product-card {
  position: relative;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.04) 100%);
  border: 1px solid rgba(59, 130, 246, 0.18);
  border-radius: 16px;
  padding: 28px 24px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: default;
  backdrop-filter: blur(16px);
  overflow: hidden;
}

/* 顶部光感条 */
.product-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.5), transparent);
}

.product-card:hover {
  transform: translateY(-4px);
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.16) 0%, rgba(37, 99, 235, 0.08) 100%);
  border-color: rgba(96, 165, 250, 0.35);
  box-shadow:
    0 12px 40px rgba(0, 0, 0, 0.3),
    0 0 30px rgba(59, 130, 246, 0.12);
}

.card-title {
  position: relative;
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 16px;
  padding-bottom: 16px;
  line-height: 1.5;
  text-align: center;
}

.card-title .title-line {
  display: block;
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

.card-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 1px;
}

.card-desc {
  font-size: 14px;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.65);
}

/* 响应式 */
@media (max-width: 900px) {
  .about-page {
    padding: 40px 20px 80px;
  }

  .about-section {
    margin-bottom: 60px;
  }

  .products-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .brand-name {
    font-size: 24px;
  }

  .mission-text {
    font-size: 20px;
  }

  .product-card {
    padding: 24px 20px;
  }
}

@media (max-width: 600px) {
  .about-page {
    padding: 32px 16px 60px;
  }

  .section-title {
    font-size: 13px;
  }

  .brand-name {
    font-size: 22px;
  }

  .mission-text {
    font-size: 18px;
  }

  .story-text {
    font-size: 14px;
  }

  .card-title {
    font-size: 15px;
  }

  .card-desc {
    font-size: 13px;
  }
}
</style>
