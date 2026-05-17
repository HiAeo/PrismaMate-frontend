<template>
  <PublicLayout>
    <div class="legal-page">
      <div class="legal-container">
        <h1>{{ t('privacy.title') }}</h1>
        <p class="last-update">{{ t('privacy.lastUpdate') }}</p>

        <div class="content">
          <p>{{ t('privacy.intro') }}</p>

          <h2>{{ t('privacy.sections.collect.h2') }}</h2>
          <h3>{{ t('privacy.sections.collect.h3_1') }}</h3>
          <p>{{ t('privacy.sections.collect.p1') }}</p>

          <h3>{{ t('privacy.sections.collect.h3_2') }}</h3>
          <p>{{ t('privacy.sections.collect.p2') }}</p>

          <h3>{{ t('privacy.sections.collect.h3_3') }}</h3>
          <p>{{ t('privacy.sections.collect.p3') }}</p>

          <h2>{{ t('privacy.sections.usage.h2') }}</h2>
          <ul>
            <li>{{ t('privacy.sections.usage.li1') }}</li>
            <li>{{ t('privacy.sections.usage.li2') }}</li>
            <li>{{ t('privacy.sections.usage.li3') }}</li>
            <li>{{ t('privacy.sections.usage.li4') }}</li>
            <li>{{ t('privacy.sections.usage.li5') }}</li>
            <li>{{ t('privacy.sections.usage.li6') }}</li>
            <li>{{ t('privacy.sections.usage.li7') }}</li>
            <li>{{ t('privacy.sections.usage.li8') }}</li>
          </ul>

          <h2>{{ t('privacy.sections.share.h2') }}</h2>
          <h3>{{ t('privacy.sections.share.h3_1') }}</h3>
          <ul>
            <li>{{ t('privacy.sections.share.li1') }}</li>
            <li>{{ t('privacy.sections.share.li2') }}</li>
            <li>{{ t('privacy.sections.share.li3') }}</li>
          </ul>

          <h3>{{ t('privacy.sections.share.h3_2') }}</h3>
          <p>{{ t('privacy.sections.share.p1') }}</p>

          <h2>{{ t('privacy.sections.storage.h2') }}</h2>
          <h3>{{ t('privacy.sections.storage.h3_1') }}</h3>
          <p>{{ t('privacy.sections.storage.p1') }}</p>

          <h3>{{ t('privacy.sections.storage.h3_2') }}</h3>
          <ul>
            <li>{{ t('privacy.sections.storage.li1') }}</li>
            <li>{{ t('privacy.sections.storage.li2') }}</li>
            <li>{{ t('privacy.sections.storage.li3') }}</li>
          </ul>

          <h3>{{ t('privacy.sections.storage.h3_3') }}</h3>
          <p>{{ t('privacy.sections.storage.p2') }}</p>

          <h2>{{ t('privacy.sections.cookie.h2') }}</h2>
          <p>{{ t('privacy.sections.cookie.p1') }}</p>

          <h2>{{ t('privacy.sections.rights.h2') }}</h2>
          <p>{{ t('privacy.sections.rights.p1') }}</p>

          <h2>{{ t('privacy.sections.contact.h2') }}</h2>
          <p>{{ t('privacy.sections.contact.p1') }}</p>
          <ul>
            <li>{{ t('privacy.sections.contact.email1') }}</li>
            <li>{{ t('privacy.sections.contact.email2') }}</li>
          </ul>
          <p class="update-info">{{ t('privacy.sections.contact.reply') }}</p>
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

.content li strong {
  color: var(--foreground);
}

.update-info {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px dashed var(--border);
  font-style: italic;
  color: var(--muted);
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
