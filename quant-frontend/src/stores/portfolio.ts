import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { portfolioApi, type Position, type CreatePositionDto } from '@/api'

export const usePortfolioStore = defineStore('portfolio', () => {
  const positions = ref<Position[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const summary = computed(() => {
    const totalCost = positions.value.reduce((sum, p) => sum + p.buyPrice * p.quantity, 0)
    const totalValue = positions.value.reduce((sum, p) => sum + p.currentPrice * p.quantity, 0)
    const totalPnL = totalValue - totalCost
    const totalPnLPct = totalCost > 0 ? (totalPnL / totalCost) * 100 : 0
    return { totalCost, totalValue, totalPnL, totalPnLPct }
  })

  const positionsWithCalc = computed(() =>
    positions.value.map(p => {
      const cost = p.buyPrice * p.quantity
      const value = p.currentPrice * p.quantity
      const pnl = value - cost
      const pnlPct = (pnl / cost) * 100
      const buyDate = new Date(p.buyDate)
      const now = new Date()
      const days = Math.floor((now.getTime() - buyDate.getTime()) / (1000 * 60 * 60 * 24))
      return { ...p, cost, value, pnl, pnlPct, holdDays: days }
    })
  )

  async function fetchPortfolio() {
    loading.value = true
    error.value = null
    try {
      positions.value = await portfolioApi.getPortfolio()
    } catch (e: any) {
      error.value = `持仓数据加载失败：${e?.message ?? '请确认后端服务已启动（端口 8888）'}`
      positions.value = []
    } finally {
      loading.value = false
    }
  }

  async function addPosition(dto: CreatePositionDto) {
    error.value = null
    try {
      const pos = await portfolioApi.addPosition(dto)
      positions.value.push(pos)
    } catch (e: any) {
      error.value = `添加持仓失败：${e?.message ?? '请求失败'}`
      throw e
    }
  }

  async function updatePosition(id: string, data: Partial<Position>) {
    error.value = null
    try {
      const updated = await portfolioApi.updatePosition(id, data)
      const idx = positions.value.findIndex(p => p.id === id)
      if (idx !== -1) positions.value[idx] = updated
    } catch (e: any) {
      error.value = `更新失败：${e?.message ?? '请求失败'}`
      throw e
    }
  }

  async function deletePosition(id: string) {
    error.value = null
    try {
      await portfolioApi.deletePosition(id)
      positions.value = positions.value.filter(p => p.id !== id)
    } catch (e: any) {
      error.value = `删除失败：${e?.message ?? '请求失败'}`
      throw e
    }
  }

  return {
    positions, loading, error,
    summary, positionsWithCalc,
    fetchPortfolio, addPosition, updatePosition, deletePosition
  }
})
