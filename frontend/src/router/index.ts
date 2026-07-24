import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/api/request'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { title: '登录', noAuth: true },
  },
  {
    path: '/input',
    name: 'input',
    component: () => import('@/views/InputPage.vue'),
    meta: { title: '资料审查' },
  },
  {
    path: '/diagnosis/:id?',
    name: 'diagnosis',
    component: () => import('@/views/DiagnosisPage.vue'),
    meta: { title: '能力诊断' },
  },
  {
    path: '/resources/:assessmentId',
    name: 'resources',
    component: () => import('@/views/ResourcesPage.vue'),
    meta: { title: '资源包' },
  },
  {
    path: '/resource/:id',
    name: 'resourceDetail',
    component: () => import('@/views/ResourceDetailPage.vue'),
    meta: { title: '资源详情' },
  },
  {
    path: '/path',
    name: 'path',
    component: () => import('@/views/PathPage.vue'),
    meta: { title: '学习路径' },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: { title: '个人中心' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫
router.beforeEach((to, _from, next) => {
  // 修改页面标题
  document.title = (to.meta.title as string) || '职学导航'

  // 无需登录的页面直接放行
  if (to.meta.noAuth) {
    next()
    return
  }

  // 检查 token：无 token → 重定向 /login
  const token = getToken()
  if (!token) {
    next('/login')
    return
  }

  next()
})

export default router
