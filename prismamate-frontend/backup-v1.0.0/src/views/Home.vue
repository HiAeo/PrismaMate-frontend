<template>
  <PublicLayout>
    <!-- ==================== 区块一：Hero 区 ==================== -->
    <section class="hero-section">
      <!-- 公告条 -->
      <div class="announcement-bar">
        <span class="announcement-dot"></span>
        <span class="announcement-text">PrismaMate GEO检测引擎已全面升级，支持 DeepSeek、Kimi、豆包 三大平台。</span>
      </div>

      <div class="hero-grid page-container">
        <!-- 左侧文案 -->
        <div class="hero-left">
          <div class="hero-tag"><span class="tag-dot"></span>GEO生成式引擎优化第三方检测平台</div>
          <h1 class="hero-title">
            <span class="title-line">PrismaMate</span>
            <span class="title-line">棱镜报告</span>
          </h1>
          <p class="hero-subtitle">让AI时代的品牌竞争，建立在真实数据之上。</p>
          <div class="hero-buttons">
            <a href="/health-check/new" class="hero-btn">
              AI 可见度体检报告
            </a>
            <a href="/geo-verification" class="hero-btn">
              GEO 效果检测报告
            </a>
            <a href="/verify" class="hero-btn">
              棱镜报告防篡改验真
            </a>
          </div>
        </div>

        <!-- 右侧视觉 - 三大模型卡片 -->
        <div class="hero-right">
          <div class="cards-container">
            <div
              v-for="(card, index) in llmCards"
              :key="card.id"
              class="llm-card"
              :class="[`llm-card-${card.id}`, { 'is-hovered': hoveredCard === card.id }]"
              :style="{ animationDelay: `${index * 0.15}s` }"
              @mouseenter="hoveredCard = card.id"
              @mouseleave="hoveredCard = null"
              @click="openUrl(card.url)"
            >
              <div class="card-header">
                <div class="card-logo">
                  <component :is="card.logoComponent" class="logo-icon" />
                </div>
                <div class="card-info">
                  <component :is="card.nameComponent" class="name-icon" />
                </div>
                <div class="card-badge" :class="`badge-${card.id}`">{{ card.badge }}</div>
              </div>
              <div class="card-metrics">
                <div class="metric">
                  <span class="metric-label">品牌提及</span>
                  <span class="metric-value">{{ card.mentions }}</span>
                </div>
                <div class="metric">
                  <span class="metric-label">排名</span>
                  <span class="metric-value rank">{{ card.rank }}</span>
                </div>
              </div>
              <div class="card-chart">
                <!-- DeepSeek: 曲线面积图 -->
                <template v-if="card.id === 'deepseek'">
                  <svg viewBox="0 0 260 40" height="40" class="chart-svg">
                    <defs>
                      <linearGradient id="dsGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#4D6BFE" stop-opacity="0.35"/>
                        <stop offset="100%" stop-color="#4D6BFE" stop-opacity="0"/>
                      </linearGradient>
                    </defs>
                    <path d="M0,32 C12,32 18,22 32,24 C46,26 52,12 66,17 C80,22 86,30 100,23 C114,16 120,34 134,26 C148,18 154,10 168,17 C182,24 188,34 202,27 C216,20 222,32 236,28 C250,24 260,32 260,32 L260,40 L0,40 Z" fill="url(#dsGrad)"/>
                    <path d="M0,32 C12,32 18,22 32,24 C46,26 52,12 66,17 C80,22 86,30 100,23 C114,16 120,34 134,26 C148,18 154,10 168,17 C182,24 188,34 202,27 C216,20 222,32 236,28 C250,24 260,32 260,32" fill="none" stroke="#4D6BFE" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </template>
                <!-- Kimi: 柱形图 -->
                <template v-if="card.id === 'kimi'">
                  <svg viewBox="0 0 260 40" height="40" class="chart-svg">
                    <rect x="2" y="22" width="16" height="18" rx="3" fill="#1783FF" opacity="0.3"/>
                    <rect x="22" y="12" width="16" height="28" rx="3" fill="#1783FF" opacity="0.5"/>
                    <rect x="42" y="4" width="16" height="36" rx="3" fill="#1783FF"/>
                    <rect x="62" y="16" width="16" height="24" rx="3" fill="#1783FF" opacity="0.4"/>
                    <rect x="82" y="8" width="16" height="32" rx="3" fill="#1783FF" opacity="0.65"/>
                    <rect x="102" y="20" width="16" height="20" rx="3" fill="#1783FF" opacity="0.35"/>
                    <rect x="122" y="10" width="16" height="30" rx="3" fill="#1783FF" opacity="0.55"/>
                    <rect x="142" y="24" width="16" height="16" rx="3" fill="#1783FF" opacity="0.3"/>
                    <rect x="162" y="14" width="16" height="26" rx="3" fill="#1783FF" opacity="0.45"/>
                    <rect x="182" y="18" width="16" height="22" rx="3" fill="#1783FF" opacity="0.4"/>
                    <rect x="202" y="26" width="16" height="14" rx="3" fill="#1783FF" opacity="0.25"/>
                    <rect x="222" y="16" width="16" height="24" rx="3" fill="#1783FF" opacity="0.5"/>
                    <rect x="242" y="22" width="16" height="18" rx="3" fill="#1783FF" opacity="0.35"/>
                  </svg>
                </template>
                <!-- 豆包: 饼图 -->
                <template v-if="card.id === 'doubao'">
                  <svg viewBox="0 0 260 40" height="40" class="chart-svg">
                    <path d="M 110 6 A 14 14 0 0 1 124 20" fill="none" stroke="#37E1BE" stroke-width="2.5" opacity="0.6" stroke-linecap="round"/>
                    <path d="M 124 20 A 14 14 0 0 1 110 34" fill="none" stroke="#37E1BE" stroke-width="2.5" opacity="0.35" stroke-linecap="round"/>
                    <path d="M 110 34 A 14 14 0 1 1 110 6" fill="none" stroke="#37E1BE" stroke-width="2.5" opacity="0.12" stroke-linecap="round"/>
                    <path d="M 145 12 A 8 8 0 0 1 153 20" fill="none" stroke="#37E1BE" stroke-width="2" opacity="0.45" stroke-linecap="round"/>
                    <path d="M 153 20 A 8 8 0 0 1 145 28" fill="none" stroke="#37E1BE" stroke-width="2" opacity="0.25" stroke-linecap="round"/>
                    <path d="M 145 28 A 8 8 0 1 1 145 12" fill="none" stroke="#37E1BE" stroke-width="2" opacity="0.1" stroke-linecap="round"/>
                    <circle cx="175" cy="20" r="5" fill="#37E1BE" opacity="0.5"/>
                  </svg>
                </template>
                <span class="chart-score">{{ card.score }}分</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 区块八：页脚（PublicLayout 内置） ==================== -->
  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import PublicLayout from '@/components/PublicLayout.vue'
import DeepSeekLogo from '@/components/icons/DeepSeekLogo.vue'
import DeepSeekText from '@/components/icons/DeepSeekText.vue'
import KimiLogo from '@/components/icons/KimiLogo.vue'
import KimiText from '@/components/icons/KimiText.vue'
import DoubaoLogo from '@/components/icons/DoubaoLogo.vue'
import DoubaoText from '@/components/icons/DoubaoText.vue'

const hoveredCard = ref<string | null>(null)

function openUrl(url: string) {
  window.open(url, '_blank')
}

const llmCards = [
  {
    id: 'deepseek',
    name: 'DeepSeek',
    logoComponent: markRaw(DeepSeekLogo),
    nameComponent: markRaw(DeepSeekText),
    badge: '推荐',
    mentions: '4/5',
    rank: '#1',
    score: 88,
    url: 'https://chat.deepseek.com'
  },
  {
    id: 'kimi',
    name: 'Kimi',
    logoComponent: markRaw(KimiLogo),
    nameComponent: markRaw(KimiText),
    badge: '热门',
    mentions: '3/5',
    rank: '#2',
    score: 72,
    url: 'https://kimi.moonshot.cn'
  },
  {
    id: 'doubao',
    name: '豆包',
    logoComponent: markRaw(DoubaoLogo),
    nameComponent: markRaw(DoubaoText),
    badge: '新增',
    mentions: '2/5',
    rank: '#4',
    score: 45,
    url: 'https://www.doubao.com'
  }
]
</script>

<style scoped>
/* === Hero 区 === */
.hero-section {
  background: #000000;
  min-height: calc(100vh - 64px);
  padding: 32px 0 80px;
  display: flex;
  flex-direction: column;
}

.announcement-bar {
  text-align: center;
  margin-bottom: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.announcement-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
  display: inline-block;
  flex-shrink: 0;
}

.announcement-text {
  color: rgba(255, 255, 255, 0.45);
  font-size: 13px;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 140px;
  align-items: center;
  flex: 1;
}

.hero-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transform: translateX(-60px);
}

.hero-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
  margin-bottom: 24px;
  letter-spacing: 0.02em;
}

.tag-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4D9FFF;
  flex-shrink: 0;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.15;
  letter-spacing: -0.03em;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 20px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.55);
  margin-bottom: 36px;
}

.title-line {
  display: block;
}

.hero-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  font-weight: 400;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  text-decoration: none;
  transition: all 0.25s ease;
}

.hero-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
  transform: translateX(4px);
}

/* 右侧视觉 - 三大模型卡片 */
.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}

.cards-container {
  position: relative;
  width: 100%;
  height: 500px;
}

.llm-card {
  position: absolute;
  width: 360px;
  left: 50%;
  top: 120px;
  margin-left: -180px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 22px 26px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  backdrop-filter: blur(16px);
  --rotate: 0deg;
  --tx: 0px;
  --ty: 0px;
  transform: rotate(var(--rotate)) translateX(var(--tx)) translateY(var(--ty));
  animation: slideInRight 0.6s ease-out both;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: rotate(var(--rotate)) translateX(calc(var(--tx) + 30px)) translateY(var(--ty));
  }
  to {
    opacity: 1;
    transform: rotate(var(--rotate)) translateX(var(--tx)) translateY(var(--ty));
  }
}

/* 扇子布局 */
.llm-card-deepseek {
  --rotate: -14deg;
  --tx: -170px;
  --ty: 60px;
  z-index: 3;
}

.llm-card-doubao {
  --rotate: 14deg;
  --tx: 170px;
  --ty: 60px;
  z-index: 2;
}

.llm-card-kimi {
  --rotate: 0deg;
  --tx: 0px;
  --ty: -30px;
  z-index: 1;
}

.llm-card:hover,
.llm-card.is-hovered {
  z-index: 10;
  background: rgba(255, 255, 255, 0.14);
}

.llm-card-deepseek:hover,
.llm-card-deepseek.is-hovered {
  transform: rotate(-10deg) translateX(-170px) translateY(48px) scale(1.03);
  border-color: rgba(77, 107, 254, 0.4);
  box-shadow: 0 8px 32px rgba(77, 107, 254, 0.15);
}

.llm-card-kimi:hover,
.llm-card-kimi.is-hovered {
  transform: rotate(0deg) translateY(-40px) scale(1.03);
  border-color: rgba(23, 131, 255, 0.4);
  box-shadow: 0 8px 32px rgba(23, 131, 255, 0.15);
}

.llm-card-doubao:hover,
.llm-card-doubao.is-hovered {
  transform: rotate(10deg) translateX(170px) translateY(48px) scale(1.03);
  border-color: rgba(55, 225, 190, 0.4);
  box-shadow: 0 8px 32px rgba(55, 225, 190, 0.15);
}

.llm-card .card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.card-logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.llm-card-deepseek .card-logo { background: rgba(77, 107, 254, 0.15); }
.llm-card-kimi .card-logo { background: rgba(23, 131, 255, 0.15); }
.llm-card-doubao .card-logo { background: rgba(55, 225, 190, 0.15); }

.logo-icon {
  width: 32px;
  height: 32px;
}

.name-icon {
  height: 26px;
  width: auto;
  display: block;
}

.card-info {
  flex: 1;
  display: flex;
  align-items: center;
}

.card-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 6px;
  flex-shrink: 0;
}

.badge-deepseek {
  background: rgba(77, 107, 254, 0.2);
  color: #4D6BFE;
}

.badge-kimi {
  background: rgba(23, 131, 255, 0.2);
  color: #1783FF;
}

.badge-doubao {
  background: rgba(55, 225, 190, 0.2);
  color: #37E1BE;
}

.card-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.metric-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.metric-value.rank {
  color: #10B981;
}

.llm-card-doubao .metric-value.rank {
  color: rgba(255, 255, 255, 0.5);
}

.card-chart {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 44px;
}

.chart-svg {
  flex: 1;
  height: 40px;
  width: auto;
  overflow: visible;
}

.chart-score {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.45);
  white-space: nowrap;
}

@media (max-width: 900px) {
  .hero-grid {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 48px;
  }
  .hero-left {
    align-items: center;
  }
  .hero-title {
    font-size: 40px;
  }
  .hero-right {
    display: none;
  }
}
</style>