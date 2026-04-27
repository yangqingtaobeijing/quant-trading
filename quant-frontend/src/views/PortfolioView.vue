<template>
  <div class="flex gap-5">
    <!-- Left: Main table area -->
    <div class="flex-1 min-w-0">
      <!-- Header -->
      <div class="flex items-center justify-between mb-5">
        <div>
          <h2 class="text-base font-semibold mb-1" style="color: var(--t-text-primary);">持仓管理</h2>
          <p class="text-xs" style="color: var(--t-text-muted);">{{ portfolioStore.positions.length }} 个持仓</p>
        </div>
        <button
          class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
          style="background: rgba(59,130,246,0.1); color: #3B82F6; border: 1px solid rgba(59,130,246,0.3);"
          @click="openDrawer()"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
          添加持仓
        </button>
      </div>

      <!-- Error -->
      <div v-if="portfolioStore.error" class="rounded-xl border mb-4 px-5 py-3 flex items-center gap-3"
           style="background: rgba(255,77,77,0.08); border-color: rgba(255,77,77,0.3);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="color: #FF4D4D; flex-shrink: 0;">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span class="text-sm" style="color: #FF4D4D;">{{ portfolioStore.error }}</span>
        <button class="ml-auto text-xs px-3 py-1 rounded-lg"
                style="color: #FF4D4D; border: 1px solid rgba(255,77,77,0.3);"
                @click="portfolioStore.fetchPortfolio()">重试</button>
      </div>

      <!-- Loading -->
      <div v-if="portfolioStore.loading" class="space-y-2">
        <div v-for="i in 4" :key="i" class="skeleton h-16 rounded-lg w-full"></div>
      </div>

      <!-- Table -->
      <div v-else class="rounded-xl border overflow-hidden" style="border-color: var(--t-border);">
        <table class="w-full" style="min-width: 900px;">
          <thead>
            <tr style="background: var(--t-bg-card); border-bottom: 1px solid var(--t-border);">
              <th v-for="col in columns" :key="col"
                  class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider"
                  style="color: var(--t-text-muted);">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="portfolioStore.positionsWithCalc.length === 0">
              <td :colspan="columns.length" class="px-4 py-12 text-center">
                <div class="text-sm" style="color: var(--t-text-muted);">暂无持仓记录</div>
              </td>
            </tr>
            <tr
              v-for="(pos, i) in portfolioStore.positionsWithCalc"
              :key="pos.id"
              class="border-b transition-colors hover:bg-white/3"
              :style="{
                borderColor: '#1A2338',
                background: pos.pnl >= 0
                  ? (i % 2 === 0 ? 'rgba(0,212,170,0.03)' : 'rgba(0,212,170,0.05)')
                  : (i % 2 === 0 ? 'rgba(255,77,77,0.03)' : 'rgba(255,77,77,0.05)')
              }"
            >
              <!-- Symbol -->
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <span class="font-mono font-semibold text-sm" style="color: var(--t-text-primary);">{{ pos.symbol }}</span>
                  <span class="text-xs px-1 py-0.5 rounded font-mono"
                        :style="{ background: 'var(--t-border)', color: pos.market === 'CN' ? '#F59E0B' : '#3B82F6', fontSize: '10px' }">
                    {{ pos.market }}
                  </span>
                </div>
                <div class="text-xs mt-0.5" style="color: var(--t-text-muted);">{{ pos.name }}</div>
              </td>

              <!-- Buy price -->
              <td class="px-4 py-3">
                <span class="font-mono text-sm" style="color: var(--t-text-secondary);">
                  {{ pos.market === 'CN' ? '¥' : '$' }}{{ formatNumber(pos.buyPrice) }}
                </span>
              </td>

              <!-- Current price -->
              <td class="px-4 py-3">
                <span class="font-mono text-sm font-medium" style="color: var(--t-text-primary);">
                  {{ pos.market === 'CN' ? '¥' : '$' }}{{ formatNumber(pos.currentPrice) }}
                </span>
              </td>

              <!-- Quantity -->
              <td class="px-4 py-3">
                <span class="font-mono text-sm" style="color: var(--t-text-secondary);">{{ pos.quantity }}</span>
              </td>

              <!-- PnL amount -->
              <td class="px-4 py-3">
                <div class="font-mono text-sm font-semibold" :class="pos.pnl >= 0 ? 'num-positive' : 'num-negative'">
                  {{ pos.pnl >= 0 ? '+' : '' }}{{ pos.market === 'CN' ? '¥' : '$' }}{{ formatNumber(Math.abs(pos.pnl)) }}
                </div>
                <div class="font-mono text-xs" :class="pos.pnlPct >= 0 ? 'num-positive' : 'num-negative'">
                  {{ pos.pnlPct >= 0 ? '+' : '' }}{{ pos.pnlPct.toFixed(2) }}%
                </div>
              </td>

              <!-- Stop Loss (inline edit) -->
              <td class="px-4 py-3">
                <InlineEdit
                  :value="pos.stopLoss"
                  :prefix="pos.market === 'CN' ? '¥' : '$'"
                  @update="(v) => updateField(pos.id, 'stopLoss', v)"
                />
              </td>

              <!-- Take Profit (inline edit) -->
              <td class="px-4 py-3">
                <InlineEdit
                  :value="pos.takeProfit"
                  :prefix="pos.market === 'CN' ? '¥' : '$'"
                  @update="(v) => updateField(pos.id, 'takeProfit', v)"
                />
              </td>

              <!-- Hold days -->
              <td class="px-4 py-3">
                <span class="font-mono text-xs" style="color: var(--t-text-secondary);">{{ pos.holdDays }}天</span>
              </td>

              <!-- Actions -->
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button
                    class="p-1.5 rounded transition-colors hover:bg-white/10"
                    style="color: var(--t-text-muted);"
                    @click="openDrawer(pos)"
                    title="编辑"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                  <button
                    class="p-1.5 rounded transition-colors hover:bg-red-500/10"
                    style="color: var(--t-text-muted);"
                    @click="deletePosition(pos.id)"
                    title="删除"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                      <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Right: Summary cards -->
    <div class="w-56 shrink-0 flex flex-col gap-3">
      <SummaryCard
        label="总投入"
        :value="`$${formatNumber(portfolioStore.summary.totalCost)}`"
        icon="cost"
      />
      <SummaryCard
        label="当前市值"
        :value="`$${formatNumber(portfolioStore.summary.totalValue)}`"
        icon="value"
      />
      <SummaryCard
        label="总盈亏"
        :value="`${portfolioStore.summary.totalPnL >= 0 ? '+' : ''}$${formatNumber(Math.abs(portfolioStore.summary.totalPnL))}`"
        :positive="portfolioStore.summary.totalPnL >= 0"
        icon="pnl"
      />
      <SummaryCard
        label="盈亏比例"
        :value="`${portfolioStore.summary.totalPnLPct >= 0 ? '+' : ''}${portfolioStore.summary.totalPnLPct.toFixed(2)}%`"
        :positive="portfolioStore.summary.totalPnLPct >= 0"
        icon="percent"
        large
      />
    </div>
  </div>

  <!-- Add/Edit Drawer -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="drawerVisible" class="fixed inset-0 z-50 flex justify-end"
           style="background: rgba(0,0,0,0.6);" @click.self="drawerVisible = false">
        <div class="h-full flex flex-col border-l overflow-y-auto"
             style="width: 400px; background: var(--t-bg-sidebar); border-color: var(--t-border);">
          <!-- Drawer header -->
          <div class="flex items-center justify-between px-5 py-4 border-b shrink-0"
               style="border-color: var(--t-border);">
            <span class="font-semibold text-sm" style="color: var(--t-text-primary);">
              {{ editingId ? '编辑持仓' : '添加持仓' }}
            </span>
            <button class="w-7 h-7 flex items-center justify-center rounded hover:bg-white/10"
                    style="color: var(--t-text-muted);" @click="drawerVisible = false">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- Form -->
          <form class="flex-1 p-5 flex flex-col gap-4" @submit.prevent="submitForm">
            <div class="grid grid-cols-2 gap-4">
              <FormField label="股票代码 *" v-model="form.symbol" placeholder="AAPL" mono />
              <FormField label="股票名称 *" v-model="form.name" placeholder="苹果公司" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">市场 *</label>
              <div class="flex gap-2">
                <button type="button" v-for="m in ['US', 'CN']" :key="m"
                        class="flex-1 py-2 rounded-lg text-sm font-medium transition-all"
                        :style="form.market === m
                          ? { background: 'var(--t-border)', color: m === 'US' ? '#3B82F6' : '#F59E0B', border: `1px solid ${m === 'US' ? '#3B82F6' : '#F59E0B'}` }
                          : { background: 'var(--t-bg-card)', color: 'var(--t-text-muted)', border: '1px solid var(--t-border)' }"
                        @click="form.market = m as any">
                  {{ m === 'US' ? '🇺🇸 美股' : '🇨🇳 A股' }}
                </button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <FormField label="买入价 *" v-model.number="form.buyPrice" type="number" step="0.01" placeholder="0.00" mono />
              <FormField label="数量 *" v-model.number="form.quantity" type="number" placeholder="100" mono />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <FormField label="止损价" v-model.number="form.stopLoss" type="number" step="0.01" placeholder="可选" mono />
              <FormField label="止盈价" v-model.number="form.takeProfit" type="number" step="0.01" placeholder="可选" mono />
            </div>
            <FormField label="买入日期 *" v-model="form.buyDate" type="date" />
            <FormField label="备注" v-model="form.notes" placeholder="可选备注..." />

            <div class="flex gap-3 pt-2 mt-auto">
              <button type="button"
                      class="flex-1 py-2.5 rounded-lg text-sm transition-colors"
                      style="background: var(--t-bg-card); color: var(--t-text-secondary); border: 1px solid var(--t-border);"
                      @click="drawerVisible = false">
                取消
              </button>
              <button type="submit"
                      class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all"
                      style="background: rgba(59,130,246,0.15); color: #3B82F6; border: 1px solid rgba(59,130,246,0.3);">
                {{ editingId ? '保存修改' : '添加持仓' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import type { Position, CreatePositionDto } from '@/api'
import { formatNumber } from '@/utils/format'
import InlineEdit from '@/components/InlineEdit.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import FormField from '@/components/FormField.vue'

const portfolioStore = usePortfolioStore()

const columns = ['股票', '买入价', '当前价', '数量', '盈亏', '止损价', '止盈价', '持仓天数', '操作']

const drawerVisible = ref(false)
const editingId = ref<string | null>(null)

const defaultForm = () => ({
  symbol: '',
  name: '',
  market: 'US' as 'US' | 'CN',
  buyPrice: 0,
  quantity: 0,
  stopLoss: undefined as number | undefined,
  takeProfit: undefined as number | undefined,
  buyDate: new Date().toISOString().slice(0, 10),
  notes: '',
})

const form = reactive(defaultForm())

function openDrawer(pos?: Position & { pnl?: number; pnlPct?: number; holdDays?: number }) {
  Object.assign(form, defaultForm())
  editingId.value = null
  if (pos) {
    editingId.value = pos.id
    form.symbol = pos.symbol
    form.name = pos.name
    form.market = pos.market
    form.buyPrice = pos.buyPrice
    form.quantity = pos.quantity
    form.stopLoss = pos.stopLoss
    form.takeProfit = pos.takeProfit
    form.buyDate = pos.buyDate
    form.notes = pos.notes ?? ''
  }
  drawerVisible.value = true
}

async function submitForm() {
  const dto: CreatePositionDto = {
    symbol: form.symbol.toUpperCase(),
    name: form.name,
    market: form.market,
    buyPrice: form.buyPrice,
    quantity: form.quantity,
    stopLoss: form.stopLoss || undefined,
    takeProfit: form.takeProfit || undefined,
    buyDate: form.buyDate,
    notes: form.notes || undefined,
  }
  if (editingId.value) {
    await portfolioStore.updatePosition(editingId.value, dto)
  } else {
    await portfolioStore.addPosition(dto)
  }
  drawerVisible.value = false
}

async function updateField(id: string, field: 'stopLoss' | 'takeProfit', value: number) {
  await portfolioStore.updatePosition(id, { [field]: value })
}

async function deletePosition(id: string) {
  if (confirm('确认删除该持仓记录？')) {
    await portfolioStore.deletePosition(id)
  }
}

onMounted(() => portfolioStore.fetchPortfolio())
</script>
