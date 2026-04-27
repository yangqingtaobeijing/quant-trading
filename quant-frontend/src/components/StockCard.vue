<template>
  <div
    class="relative rounded-xl border cursor-pointer transition-all duration-200 overflow-hidden group"
    :style="{
      background: 'var(--t-bg-card)',
      borderColor: signalBorderColor || 'var(--t-border)',
    }"
    :class="[hasSignal ? 'hover:shadow-lg' : '']"
    style="box-shadow: 0 1px 3px rgba(0,0,0,0.4);"
    @click="$emit('click', quote)"
  >
    <!-- Signal badge top-right -->
    <div v-if="quote.signal" class="absolute top-2 right-2 z-10">
      <span class="badge" :class="signalBadgeClass">{{ signalLabel }}</span>
    </div>

    <!-- Glow line on left border if signal -->
    <div v-if="quote.signal" class="absolute left-0 top-0 bottom-0 w-0.5 rounded-l-xl"
         :style="{ background: signalBorderColor }"></div>

    <div class="p-4">
      <!-- Header row -->
      <div class="flex items-start justify-between mb-3">
        <div class="min-w-0 pr-8">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="text-sm font-mono font-bold" style="color: var(--t-text-primary);">{{ quote.symbol }}</span>
            <span class="text-xs px-1.5 py-0.5 rounded font-mono"
                  :style="{ background: 'var(--t-border)', color: quote.market === 'CN' ? '#F59E0B' : '#3B82F6', fontSize: '10px' }">
              {{ quote.market }}
            </span>
          </div>
          <div class="text-xs truncate" style="color: var(--t-text-secondary);">{{ quote.name }}</div>
        </div>
      </div>

      <!-- Price row -->
      <div class="flex items-end justify-between mb-3">
        <div class="font-mono font-bold text-xl" style="color: var(--t-text-primary);">
          {{ quote.market === 'CN' ? '¥' : '$' }}{{ formatNumber(quote.price) }}
        </div>
        <div class="text-right">
          <div class="font-mono text-sm font-semibold" :class="changeClass((quote.change_pct ?? quote.changePercent ?? 0) * 100)">
            {{ formatChangePercent((quote.change_pct ?? quote.changePercent ?? 0) * 100) }}
          </div>
          <div class="font-mono text-xs" :class="changeClass(quote.change ?? 0)">
            {{ formatChange(quote.change ?? 0) }}
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="h-px mb-3" style="background: var(--t-border);"></div>

      <!-- Indicators grid -->
      <div class="grid grid-cols-3 gap-2">
        <div>
          <div class="text-xs mb-0.5" style="color: var(--t-text-muted);">EMA20</div>
          <div class="font-mono text-xs font-medium" style="color: #3B82F6;">
            {{ formatNumber(quote.ema20 ?? 0) }}
          </div>
        </div>
        <div>
          <div class="text-xs mb-0.5" style="color: var(--t-text-muted);">EMA60</div>
          <div class="font-mono text-xs font-medium" style="color: #F59E0B;">
            {{ formatNumber(quote.ema60 ?? 0) }}
          </div>
        </div>
        <div>
          <div class="text-xs mb-0.5" style="color: var(--t-text-muted);">RSI14</div>
          <div class="font-mono text-xs font-medium" :class="rsiClass">
            {{ (quote.rsi14 ?? 0).toFixed(1) }}
          </div>
        </div>
      </div>

      <!-- Volume -->
      <div class="mt-2 flex items-center gap-1">
        <span class="text-xs" style="color: var(--t-text-muted);">成交量</span>
        <span class="font-mono text-xs" style="color: var(--t-text-secondary);">{{ formatVolume(quote.volume ?? 0) }}</span>
      </div>
    </div>

    <!-- Hover overlay -->
    <div class="absolute inset-0 rounded-xl pointer-events-none transition-opacity duration-200 opacity-0 group-hover:opacity-100"
         style="background: rgba(255,255,255,0.02);"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { QuoteData } from '@/api'
import { formatNumber, formatChangePercent, formatChange, formatVolume, changeClass } from '@/utils/format'

const props = defineProps<{ quote: QuoteData }>()
defineEmits<{ (e: 'click', q: QuoteData): void }>()

const hasSignal = computed(() => !!props.quote.signal)

const signalBorderColor = computed(() => {
  switch (props.quote.signal) {
    case 'BUY':      return '#00D4AA'
    case 'SELL':     return '#FF4D4D'
    case 'OVERSOLD': return '#F59E0B'
    case 'OVERBOUGHT': return '#FCD34D'
    default:         return ''
  }
})

const signalBadgeClass = computed(() => {
  switch (props.quote.signal) {
    case 'BUY':      return 'badge-buy'
    case 'SELL':     return 'badge-sell'
    case 'OVERSOLD': return 'badge-oversold'
    case 'OVERBOUGHT': return 'badge-overbought'
    default:         return ''
  }
})

const signalLabel = computed(() => {
  switch (props.quote.signal) {
    case 'BUY':      return '买入'
    case 'SELL':     return '卖出'
    case 'OVERSOLD': return '超卖'
    case 'OVERBOUGHT': return '超买'
    default:         return ''
  }
})

const rsiClass = computed(() => {
  const r = props.quote.rsi14 ?? 0
  if (r >= 70) return 'text-yellow-300'
  if (r <= 30) return 'text-orange-400'
  return 'text-[var(--t-text-secondary)]'
})
</script>
