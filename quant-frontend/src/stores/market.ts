import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { marketApi, type QuoteData, type MarketSentiment, type WatchlistItem } from '@/api'

export const useMarketStore = defineStore('market', () => {
  // State
  const watchlist = ref<WatchlistItem[]>([])
  const quotes = ref<Map<string, QuoteData>>(new Map())
  const sentiment = ref<MarketSentiment | null>(null)
  const loading = ref(false)
  const quotesLoading = ref(false)
  const lastUpdated = ref<Date | null>(null)
  const error = ref<string | null>(null)

  // Getters
  const quoteList = computed(() =>
    watchlist.value.map(w => quotes.value.get(w.symbol)).filter(Boolean) as QuoteData[]
  )

  const hasSignals = computed(() =>
    quoteList.value.filter(q => q.signal).length
  )

  // Actions
  async function fetchWatchlist() {
    try {
      watchlist.value = await marketApi.getWatchlist()
      error.value = null
    } catch (e: any) {
      error.value = `自选股加载失败：${e?.message ?? '网络错误，请确认后端服务已启动（端口 8888）'}`
    }
  }

  async function fetchQuotes() {
    if (watchlist.value.length === 0) return
    quotesLoading.value = true
    try {
      const symbols = watchlist.value.map(w => w.symbol)
      const data = await marketApi.getQuotes(symbols, watchlist.value)
      data.forEach(q => quotes.value.set(q.symbol, q))
      lastUpdated.value = new Date()
      error.value = null
    } catch (e: any) {
      error.value = `行情数据加载失败：${e?.message ?? '请求超时或服务异常'}`
    } finally {
      quotesLoading.value = false
    }
  }

  async function fetchSentiment() {
    try {
      sentiment.value = await marketApi.getSentiment()
    } catch {
      // 市场情绪不显示错误，不影响主功能
      sentiment.value = null
    }
  }

  async function addSymbol(symbol: string) {
    try {
      await marketApi.addSymbol(symbol)
      await fetchWatchlist()
      await fetchQuotes()
      error.value = null
    } catch (e: any) {
      error.value = `添加失败：${e?.message ?? '请求失败'}`
    }
  }

  async function removeSymbol(symbol: string) {
    try {
      await marketApi.removeSymbol(symbol)
      watchlist.value = watchlist.value.filter(w => w.symbol !== symbol)
      quotes.value.delete(symbol)
      error.value = null
    } catch (e: any) {
      error.value = `删除失败：${e?.message ?? '请求失败'}`
    }
  }

  async function init() {
    loading.value = true
    error.value = null
    await fetchWatchlist()
    await Promise.all([fetchQuotes(), fetchSentiment()])
    loading.value = false
  }

  return {
    watchlist, quotes, sentiment, loading, quotesLoading, lastUpdated, error,
    quoteList, hasSignals,
    fetchWatchlist, fetchQuotes, fetchSentiment, addSymbol, removeSymbol, init
  }
})
