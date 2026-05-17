<template>
  <PublicLayout>
    <div class="legal-page">
      <div class="legal-container">
        <h1>{{ t('terms.title') }}</h1>
        <p class="last-update">{{ t('terms.lastUpdate') }}</p>

        <div class="content">
          <h2>{{ t('terms.sections.service.h2') }}</h2>
          <p>{{ t('terms.sections.service.p1') }}</p>
          <p>{{ t('terms.sections.service.p2') }}</p>

          <h2>{{ t('terms.sections.account.h2') }}</h2>
          <h3>{{ t('terms.sections.account.h3_1') }}</h3>
          <p>{{ t('terms.sections.account.p1') }}</p>

          <h3>{{ t('terms.sections.account.h3_2') }}</h3>
          <p>{{ t('terms.sections.account.p2') }}</p>

          <h2>{{ t('terms.sections.usage.h2') }}</h2>
          <h3>{{ t('terms.sections.usage.h3_1') }}</h3>
          <p>{{ t('terms.sections.usage.p1') }}</p>
          <ul>
            <li>{{ t('terms.sections.usage.li1') }}</li>
            <li>{{ t('terms.sections.usage.li2') }}</li>
            <li>{{ t('terms.sections.usage.li3') }}</li>
            <li>{{ t('terms.sections.usage.li4') }}</li>
            <li>{{ t('terms.sections.usage.li5') }}</li>
          </ul>

          <h3>{{ t('terms.sections.usage.h3_2') }}</h3>
          <p>{{ t('terms.sections.usage.p2') }}</p>
          <ul>
            <li>{{ t('terms.sections.usage.li6') }}</li>
            <li>{{ t('terms.sections.usage.li7') }}</li>
            <li>{{ t('terms.sections.usage.li8') }}</li>
            <li>{{ t('terms.sections.usage.li9') }}</li>
            <li>{{ t('terms.sections.usage.li10') }}</li>
          </ul>

          <h2>{{ t('terms.sections.ip.h2') }}</h2>
          <p>{{ t('terms.sections.ip.p1') }}</p>

          <h2>{{ t('terms.sections.data.h2') }}</h2>
          <p>{{ t('terms.sections.data.p1') }}</p>

          <h2>{{ t('terms.sections.disclaimer.h2') }}</h2>
          <p>{{ t('terms.sections.disclaimer.p1') }}</p>
          <ul>
            <li>{{ t('terms.sections.disclaimer.li1') }}</li>
            <li>{{ t('terms.sections.disclaimer.li2') }}</li>
            <li>{{ t('terms.sections.disclaimer.li3') }}</li>
            <li>{{ t('terms.sections.disclaimer.li4') }}</li>
          </ul>

          <h2>{{ t('terms.sections.termination.h2') }}</h2>
          <p>{{ t('terms.sections.termination.p1') }}</p>

          <h2>{{ t('terms.sections.contact.h2') }}</h2>
          <p>{{ t('terms.sections.contact.p1') }}</p>
          <ul>
            <li>{{ t('terms.sections.contact.email') }}</li>
          </ul>
        </div>
      </div>
    </div>
  </PublicLayout>
</template>

<script setup lang="ts">
import PublicLayout from '@/components/PublicLayout.vue'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
</script>

<style scoped>
.legal-page {
  background: var(--background);
  min-height: 100vh;
}

.legal-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.legal-container h1 {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 12px;
}

.last-update {
  text-align: center;
  color: var(--muted);
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.content h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--foreground);
  margin-top: 32px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.content h2:first-child {
  margin-top: 0;
}

.content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--foreground);
  margin-top: 24px;
  margin-bottom: 12px;
}

.content p {
  line-height: 1.8;
  color: var(--foreground);
  opacity: 0.8;
  margin-bottom: 12px;
  text-align: justify;
}

.content ul {
  margin: 12px 0;
  padding-left: 24px;
}

.content li {
  line-height: 1.8;
  color: var(--foreground);
  opacity: 0.8;
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .legal-container {
    padding: 24px 16px;
  }

  .legal-container h1 {
    font-size: 28px;
  }
}
</style>
