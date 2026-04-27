<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center p-4"
           style="background: rgba(0,0,0,0.75);" @click.self="$emit('close')">
        <div class="rounded-2xl border overflow-hidden flex flex-col"
             style="background: var(--t-bg-sidebar); border-color: var(--t-border); width: min(1100px, 95vw); height: min(700px, 90vh);">

          <!-- Modal Header -->
          <div class="flex items-center justify-between px-5 py-3.5 border-b shrink-0"
               style="border-color: var(--t-border);">
            <div class="flex items-center gap-4">
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-mono font-bold text-base" style="color: var(--t-text-primary);">{{ quote?.symbol }}</span>
                  <span class="text-xs px-1.5 py-0.5 rounded font-mono"
                        :style="{ background: 'var(--t-border)', color: quote?.market === 'CN' ? '#F59E0B' : '#3B82F6' }">
                    {{ quote?.market }}
                  </span>
                </div>
                <div class="text-xs" style="color: var(--t-text-secondary);">{{ quote?.name }}</div>
              </div>
              <div class="h-8 w-px" style="background: var(--t-border);"></div>
              <div>
                <div class="font-mono font-bold text-xl" style="color: var(--t-text-primary);">
                  {{ quote?.market === 'CN' ? '¥' : '$' }}{{ formatNumber(quote?.price ?? 0) }}
                </div>
                <div class="font-mono text-sm" :class="changeClass(quote?.changePercent ?? 0)">
                  {{ formatChangePercent(quote?.changePercent ?? 0) }}
                </div>
              </div>
            </div>

            <!-- Interval selector -->
            <div class="flex items-center gap-3">
              <div class="flex gap-1 p-1 rounded-lg" style="background: var(--t-bg-card);">
                <button v-for="iv in intervals" :key="iv.value"
                        class="px-3 py-1 rounded text-xs font-mono transition-colors"
                        :style="selectedInterval === iv.value
                          ? 'background: var(--t-border); color: #00D4AA;'
                          : 'color: var(--t-text-muted);'"
                        @click="setIntervalValue(iv.value)">
                  {{ iv.label }}
                </button>
              </div>
              <button class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-white/10"
                      style="color: var(--t-text-muted);" @click="$emit('close')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Loading overlay -->
          <div v-if="loading" class="flex-1 flex items-center justify-center">
            <div class="flex flex-col items-center gap-3">
              <div class="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin"
                   style="border-color: var(--t-border); border-top-color: #00D4AA;"></div>
              <span class="text-sm" style="color: var(--t-text-muted);">加载K线数据...</span>
            </div>
          </div>

          <!-- Charts container -->
          <div v-show="!loading" class="flex-1 flex flex-col overflow-hidden">
            <!-- Candlestick chart -->
            <div ref="candleContainer" class="flex-1" style="min-height: 0;"></div>
            <!-- Divider -->
            <div class="h-px shrink-0" style="background: var(--t-border);"></div>
            <!-- RSI sub-chart -->
            <div ref="rsiContainer" class="shrink-0" style="height: 120px;"></div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'
import type { QuoteData, KlineData } from '@/api'
import { marketApi } from '@/api'
import { formatNumber, formatChangePercent, changeClass } from '@/utils/format'
import {
  createChart,
  ColorType,
  CrosshairMode,
  CandlestickSeries,
  LineSeries,
  createSeriesMarkers,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type LineData,
  type Time,
} from 'lightweight-charts'

const props = defineProps<{
  visible: boolean
  quote: QuoteData | null
}>()
defineEmits<{ (e: 'close'): void }>()

const candleContainer = ref<HTMLElement | null>(null)
const rsiContainer = ref<HTMLElement | null>(null)
const loading = ref(false)
const selectedInterval = ref('1d')

const intervals = [
  { value: '1d', label: '日K' },
  { value: '1wk', label: '周K' },
  { value: '1mo', label: '月K' },
]

const chartOptions = {
  layout: {
    background: { type: ColorType.Solid, color: 'var(--t-bg-sidebar)' },
    textColor: 'var(--t-text-secondary)',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11,
  },
  grid: {
    vertLines: { color: '#1A2338' },
    horzLines: { color: '#1A2338' },
  },
  crosshair: { mode: CrosshairMode.Normal },
  rightPriceScale: {
    borderColor: 'var(--t-border)',
    scaleMargins: { top: 0.1, bottom: 0.1 },
  },
  timeScale: {
    borderColor: 'var(--t-border)',
    timeVisible: true,
    secondsVisible: false,
  },
}

let candleChart: IChartApi | null = null
let rsiChart: IChartApi | null = null
let candleSeries: ISeriesApi<'Candlestick'> | null = null
let ema20Series: ISeriesApi<'Line'> | null = null
let ema60Series: ISeriesApi<'Line'> | null = null
let rsiLineSeries: ISeriesApi<'Line'> | null = null
let resizeObserver: ResizeObserver | null = null

function initCharts() {
  if (!candleContainer.value || !rsiContainer.value) return
  destroyCharts()

  const cWidth = candleContainer.value.clientWidth || 800
  const cHeight = candleContainer.value.clientHeight || 450

  candleChart = createChart(candleContainer.value, {
    ...chartOptions,
    width: cWidth,
    height: cHeight,
  })

  candleSeries = candleChart.addSeries(CandlestickSeries, {
    upColor: '#00D4AA',
    downColor: '#FF4D4D',
    borderUpColor: '#00D4AA',
    borderDownColor: '#FF4D4D',
    wickUpColor: '#00D4AA',
    wickDownColor: '#FF4D4D',
  })

  ema20Series = candleChart.addSeries(LineSeries, {
    color: '#3B82F6',
    lineWidth: 1,
    priceLineVisible: false,
    lastValueVisible: false,
    title: 'EMA20',
  })

  ema60Series = candleChart.addSeries(LineSeries, {
    color: '#F59E0B',
    lineWidth: 1,
    priceLineVisible: false,
    lastValueVisible: false,
    title: 'EMA60',
  })

  rsiChart = createChart(rsiContainer.value, {
    ...chartOptions,
    width: rsiContainer.value.clientWidth || 800,
    height: 120,
  })

  rsiLineSeries = rsiChart.addSeries(LineSeries, {
    color: '#A78BFA',
    lineWidth: 1,
    priceLineVisible: false,
    lastValueVisible: true,
    title: 'RSI14',
  })

  // Sync crosshair
  candleChart.subscribeCrosshairMove(param => {
    if (rsiChart && param.time) {
      rsiChart.setCrosshairPosition(0 as any, param.time, rsiLineSeries!)
    }
  })

  // Resize observer
  const ro = new ResizeObserver(() => {
    if (candleChart && candleContainer.value) {
      candleChart.resize(
        candleContainer.value.clientWidth,
        candleContainer.value.clientHeight
      )
    }
    if (rsiChart && rsiContainer.value) {
      rsiChart.resize(rsiContainer.value.clientWidth, 120)
    }
  })
  if (candleContainer.value) ro.observe(candleContainer.value)
  if (rsiContainer.value) ro.observe(rsiContainer.value)
  resizeObserver = ro
}

function destroyCharts() {
  resizeObserver?.disconnect()
  resizeObserver = null
  try { candleChart?.remove() } catch {}
  try { rsiChart?.remove() } catch {}
  candleChart = null
  rsiChart = null
  candleSeries = null
  ema20Series = null
  ema60Series = null
  rsiLineSeries = null
}

async function loadData() {
  if (!props.quote) return
  loading.value = true
  let klineData: KlineData[]
  try {
    klineData = await marketApi.getKline(props.quote.symbol, selectedInterval.value, 200)
  } catch {
    klineData = generateMockKline(props.quote.price, 200)
  }
  loading.value = false
  await nextTick()
  if (!candleSeries) initCharts()
  await nextTick()
  setChartData(klineData)
}

function setChartData(data: KlineData[]) {
  if (!candleSeries || !ema20Series || !ema60Series || !rsiLineSeries) return

  const candles: CandlestickData<Time>[] = data.map(d => ({
    time: d.time as Time,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
  }))
  candleSeries.setData(candles)

  const ema20Data: LineData<Time>[] = data
    .filter(d => d.ema20 != null)
    .map(d => ({ time: d.time as Time, value: d.ema20! }))
  const ema60Data: LineData<Time>[] = data
    .filter(d => d.ema60 != null)
    .map(d => ({ time: d.time as Time, value: d.ema60! }))
  const rsiData: LineData<Time>[] = data
    .filter(d => d.rsi14 != null)
    .map(d => ({ time: d.time as Time, value: d.rsi14! }))

  ema20Series.setData(ema20Data)
  ema60Series.setData(ema60Data)
  rsiLineSeries.setData(rsiData)

  // Series markers (v5 API)
  const markerList = data
    .filter(d => d.signal)
    .map(d => ({
      time: d.time as Time,
      position: (d.signal === 'BUY' || d.signal === 'OVERSOLD') ? 'belowBar' : 'aboveBar',
      color: (d.signal === 'BUY' || d.signal === 'OVERSOLD') ? '#00D4AA' : '#FF4D4D',
      shape: (d.signal === 'BUY' || d.signal === 'OVERSOLD') ? 'arrowUp' : 'arrowDown',
      text: d.signal === 'BUY' ? 'B' : d.signal === 'SELL' ? 'S' : d.signal!.charAt(0),
    }))

  if (markerList.length > 0) {
    createSeriesMarkers(candleSeries, markerList as any)
  }

  candleChart?.timeScale().fitContent()
  rsiChart?.timeScale().fitContent()
}

function setIntervalValue(iv: string) {
  selectedInterval.value = iv
  loadData()
}

watch(() => props.visible, async (v) => {
  if (v) {
    loading.value = true
    await nextTick()
    initCharts()
    await loadData()
  } else {
    destroyCharts()
  }
})

watch(() => props.quote, () => {
  if (props.visible) loadData()
})

onUnmounted(destroyCharts)

// ─── Mock K-line generator ─────────────────────────────────────────────────

function generateMockKline(currentPrice: number, count: number): KlineData[] {
  const data: KlineData[] = []
  let price = currentPrice * 0.7
  const now = Math.floor(Date.now() / 1000)
  const daySeconds = 86400

  for (let i = count; i >= 0; i--) {
    const change = (Math.random() - 0.48) * price * 0.02
    const open = price
    const close = price + change
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    const low = Math.min(open, close) * (1 - Math.random() * 0.01)
    const volume = Math.floor(Math.random() * 50000000 + 10000000)
    const time = Math.floor((now - i * daySeconds) / daySeconds) * daySeconds
    data.push({ time, open, high, low, close, volume })
    price = close
  }

  // EMA
  const k20 = 2 / 21
  const k60 = 2 / 61
  let ema20 = data[0]!.close
  let ema60 = data[0]!.close
  for (let i = 0; i < data.length; i++) {
    const item = data[i]!
    ema20 = item.close * k20 + ema20 * (1 - k20)
    ema60 = item.close * k60 + ema60 * (1 - k60)
    if (i >= 19) item.ema20 = ema20
    if (i >= 59) item.ema60 = ema60
  }

  // RSI14
  for (let i = 14; i < data.length; i++) {
    let gains = 0
    let losses = 0
    for (let j = i - 13; j <= i; j++) {
      const curr = data[j]!
      const prev = data[j - 1]!
      const diff = curr.close - prev.close
      if (diff > 0) gains += diff
      else losses += Math.abs(diff)
    }
    const rs = losses === 0 ? 100 : gains / losses
    const rsiVal = 100 - 100 / (1 + rs)
    data[i]!.rsi14 = rsiVal
    if (rsiVal < 30) data[i]!.signal = 'OVERSOLD'
    else if (rsiVal > 70) data[i]!.signal = 'OVERBOUGHT'
  }

  return data
}
</script>
