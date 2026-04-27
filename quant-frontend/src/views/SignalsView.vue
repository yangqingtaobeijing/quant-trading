<template>
  <div>
    <!-- Header row -->
    <div class="flex items-center justify-between mb-5">
      <div>
        <h2 class="text-base font-semibold mb-1" style="color: var(--t-text-primary);">信号面板</h2>
        <p class="text-xs" style="color: var(--t-text-muted);">
          共 {{ signalStore.signals.length }} 条信号
          <span v-if="signalStore.lastScanTime" class="ml-2">
            · 最后扫描：{{ formatTime(signalStore.lastScanTime.toISOString()) }}
          </span>
        </p>
      </div>

      <button
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
        style="background: rgba(0,212,170,0.1); color: #00D4AA; border: 1px solid rgba(0,212,170,0.3);"
        :disabled="signalStore.scanning"
        @click="scan"
      >
        <span v-if="signalStore.scanning" class="flex items-center gap-2">
          <span class="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"
                style="border-color: #00D4AA; border-top-color: transparent;"></span>
          扫描中...
        </span>
        <span v-else class="flex items-center gap-2">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          立即扫描
        </span>
      </button>
    </div>

    <!-- Filter tabs -->
    <div class="flex items-center gap-2 mb-4">
      <button v-for="tab in filterTabs" :key="tab.value"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              :style="activeFilter === tab.value
                ? { background: tab.bg, color: tab.color, border: `1px solid ${tab.border}` }
                : { background: 'var(--t-bg-card)', color: 'var(--t-text-muted)', border: '1px solid var(--t-border)' }"
              @click="activeFilter = tab.value">
        {{ tab.label }}
        <span class="font-mono text-xs px-1.5 py-0.5 rounded"
              :style="activeFilter === tab.value
                ? { background: 'rgba(255,255,255,0.15)', color: 'inherit' }
                : { background: 'var(--t-border)', color: 'var(--t-text-secondary)' }">
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- Error -->
    <div v-if="signalStore.error" class="rounded-xl border mb-4 px-5 py-3 flex items-center gap-3"
         style="background: rgba(255,77,77,0.08); border-color: rgba(255,77,77,0.3);">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="color: #FF4D4D; flex-shrink: 0;">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span class="text-sm" style="color: #FF4D4D;">{{ signalStore.error }}</span>
      <button class="ml-auto text-xs px-3 py-1 rounded-lg"
              style="color: #FF4D4D; border: 1px solid rgba(255,77,77,0.3);"
              @click="signalStore.fetchSignals()">重试</button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="signalStore.loading" class="space-y-2">
      <div v-for="i in 5" :key="i" class="skeleton h-14 rounded-lg w-full"></div>
    </div>

    <!-- Signals table -->
    <div v-else class="rounded-xl border overflow-hidden" style="border-color: var(--t-border);">
      <table class="w-full">
        <thead>
          <tr style="background: var(--t-bg-card); border-bottom: 1px solid var(--t-border);">
            <th v-for="col in columns" :key="col.key"
                class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider"
                style="color: var(--t-text-muted);">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredSignals.length === 0">
            <td :colspan="columns.length" class="px-4 py-12 text-center">
              <div class="text-sm" style="color: var(--t-text-muted);">暂无信号</div>
            </td>
          </tr>
          <tr
            v-for="(signal, index) in filteredSignals"
            :key="signal.id"
            class="border-b transition-colors hover:bg-white/3"
            :style="{
              borderColor: '#1A2338',
              background: index % 2 === 0 ? 'var(--t-bg-sidebar)' : 'var(--t-bg-card)',
            }"
          >
            <!-- Time -->
            <td class="px-4 py-3">
              <span class="font-mono text-xs" style="color: var(--t-text-secondary);">{{ formatTime(signal.created_at) }}</span>
            </td>

            <!-- Symbol -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="font-mono font-semibold text-sm" style="color: var(--t-text-primary);">{{ signal.symbol }}</span>
                <span class="text-xs px-1.5 py-0.5 rounded font-mono"
                      style="background: var(--t-border); color: var(--t-text-secondary); font-size: 10px;">
                  {{ signal.symbol.includes('.') ? (signal.symbol.endsWith('.SH') ? 'SH' : 'SZ') : 'US' }}
                </span>
              </div>
              <div class="text-xs mt-0.5" style="color: var(--t-text-muted);">{{ signal.name }}</div>
            </td>

            <!-- Signal type -->
            <td class="px-4 py-3">
              <SignalBadge :type="signal.signal_type" />
            </td>

            <!-- Price -->
            <td class="px-4 py-3">
              <span class="font-mono text-sm font-medium" style="color: var(--t-text-primary);">
                {{ signal.symbol.includes('.') ? '¥' : '$' }}{{ formatNumber(signal.price) }}
              </span>
            </td>

            <!-- Strategy -->
            <td class="px-4 py-3">
              <div class="text-xs font-medium" style="color: var(--t-text-secondary);">{{ signal.strategy }}</div>
              <div v-if="signal.description" class="text-xs mt-0.5" style="color: var(--t-text-muted);">
                {{ signal.description }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSignalStore } from '@/stores/signal'
import type { SignalType } from '@/api'
import { formatNumber, formatTime } from '@/utils/format'
import SignalBadge from '@/components/SignalBadge.vue'

const signalStore = useSignalStore()
type FilterType = SignalType | 'ALL'
const activeFilter = ref<FilterType>('ALL')

const columns = [
  { key: 'time', label: '时间' },
  { key: 'symbol', label: '股票' },
  { key: 'type', label: '信号类型' },
  { key: 'price', label: '触发价格' },
  { key: 'strategy', label: '策略说明' },
]

const filterTabs = computed(() => [
  { value: 'ALL' as FilterType, label: '全部', count: signalStore.signals.length, color: 'var(--t-text-primary)', bg: 'var(--t-border)', border: 'var(--t-border-light)' },
  { value: 'BUY' as FilterType, label: '买入', count: signalStore.signalsByType.BUY.length, color: '#00D4AA', bg: 'rgba(0,212,170,0.1)', border: 'rgba(0,212,170,0.3)' },
  { value: 'SELL' as FilterType, label: '卖出', count: signalStore.signalsByType.SELL.length, color: '#FF4D4D', bg: 'rgba(255,77,77,0.1)', border: 'rgba(255,77,77,0.3)' },
  { value: 'OVERSOLD' as FilterType, label: '超卖', count: signalStore.signalsByType.OVERSOLD.length, color: '#F59E0B', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.3)' },
  { value: 'OVERBOUGHT' as FilterType, label: '超买', count: signalStore.signalsByType.OVERBOUGHT.length, color: '#FCD34D', bg: 'rgba(252,211,77,0.1)', border: 'rgba(252,211,77,0.3)' },
])

const filteredSignals = computed(() =>
  activeFilter.value === 'ALL'
    ? signalStore.signals
    : signalStore.signalsByType[activeFilter.value as SignalType]
)

async function scan() {
  await signalStore.scan()
}

onMounted(() => signalStore.fetchSignals())
</script>
