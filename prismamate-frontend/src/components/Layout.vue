<template>
  <div class="dashboard-layout">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="navbar-inner">
        <!-- Logo -->
        <router-link to="/home" class="logo-group">
          <img src="@/assets/logo-dark.svg" alt="PrismaMate 棱镜报告" class="logo-img" />
        </router-link>

        <!-- 导航链接 -->
        <div class="nav-links">
          <!-- 用户端：五大核心板块导航 -->
          <template v-if="!isAdmin">
            <a
              v-for="item in userMenu"
              :key="item.path"
              :class="['nav-link', { active: isMenuActive(item.path) }]"
              @click="navigate(item.path)"
            >
              {{ item.label }}
            </a>
          </template>
          <!-- 管理员端：顶部导航 -->
          <template v-else>
            <a
              v-for="item in adminMenu"
              :key="item.path"
              :class="['nav-link', { active: isMenuActive(item.path) }]"
              @click="navigate(item.path)"
            >
              <component v-if="item.icon" :is="item.icon" class="nav-icon" />
              {{ item.label }}
            </a>
          </template>

          <!-- 功能按钮区域 -->
          <div class="nav-actions">
            <button v-if="isAdmin" class="action-btn" @click="toggleLang" :title="isEnglish ? '切换中文' : 'Switch to English'">
              {{ isEnglish ? '中文' : 'EN' }}
            </button>

            <!-- 用户菜单 -->
            <div class="user-menu" ref="userMenuRef">
              <div class="user-avatar" @click="showUserDropdown = !showUserDropdown">
                {{ userInitials }}
              </div>
              <div v-show="showUserDropdown" class="user-dropdown">
                <a v-if="!isAdmin" @click="$router.push('/profile'); showUserDropdown = false">个人中心</a>
                <a v-if="!isAdmin && isAdminUser" @click="goToAdmin(); showUserDropdown = false">进入管理后台</a>
                <a v-if="isAdmin" @click="backToUser(); showUserDropdown = false">返回用户端</a>
                <a @click="handleLogout(); showUserDropdown = false">退出登录</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 中间区域 -->
    <div class="dashboard-main">
      <main class="content-area">
        <div class="content-card">
          <slot />
        </div>
      </main>
    </div>

    <!-- 底部信息 -->
    <AppFooter />

    <!-- 统一登录/注册对话框 -->
    <AuthDialog ref="authDialogRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onBeforeUnmount, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import AppFooter from '@/components/AppFooter.vue'
import AuthDialog from '@/components/AuthDialog.vue'

import {
  Grid,
  FirstAidKit,
  DataLine,
  Document,
  User,
  SetUp,
  Collection,
  Wallet,
  Coin
} from '@element-plus/icons-vue'

const authDialogRef = ref<InstanceType<typeof AuthDialog>>()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const showUserDropdown = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const isEnglish = ref(false)

function toggleLang() {
  isEnglish.value = !isEnglish.value
}

watch(() => userStore.showAuthDialog, (show) => {
  if (show) {
    authDialogRef.value?.open(userStore.authDialogTab)
    userStore.showAuthDialog = false
  }
})

const userInitials = computed(() => {
  const name = userStore.user?.username || userStore.user?.email || '用户'
  return name.slice(0, 1).toUpperCase()
})

const isAdminUser = computed(() => {
  return userStore.user?.username === 'admin'
})

function goToAdmin() {
  userStore.logout()
  setTimeout(() => {
    window.location.href = '/admin/login'
  }, 150)
}

function backToUser() {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_info')
  isAdminRef.value = false
  window.location.href = '/brand-hub'
}

const isAdminRef = ref(!!localStorage.getItem('admin_token'))
const isAdmin = computed(() => isAdminRef.value)

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === 'admin_token') {
      isAdminRef.value = !!localStorage.getItem('admin_token')
    }
  })
}

watch(() => route.path, () => {
  isAdminRef.value = !!localStorage.getItem('admin_token')
}, { immediate: true })

interface MenuItem {
  label: string
  path: string
  icon?: any
}

const userMenu: MenuItem[] = [
  { label: 'AI品牌智库', path: '/brand-hub', icon: markRaw(Collection) },
  { label: 'AI可见度体检', path: '/ai-health-check', icon: markRaw(FirstAidKit) },
  { label: 'GEO效果检测', path: '/geo-verification', icon: markRaw(DataLine) },
  { label: '报告防篡改验真', path: '/verify', icon: markRaw(Document) },
  { label: '个人中心', path: '/profile', icon: markRaw(User) },
]

const adminMenu: MenuItem[] = [
  { label: '仪表盘', path: '/admin/dashboard', icon: markRaw(Grid) },
  { label: '用户管理', path: '/admin/users', icon: markRaw(User) },
  { label: '套餐配置', path: '/admin/plans', icon: markRaw(SetUp) },
  { label: '订阅记录', path: '/admin/subscriptions', icon: markRaw(Wallet) },
  { label: '积分流水', path: '/admin/points', icon: markRaw(Coin) },
]

function isMenuActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}

function navigate(path: string) {
  router.push(path)
}

function handleLogout() {
  if (localStorage.getItem('admin_token')) {
    localStorage.removeItem('admin_token')
    ElMessage.success('已退出管理员登录')
    router.push('/admin/login')
    return
  }
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
  isAdminRef.value = !!localStorage.getItem('admin_token')
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ========== 整体布局 ========== */
.dashboard-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0F0F0F;
}

/* ========== 顶部导航 ========== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
  background: #0F0F0F;
  border-bottom: 1px solid #2D2D2D;
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

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

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  color: #9CA3AF;
  font-size: 14px;
  font-weight: 400;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
}

.nav-link:hover,
.nav-link.active {
  color: #FFFFFF;
}

.nav-icon {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  vertical-align: middle;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 6px;
  color: #F3F4F6;
  font-size: 13px;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: #2D2D2D;
  border-color: #3B82F6;
  color: #FFFFFF;
}

.user-menu {
  position: relative;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #2D2D2D;
  color: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.user-avatar:hover {
  background: #3D3D3D;
}

.user-dropdown {
  position: absolute;
  top: 44px;
  right: 0;
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 8px;
  padding: 6px;
  min-width: 140px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.user-dropdown a {
  display: block;
  padding: 8px 12px;
  color: #F3F4F6;
  font-size: 13px;
  text-decoration: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.user-dropdown a:hover {
  background: #2D2D2D;
  color: #FFFFFF;
}

/* ========== 中间区域 ========== */
.dashboard-main {
  flex: 1;
  display: flex;
  padding-top: 64px;
  min-height: calc(100vh - 64px);
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow: auto;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.content-card {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  padding: 24px 28px;
  min-height: calc(100vh - 64px - 48px - 80px);
}

/* ========== Element Plus 深色适配 ========== */
::deep(.el-card) {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
  color: #F3F4F6;
}

::deep(.el-card__header) {
  border-bottom: 1px solid #2D2D2D;
  color: #E5E5E5;
  font-weight: 500;
  font-size: 16px;
  padding: 16px 20px;
}

::deep(.el-card__body) {
  padding: 20px;
  color: #F3F4F6;
}

::deep(.el-table) {
  background: transparent;
  color: #F3F4F6;
}

::deep(.el-table__header-wrapper th) {
  background: transparent !important;
  color: #9CA3AF !important;
  font-weight: 500;
  font-size: 14px;
  border-bottom: 1px solid #2D2D2D !important;
}

::deep(.el-table tr) {
  background: transparent;
}

::deep(.el-table td) {
  background: transparent;
  color: #F3F4F6;
  border-bottom: 1px solid #2D2D2D;
  padding: 12px 16px;
}

::deep(.el-table__body tr:hover > td) {
  background: #272727 !important;
}

::deep(.el-table__empty-text) {
  color: #9CA3AF;
}

::deep(.el-form-item__label) {
  color: #D1D5DB;
  font-size: 14px;
  width: 120px;
}

::deep(.el-input__wrapper) {
  background: #272727;
  border: 1px solid #2D2D2D;
  border-radius: 8px;
  box-shadow: none;
  height: 42px;
}

::deep(.el-input__inner) {
  color: #F3F4F6;
  height: 42px;
}

::deep(.el-input__wrapper:hover) {
  border-color: #3B82F6;
}

::deep(.el-input__wrapper.is-focus) {
  border-color: #3B82F6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

::deep(.el-select .el-input__wrapper) {
  background: #272727;
  height: 42px;
}

::deep(.el-select__wrapper) {
  background: #272727 !important;
  border-color: #2D2D2D !important;
  min-height: 42px;
  border-radius: 8px;
}

::deep(.el-dialog) {
  background: #1A1A1A;
  border: 1px solid #2D2D2D;
  border-radius: 12px;
}

::deep(.el-dialog__header) {
  border-bottom: 1px solid #2D2D2D;
  margin-right: 0;
  padding: 16px 20px;
}

::deep(.el-dialog__title) {
  color: #FFFFFF;
  font-weight: 600;
  font-size: 16px;
}

::deep(.el-dialog__body) {
  color: #F3F4F6;
  padding: 20px;
}

::deep(.el-dialog__footer) {
  border-top: 1px solid #2D2D2D;
  padding: 12px 20px;
}

::deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-hover-color: #FFFFFF;
  --el-pagination-button-color: #9CA3AF;
  --el-pagination-button-disabled-color: rgba(255, 255, 255, 0.1);
}

::deep(.el-pagination .el-pager li) {
  background: transparent;
  color: #9CA3AF;
  border-radius: 6px;
}

::deep(.el-pagination .el-pager li.is-active) {
  color: #FFFFFF;
  background: #3B82F6;
}

::deep(.el-tag) {
  border: none;
  border-radius: 6px;
  padding: 0 10px;
  height: 26px;
  line-height: 26px;
  font-size: 13px;
}

::deep(.el-tag--info) {
  background: #333333;
  color: #9CA3AF;
}

::deep(.el-tag--success) {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
}

::deep(.el-tag--warning) {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}

::deep(.el-tag--danger) {
  background: rgba(220, 38, 38, 0.15);
  color: #EF4444;
}

::deep(.el-tag--primary) {
  background: rgba(59, 130, 246, 0.15);
  color: #3B82F6;
}

::deep(.el-button) {
  border-radius: 8px;
  font-weight: 400;
}

::deep(.el-button--default) {
  background: #333333;
  border-color: #2D2D2D;
  color: #D1D5DB;
  height: 42px;
  padding: 0 20px;
}

::deep(.el-button--default:hover) {
  background: #3D3D3D;
  border-color: #3B82F6;
  color: #FFFFFF;
}

::deep(.el-button--primary) {
  background: #3B82F6;
  border-color: #3B82F6;
  color: #FFFFFF;
  height: 42px;
  padding: 0 20px;
}

::deep(.el-button--primary:hover) {
  background: #2563EB;
  border-color: #2563EB;
  color: #FFFFFF;
}

::deep(.el-button--success) {
  background: #10B981;
  border-color: #10B981;
  color: #FFFFFF;
}

::deep(.el-button--warning) {
  background: #F59E0B;
  border-color: #F59E0B;
  color: #FFFFFF;
}

::deep(.el-button--danger) {
  background: #EF4444;
  border-color: #EF4444;
  color: #FFFFFF;
}

::deep(.el-button--small) {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
  border-radius: 6px;
}

::deep(.el-button--text) {
  background: transparent;
  border: none;
  color: #3B82F6;
  height: auto;
  padding: 0;
}

::deep(.el-button--text:hover) {
  color: #60A5FA;
}

::deep(.el-divider) {
  border-color: #2D2D2D;
}

::deep(.el-divider__text) {
  background: transparent;
  color: #9CA3AF;
}

::deep(.el-descriptions__body) {
  background: transparent;
}

::deep(.el-descriptions__label) {
  background: #272727 !important;
  color: #D1D5DB !important;
  font-size: 14px;
  width: 120px;
}

::deep(.el-descriptions__content) {
  background: transparent !important;
  color: #F3F4F6;
  font-size: 14px;
}

::deep(.el-alert) {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
}

::deep(.el-alert--info .el-alert__description) {
  color: #9CA3AF;
}

::deep(.el-progress-bar__outer) {
  background: #2D2D2D;
}

::deep(.el-input-number__decrease),
::deep(.el-input-number__increase) {
  background: #333333;
  border-color: #2D2D2D;
  color: #9CA3AF;
}

::deep(.el-textarea__inner) {
  background: #272727;
  border-color: #2D2D2D;
  color: #F3F4F6;
  border-radius: 8px;
}

::deep(.el-textarea__inner:focus) {
  border-color: #3B82F6;
}

::deep(.el-form-item) {
  margin-bottom: 20px;
}

::deep(.el-input-number) {
  width: 100%;
}

/* ========== 响应式 ========== */
@media (max-width: 900px) {
  .content-area {
    padding: 20px;
  }
  .content-card {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .nav-links {
    gap: 16px;
  }
  .nav-link {
    font-size: 13px;
  }
  .navbar-inner {
    padding: 0 16px;
  }
}
</style>
