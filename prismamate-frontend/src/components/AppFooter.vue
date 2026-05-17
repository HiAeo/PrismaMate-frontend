<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-links">
        <router-link to="/about">{{ t('footer.about') }}</router-link>
        <router-link to="/pricing">{{ t('footer.pricing') }}</router-link>
        <router-link to="/terms">{{ t('footer.terms') }}</router-link>
        <router-link to="/privacy">{{ t('footer.privacy') }}</router-link>
      </div>
      <div class="footer-copyright">
        {{ t('footer.copyright') }}
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useI18n } from '@/composables/useI18n'
const { t } = useI18n()
</script>

<style scoped>
.app-footer {
  background: var(--background);
  border-top: 1px solid var(--border);
  padding: var(--spacing-lg) 20px;
  margin-top: auto;
}

.footer-content {
  max-width: var(--page-width);
  margin: 0 auto;
  text-align: center;
}

.footer-links {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}

.footer-links a {
  color: var(--muted);
  text-decoration: none;
  font-size: var(--text-sm);
  transition: all 150ms ease;
}

.footer-links a:hover {
  color: var(--foreground);
}

.footer-copyright {
  font-size: var(--text-xs);
  color: var(--muted);
}
</style>
