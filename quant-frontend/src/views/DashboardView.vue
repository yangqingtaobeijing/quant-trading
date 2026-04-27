<template>
  <div>
    <!-- Market Sentiment Bar -->
    <div class="rounded-xl border mb-5 px-5 py-3 flex items-center gap-6 flex-wrap"
         style="background: var(--t-bg-card); border-color: var(--t-border);">
      <!-- VIX -->
      <div class="flex items-center gap-3">
        <div>
          <div class="text-xs mb-0.5" style="color: var(--t-text-muted);">VIX 恐慌指数</div>
          <div class="flex items-center gap-2">
            <span class="font-mono font-bold text-base" :class="vixClass">
              {{ formatNumber(sentiment?.vix ?? 0) }}
            </span>
            <span class="font-mono text-xs" :class="changeClass(-(sentiment?.vixChange ?? 0))">
              {{ formatChangePercent(-(sentiment?.vixChange ?? 0)) }}
            </span>
          </div>
        </div>
        <div class="h-8 w-px" style="background: var(--t-border);"></div>
      </div>

      <!-- Indices -->
      <div v-for="idx in sentiment?.indices ?? mockIndices" :key="idx.symbol"
           class="flex items-center gap-3">
        <div>
          <div class="text-xs mb-0.5" style="color: var(--t-text-muted);">{{ idx.name }}</div>
          <div class="flex items-center gap-2">
            <span class="font-mono text-sm font-semibold" style="color: var(--t-text-primary);">
              {{ formatNumber(idx.price) }}
            </span>
            <span class="font-mono text-xs" :class="changeClass(idx.changePercent)">
              {{ formatChangePercent(idx.changePercent) }}
            </span>
          </div>
        </div>
        <div class="h-8 w-px" style="background: var(--t-border);"></div>
      </div>

      <div class="flex-1"></div>

      <!-- Add symbol input -->
      <form class="flex items-center gap-2" @submit.prevent="addSymbol">
        <input
          v-model="newSymbol"
          type="text"
          placeholder="添加自选股 (e.g. AAPL)"
          class="px-3 py-1.5 rounded-lg text-sm font-mono border outline-none transition-colors"
          style="background: var(--t-bg-deep); border-color: var(--t-border); color: var(--t-text-primary); width: 200px;"
          :style="{ borderColor: newSymbol ? '#3B82F6' : 'var(--t-border)' }"
        />
        <button
          type="submit"
          :disabled="!newSymbol.trim() || adding"
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50"
          style="background: rgba(59,130,246,0.15); color: #3B82F6; border: 1px solid rgba(59,130,246,0.3);"
        >
          <span v-if="adding" class="flex items-center gap-1.5">
            <span class="w-3.5 h-3.5 border border-t-transparent rounded-full animate-spin" style="border-color: #3B82F6; border-top-color: transparent;"></span>
            添加中
          </span>
          <span v-else>+ 添加</span>
        </button>
      </form>
    </div>

    <!-- Signal summary row (only shown when there are signals) -->
    <div v-if="signalCount > 0" class="rounded-xl border mb-5 px-5 py-3"
         style="background: rgba(0,212,170,0.05); border-color: rgba(0,212,170,0.2);">
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 rounded-full animate-pulse" style="background: #00D4AA;"></div>
        <span class="text-sm font-medium" style="color: #00D4AA;">
          {{ signalCount }} 个信号触发
        </span>
        <span class="text-xs" style="color: var(--t-text-muted);">
          {{ signalSummary }}
        </span>
        <RouterLink to="/signals" class="ml-auto text-xs px-3 py-1 rounded-lg transition-colors hover:bg-white/10"
                    style="color: #3B82F6; border: 1px solid rgba(59,130,246,0.3);">
          查看全部信号 →
        </RouterLink>
      </div>
    </div>

    <!-- Stock Cards Grid -->
    <!-- Error Banner -->
    <div v-if="marketStore.error" class="rounded-xl border mb-5 px-5 py-3 flex items-center gap-3"
         style="background: rgba(255,77,77,0.08); border-color: rgba(255,77,77,0.3);">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="color: #FF4D4D; flex-shrink: 0;">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span class="text-sm" style="color: #FF4D4D;">{{ marketStore.error }}</span>
      <button class="ml-auto text-xs px-3 py-1 rounded-lg transition-colors"
              style="color: #FF4D4D; border: 1px solid rgba(255,77,77,0.3);"
              @click="marketStore.init()">重试</button>
    </div>

    <div v-if="marketStore.loading" class="grid gap-4" style="grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));">
      <SkeletonCard v-for="i in 8" :key="i" />
    </div>

    <div v-else-if="quoteList.length === 0 && !marketStore.error" class="flex flex-col items-center justify-center py-20">
      <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
           style="background: var(--t-bg-card); border: 1px solid var(--t-border);">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14M5 12h14" stroke="var(--t-border)" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="text-sm font-medium mb-1" style="color: var(--t-text-muted);">暂无自选股</div>
      <div class="text-xs" style="color: var(--t-border-light);">在上方输入框添加股票代码</div>
    </div>

    <div v-else class="grid gap-4" style="grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));">
      <StockCard
        v-for="quote in quoteList"
        :key="quote.symbol"
        :quote="quote"
        @click="openKline"
      />
    </div>

    <!-- K-line Modal -->
    <KlineModal
      :visible="klineVisible"
      :quote="selectedQuote"
      @close="klineVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import type { QuoteData } from '@/api'
import { formatNumber, formatChangePercent, changeClass } from '@/utils/format'
import StockCard from '@/components/StockCard.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import KlineModal from '@/components/KlineModal.vue'

const marketStore = useMarketStore()

const newSymbol = ref('')
const adding = ref(false)
const klineVisible = ref(false)
const selectedQuote = ref<QuoteData | null>(null)

const sentiment = computed(() => marketStore.sentiment)
const quoteList = computed(() => marketStore.quoteList)

const vixClass = computed(() => {
  const vix = marketStore.sentiment?.vix ?? 0
  if (vix >= 30) return 'num-negative'
  if (vix <= 15) return 'num-positive'
  return 'text-[var(--t-text-primary)]'
})

const signalCount = computed(() => quoteList.value.filter(q => q.signal).length)
const signalSummary = computed(() => {
  const buy = quoteList.value.filter(q => q.signal === 'BUY').length
  const sell = quoteList.value.filter(q => q.signal === 'SELL').length
  const parts = []
  if (buy) parts.push(`${buy} 买入`)
  if (sell) parts.push(`${sell} 卖出`)
  const rest = signalCount.value - buy - sell
  if (rest) parts.push(`${rest} 超买超卖`)
  return parts.join(' · ')
})

const mockIndices = [
  { symbol: 'SPY', name: 'S&P 500', price: 522.40, changePercent: 0.43 },
  { symbol: 'QQQ', name: 'NASDAQ 100', price: 448.20, changePercent: 0.71 },
  { symbol: '000300.SH', name: '沪深300', price: 3842.15, changePercent: -0.32 },
]

async function addSymbol() {
  if (!newSymbol.value.trim()) return
  adding.value = true
  await marketStore.addSymbol(newSymbol.value.trim().toUpperCase())
  newSymbol.value = ''
  adding.value = false
}

function openKline(quote: QuoteData) {
  selectedQuote.value = quote
  klineVisible.value = true
}

// Auto-refresh every 60 seconds
let refreshTimer: ReturnType<typeof setInterval>

onMounted(async () => {
  await marketStore.init()
  refreshTimer = setInterval(() => {
    marketStore.fetchQuotes()
    marketStore.fetchSentiment()
  }, 60000)
})

onUnmounted(() => clearInterval(refreshTimer))
</script>
