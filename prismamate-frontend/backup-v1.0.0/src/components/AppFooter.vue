<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-links">
        <router-link to="/home">关于我们</router-link>
        <router-link to="/pricing">订阅价格</router-link>
        <router-link to="/terms">服务条款</router-link>
        <router-link to="/privacy">隐私政策</router-link>
      </div>
      <div class="footer-copyright">
        &copy; 2026 PrismaMate. All rights reserved.
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// 全局页脚组件
</script>

<style scoped>
.app-footer {
  background: #000000;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
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
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
  font-size: var(--text-sm);
  transition: all 150ms ease;
}

.footer-links a:hover {
  color: #FFFFFF;
}

.footer-copyright {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.35);
}
</style>