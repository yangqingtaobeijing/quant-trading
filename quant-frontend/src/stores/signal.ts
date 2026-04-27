import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { signalApi, type Signal, type SignalType } from '@/api'

export const useSignalStore = defineStore('signal', () => {
  const signals = ref<Signal[]>([])
  const loading = ref(false)
  const scanning = ref(false)
  const lastScanTime = ref<Date | null>(null)
  const error = ref<string | null>(null)

  const latestSignals = computed(() => signals.value.slice(0, 5))
  const signalsByType = computed(() => {
    const map: Record<SignalType, Signal[]> = { BUY: [], SELL: [], OVERSOLD: [], OVERBOUGHT: [] }
    signals.value.forEach(s => { const t = s.signal_type || s.type; if (t && map[t]) map[t].push(s) })
    return map
  })

  async function fetchSignals() {
    loading.value = true
    error.value = null
    try {
      signals.value = await signalApi.getSignals()
    } catch (e: any) {
      error.value = `信号加载失败：${e?.message ?? '请确认后端服务已启动（端口 8888）'}`
      signals.value = []
    } finally {
      loading.value = false
    }
  }

  async function scan() {
    scanning.value = true
    error.value = null
    try {
      const res = await signalApi.scanSignals() as any
      const newSignals: Signal[] = Array.isArray(res) ? res : (res?.signals ?? [])
      const existingIds = new Set(signals.value.map(s => s.id))
      const fresh = newSignals.filter(s => !existingIds.has(s.id))
      signals.value = [...fresh, ...signals.value]
      lastScanTime.value = new Date()
    } catch (e: any) {
      error.value = `扫描失败：${e?.message ?? '请求失败'}`
    } finally {
      scanning.value = false
    }
  }

  return {
    signals, loading, scanning, lastScanTime, error,
    latestSignals, signalsByType,
    fetchSignals, scan
  }
})
