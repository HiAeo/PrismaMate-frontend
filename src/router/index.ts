import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' },
  },
  // Phase 1: 极简检测页面，无需登录
  {
    path: '/detect',
    name: 'SimpleDetection',
    component: () => import('@/views/SimpleDetection.vue'),
    meta: { title: '品牌检测', guest: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', guest: true },
  },
  {
    path: '/verify',
    name: 'Verify',
    component: () => import('@/views/Verify.vue'),
    meta: { title: '报告验证', guest: true },
  },
  {
    path: '/verify/:code',
    name: 'VerifyWithCode',
    component: () => import('@/views/Verify.vue'),
    meta: { title: '报告验证', guest: true },
  },
  {
    path: '/detection',
    name: 'Detection',
    component: () => import('@/views/Detection.vue'),
    meta: { title: '检测任务', requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: { title: '报告列表', requiresAuth: true },
  },
  {
    path: '/reports/:id',
    name: 'ReportDetail',
    component: () => import('@/views/ReportDetail.vue'),
    meta: { title: '报告详情', requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '用户中心', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'PrismaMate'} - PrismaMate 棱镜`

  const userStore = useUserStore()

  // 需要登录的页面
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 已登录用户访问游客页面（如登录页）
  if (to.meta.guest && userStore.isLoggedIn) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
