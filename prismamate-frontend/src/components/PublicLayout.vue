<template>
  <div class="public-layout">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="navbar-inner">
        <!-- Logo -->
        <router-link to="/home" class="logo-group">
          <img src="@/assets/logo-dark.svg" alt="PrismaMate 棱镜报告" class="logo-img" />
        </router-link>

        <!-- 导航链接 -->
        <div class="nav-links">
          <a
            v-for="link in mainLinks"
            :key="link.path"
            :class="['nav-link', { active: isActive(link) }]"
            @click="$router.push(link.path)"
          >
            {{ link.label }}
          </a>

          <!-- 功能按钮区域 -->
          <div class="nav-actions">
            <!-- 语言切换 -->
            <button class="action-btn" @click="toggleLocale" :title="t('nav.langSwitch')">
              {{ isEnglish ? '中文' : 'EN' }}
            </button>

            <!-- 未登录 -->
            <template v-if="!userStore.isLoggedIn">
              <a class="nav-link nav-link-highlight" @click="authDialogRef?.open('login')">{{ t('nav.login') }}</a>
              <span class="nav-divider">|</span>
              <a class="nav-link nav-link-highlight" @click="authDialogRef?.open('register')">{{ t('nav.register') }}</a>
            </template>

            <!-- 已登录 -->
            <template v-else>
              <div class="user-menu" ref="userMenuRef">
                <div class="user-avatar" @click="showUserDropdown = !showUserDropdown">
                  <el-icon :size="16"><UserFilled /></el-icon>
                </div>
                <div v-show="showUserDropdown" class="user-dropdown">
                  <a @click="$router.push('/profile'); showUserDropdown = false">{{ t('nav.profile') }}</a>
                  <a @click="handleLogout(); showUserDropdown = false">{{ t('nav.logout') }}</a>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- 页面内容 -->
    <div class="page-content">
      <slot />
    </div>

    <!-- 底部信息 -->
    <AppFooter />

    <!-- 统一登录/注册对话框 -->
    <AuthDialog ref="authDialogRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import AppFooter from '@/components/AppFooter.vue'
import AuthDialog from '@/components/AuthDialog.vue'
import { useI18n } from '@/composables/useI18n'

const authDialogRef = ref<InstanceType<typeof AuthDialog>>()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const showUserDropdown = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

const { t, locale, toggleLocale } = useI18n()

const isEnglish = computed(() => locale.value === 'en')

// 全局监听登录弹窗状态
watch(() => userStore.showAuthDialog, (show) => {
  if (show) {
    authDialogRef.value?.open(userStore.authDialogTab)
    userStore.showAuthDialog = false
  }
})

const mainLinks = computed(() => [
  { label: t('nav.home'), path: '/home', activeCheck: (p: string) => p === '/home' || p === '/' },
  { label: t('nav.about'), path: '/about' },
  { label: t('nav.pricing'), path: '/pricing' },
])

function isActive(link: { label: string; path: string; activeCheck?: (path: string) => boolean }) {
  if (link.activeCheck) return link.activeCheck(route.path)
  return route.path === link.path || route.path.startsWith(link.path)
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/home')
}

function handleClickOutside(event: MouseEvent) {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    showUserDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.public-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--background);
}

/* === 导航栏 === */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  background: var(--background);
  border-bottom: 1px solid var(--border);
}

.navbar-inner {
  max-width: var(--page-width);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
}

/* Logo */
.logo-group {
  display: flex;
  align-items: center;
  cursor: pointer;
  text-decoration: none;
  transition: transform 0.3s ease;
}

.logo-group:hover {
  transform: scale(1.05);
}

.logo-group:active {
  transform: scale(0.98);
}

.logo-img {
  height: 36px;
  width: auto;
}

/* 导航链接 */
.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  color: var(--muted);
  font-size: 14px;
  font-weight: 400;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
  position: relative;
}

.nav-link:hover,
.nav-link.active {
  color: var(--foreground);
}

.nav-link-highlight {
  background: var(--hover-bg);
  padding: 6px 16px;
  border-radius: var(--radius-md);
  color: var(--foreground);
}

.nav-link-highlight:hover {
  background: var(--border);
}

.nav-divider {
  color: var(--border);
  font-size: 14px;
  user-select: none;
}

/* 功能按钮区域 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--muted);
  font-size: 13px;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: var(--hover-bg);
  border-color: var(--muted);
  color: var(--foreground);
}

.theme-btn {
  padding: 6px 10px;
}

.icon-sun,
.icon-moon {
  font-size: 16px;
  line-height: 1;
}

/* 用户菜单 */
.user-menu {
  position: relative;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--hover-bg);
  color: var(--foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.user-avatar:hover {
  background: var(--border);
}

.user-dropdown {
  position: absolute;
  top: 44px;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 6px;
  min-width: 140px;
  box-shadow: 0 8px 32px var(--overlay);
}

.user-dropdown a {
  display: block;
  padding: 8px 12px;
  color: var(--muted);
  font-size: 13px;
  text-decoration: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
}

.user-dropdown a:hover {
  background: var(--hover-bg);
  color: var(--foreground);
}

.page-content {
  flex: 1;
  padding-top: 64px;
}

@media (max-width: 768px) {
  .nav-links {
    gap: 16px;
  }
  .nav-link {
    font-size: 13px;
  }
  .navbar-inner {
    padding: 0 var(--spacing-md);
  }
}
</style>
