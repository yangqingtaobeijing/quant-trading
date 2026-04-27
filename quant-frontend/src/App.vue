<template>
  <div class="terminal-bg flex h-screen overflow-hidden" :style="{ background: 'var(--t-bg-deep)', minWidth: '1280px' }">
    <!-- Sidebar Navigation -->
    <aside
      class="flex flex-col shrink-0 border-r transition-all duration-300 z-20"
      :style="{
        width: sidebarExpanded ? '200px' : '64px',
        background: 'var(--t-bg-sidebar)',
        borderColor: 'var(--t-border)'
      }"
    >
      <!-- Logo -->
      <div class="flex items-center h-14 px-4 border-b" :style="{ borderColor: 'var(--t-border)' }">
        <div class="flex items-center gap-3 overflow-hidden">
          <div class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center glow-green"
               style="background: linear-gradient(135deg, #00D4AA 0%, #0097A7 100%);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M3 18L9 12L13 16L21 6" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M17 6H21V10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <transition name="fade">
            <span v-if="sidebarExpanded" class="font-bold text-sm tracking-wider whitespace-nowrap"
                  style="color: #00D4AA; font-family: 'JetBrains Mono', monospace;">
              QUANT
            </span>
          </transition>
        </div>
      </div>

      <!-- Nav Items -->
      <nav class="flex-1 py-4 flex flex-col gap-1 px-2">
        <NavItem
          v-for="item in navItems"
          :key="item.path"
          :item="item"
          :expanded="sidebarExpanded"
          :active="$route.path === item.path"
        />
      </nav>

      <!-- Toggle button -->
      <button
        class="flex items-center justify-center h-12 border-t transition-colors duration-200 hover:bg-black/5"
        :style="{ borderColor: 'var(--t-border)' }"
        @click="sidebarExpanded = !sidebarExpanded"
        :title="sidebarExpanded ? '收起' : '展开'"
      >
        <svg class="transition-transform duration-300" :class="{ 'rotate-180': sidebarExpanded }"
             width="16" height="16" viewBox="0 0 24 24" fill="none" :style="{ color: 'var(--t-text-muted)' }">
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="shrink-0 flex items-center justify-between px-6 h-14 border-b"
              :style="{ background: 'var(--t-bg-sidebar)', borderColor: 'var(--t-border)' }">
        <!-- Page title -->
        <div class="flex items-center gap-3">
          <h1 class="text-sm font-semibold tracking-wide" :style="{ color: 'var(--t-text-primary)' }">
            {{ currentPageTitle }}
          </h1>
          <div class="h-4 w-px" :style="{ background: 'var(--t-border)' }"></div>
          <span class="text-xs font-mono" :style="{ color: 'var(--t-text-muted)' }">
            {{ lastUpdatedStr }}
          </span>
        </div>

        <!-- Right: status + time + theme toggle -->
        <div class="flex items-center gap-4">
          <!-- Market status badges -->
          <div class="flex items-center gap-2">
            <MarketStatusBadge label="美股" :status="usStatus" />
            <MarketStatusBadge label="A股" :status="cnStatus" />
          </div>
          <div class="h-4 w-px" :style="{ background: 'var(--t-border)' }"></div>

          <!-- Theme toggle -->
          <button
            @click="toggleTheme"
            class="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 hover:bg-black/10"
            :style="{ border: '1px solid var(--t-border)', color: 'var(--t-text-secondary)' }"
            :title="isDark ? '切换白天模式' : '切换黑夜模式'"
          >
            <!-- Moon icon (dark mode) -->
            <svg v-if="isDark" width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <!-- Sun icon (light mode) -->
            <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2"/>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>

          <div class="h-4 w-px" :style="{ background: 'var(--t-border)' }"></div>
          <!-- Clock -->
          <div class="text-right">
            <div class="text-sm font-mono font-semibold" :style="{ color: 'var(--t-text-primary)' }">{{ timeStr }}</div>
            <div class="text-xs font-mono" :style="{ color: 'var(--t-text-muted)' }">{{ dateStr }}</div>
          </div>
        </div>
      </header>

      <!-- Router View -->
      <main class="flex-1 overflow-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMarketStore } from '@/stores/market'
import { useMarketStatus } from '@/composables/useMarketStatus'
import NavItem from '@/components/NavItem.vue'
import MarketStatusBadge from '@/components/MarketStatusBadge.vue'

const route = useRoute()
const marketStore = useMarketStore()
const { timeStr, dateStr, usStatus, cnStatus } = useMarketStatus()

const sidebarExpanded = ref(false)

// ---- Theme ----
const isDark = ref(true)

function applyTheme(dark: boolean) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
  localStorage.setItem('quant-theme', dark ? 'dark' : 'light')
}

function toggleTheme() {
  isDark.value = !isDark.value
  applyTheme(isDark.value)
}

onMounted(() => {
  const saved = localStorage.getItem('quant-theme')
  isDark.value = saved !== 'light'
  applyTheme(isDark.value)
})

const navItems = [
  { path: '/', label: '行情总览', icon: 'dashboard' },
  { path: '/signals', label: '信号面板', icon: 'signal' },
  { path: '/portfolio', label: '持仓管理', icon: 'portfolio' },
  { path: '/settings', label: '系统设置', icon: 'settings' },
]

const pageTitleMap: Record<string, string> = {
  '/': '行情总览',
  '/signals': '信号面板',
  '/portfolio': '持仓管理',
  '/settings': '系统设置',
}
const currentPageTitle = computed(() => pageTitleMap[route.path] || 'QuantTerminal')

const lastUpdatedStr = computed(() => {
  if (!marketStore.lastUpdated) return '等待数据...'
  return `更新于 ${marketStore.lastUpdated.toLocaleTimeString('zh-CN', { hour12: false })}`
})
</script>
