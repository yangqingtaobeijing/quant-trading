import { createRouter, createWebHashHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: '行情总览' }
    },
    {
      path: '/signals',
      name: 'signals',
      component: () => import('@/views/SignalsView.vue'),
      meta: { title: '信号面板' }
    },
    {
      path: '/portfolio',
      name: 'portfolio',
      component: () => import('@/views/PortfolioView.vue'),
      meta: { title: '持仓管理' }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      meta: { title: '系统设置' }
    },
  ]
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'Quant'} · QuantTerminal`
})

export default router
