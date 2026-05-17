import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import AdminUsers from '@/views/admin/AdminUsers.vue'
import AdminPlans from '@/views/admin/AdminPlans.vue'
import AdminSubscriptions from '@/views/admin/AdminSubscriptions.vue'
import AdminPoints from '@/views/admin/AdminPoints.vue'

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

  // ====== V3.0 五大核心板块 ======
  
  // AI品牌智库
  {
    path: '/brand-hub',
    name: 'BrandHub',
    component: () => import('@/views/BrandHub.vue'),
    meta: { title: 'AI品牌智库', requiresAuth: true },
  },
  
  // AI可见度体检
  {
    path: '/ai-health-check',
    name: 'AIHealthCheck',
    component: () => import('@/views/AIHealthCheck.vue'),
    meta: { title: 'AI可见度体检', requiresAuth: true },
  },
  
  // GEO效果检测
  {
    path: '/geo-verification',
    name: 'GEOVerification',
    component: () => import('@/views/GEOVerification.vue'),
    meta: { title: 'GEO效果检测', requiresAuth: true },
  },
  
  // 报告防篡改验真（公开页面）
  {
    path: '/verify',
    name: 'Verify',
    component: () => import('@/views/Verify.vue'),
    meta: { title: '报告验真', guest: true },
  },
  {
    path: '/verify/:code',
    name: 'VerifyWithCode',
    component: () => import('@/views/Verify.vue'),
    meta: { title: '报告验真', guest: true },
  },
  
  // 个人中心
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true },
  },

  // ====== 保留的旧页面（兼容） ======
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

  // ====== 管理员后台 ======
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/AdminLogin.vue'),
    meta: { title: '管理员登录', guest: true },
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { title: '管理后台', requiresAdmin: true },
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { title: '用户管理', requiresAdmin: true },
  },
  {
    path: '/admin/plans',
    name: 'AdminPlans',
    component: AdminPlans,
    meta: { title: '套餐配置', requiresAdmin: true },
  },
  {
    path: '/admin/subscriptions',
    name: 'AdminSubscriptions',
    component: AdminSubscriptions,
    meta: { title: '订阅记录', requiresAdmin: true },
  },
  {
    path: '/admin/points',
    name: 'AdminPoints',
    component: AdminPoints,
    meta: { title: '积分流水', requiresAdmin: true },
  },

  // ====== 公开页面 ======
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: { title: '关于我们', guest: true },
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('@/views/Pricing.vue'),
    meta: { title: '定价', guest: true },
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('@/views/Terms.vue'),
    meta: { title: '服务条款', guest: true },
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('@/views/Privacy.vue'),
    meta: { title: '隐私政策', guest: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'PrismaMate'} - PrismaMate 棱镜`

  const userStore = useUserStore()

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin) {
    const adminToken = localStorage.getItem('admin_token')
    if (!adminToken) {
      next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
      return
    }
  }

  // 需要登录的页面
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    // 如果当前已经在登录或注册页，不重复跳转
    if (to.name === 'Login' || to.name === 'Register') {
      next()
      return
    }
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 已登录用户访问仅限游客的页面（登录页、注册页）
  const guestOnlyRoutes = ['Login', 'Register', 'AdminLogin']
  if (to.meta.guest && userStore.isLoggedIn && guestOnlyRoutes.includes(to.name as string)) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
