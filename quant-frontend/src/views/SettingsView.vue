<template>
  <div class="max-w-3xl">
    <div class="mb-6">
      <h2 class="text-base font-semibold mb-1" style="color: var(--t-text-primary);">系统设置</h2>
      <p class="text-xs" style="color: var(--t-text-muted);">配置 API 密钥、自选股和策略参数</p>
    </div>

    <div class="flex flex-col gap-5">
      <!-- API Key section -->
      <section class="rounded-xl border p-5" style="background: var(--t-bg-card); border-color: var(--t-border);">
        <h3 class="text-sm font-semibold mb-1" style="color: var(--t-text-primary);">API 配置</h3>
        <p class="text-xs mb-4" style="color: var(--t-text-muted);">
          行情数据由 Twelve Data 提供。
          <a href="https://twelvedata.com" target="_blank" class="hover:underline" style="color: #3B82F6;">获取免费 API Key →</a>
        </p>
        <div class="flex gap-3">
          <div class="flex-1">
            <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">Twelve Data API Key</label>
            <div class="relative">
              <input
                v-model="apiKey"
                :type="showApiKey ? 'text' : 'password'"
                placeholder="your_api_key_here"
                class="w-full px-3 py-2 pr-10 rounded-lg text-sm font-mono border outline-none transition-colors"
                style="background: var(--t-bg-deep); border-color: var(--t-border); color: var(--t-text-primary);"
                :style="{ borderColor: apiKey ? '#3B82F6' : 'var(--t-border)' }"
              />
              <button type="button"
                      class="absolute right-3 top-1/2 -translate-y-1/2"
                      style="color: var(--t-text-muted);"
                      @click="showApiKey = !showApiKey">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path v-if="showApiKey" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
                  <circle v-if="showApiKey" cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  <path v-if="!showApiKey" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="flex items-end">
            <button
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style="background: rgba(59,130,246,0.1); color: #3B82F6; border: 1px solid rgba(59,130,246,0.3);"
              @click="saveApiKey"
            >
              {{ saved ? '✓ 已保存' : '保存' }}
            </button>
          </div>
        </div>
      </section>

      <!-- Watchlist management -->
      <section class="rounded-xl border p-5" style="background: var(--t-bg-card); border-color: var(--t-border);">
        <h3 class="text-sm font-semibold mb-1" style="color: var(--t-text-primary);">自选股管理</h3>
        <p class="text-xs mb-4" style="color: var(--t-text-muted);">{{ marketStore.watchlist.length }} 支自选股</p>

        <div class="flex flex-wrap gap-2 mb-4">
          <div
            v-for="item in marketStore.watchlist"
            :key="item.symbol"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg"
            style="background: var(--t-bg-deep); border: 1px solid var(--t-border);"
          >
            <span class="font-mono text-sm" style="color: var(--t-text-primary);">{{ item.symbol }}</span>
            <span class="text-xs" style="color: var(--t-text-muted);">{{ item.name }}</span>
            <button
              class="ml-1 rounded transition-colors hover:text-red-400"
              style="color: var(--t-border-light);"
              @click="removeSymbol(item.symbol)"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div v-if="marketStore.watchlist.length === 0"
               class="text-xs py-2" style="color: var(--t-text-muted);">
            暂无自选股，请在行情总览页面添加
          </div>
        </div>
      </section>

      <!-- Strategy parameters -->
      <section class="rounded-xl border p-5" style="background: var(--t-bg-card); border-color: var(--t-border);">
        <h3 class="text-sm font-semibold mb-1" style="color: var(--t-text-primary);">策略参数</h3>
        <p class="text-xs mb-4" style="color: var(--t-text-muted);">调整 EMA 和 RSI 策略的核心参数</p>

        <div class="grid grid-cols-2 gap-5">
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-3" style="color: #3B82F6;">EMA 设置</h4>
            <div class="flex flex-col gap-3">
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">快线周期 (EMA20)</label>
                <div class="flex items-center gap-3">
                  <input type="range" v-model.number="params.ema20"
                         min="5" max="50" step="1"
                         class="flex-1 accent-blue-500 h-1 rounded-full appearance-none cursor-pointer"
                         style="background: var(--t-border);" />
                  <span class="font-mono text-sm w-8 text-right" style="color: #3B82F6;">{{ params.ema20 }}</span>
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">慢线周期 (EMA60)</label>
                <div class="flex items-center gap-3">
                  <input type="range" v-model.number="params.ema60"
                         min="20" max="200" step="5"
                         class="flex-1 accent-orange-400 h-1 rounded-full appearance-none cursor-pointer"
                         style="background: var(--t-border);" />
                  <span class="font-mono text-sm w-8 text-right" style="color: #F59E0B;">{{ params.ema60 }}</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-3" style="color: '#A78BFA';">RSI 设置</h4>
            <div class="flex flex-col gap-3">
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">
                  超卖阈值 (买入信号 ≤ {{ params.rsiOversold }})
                </label>
                <div class="flex items-center gap-3">
                  <input type="range" v-model.number="params.rsiOversold"
                         min="10" max="40" step="1"
                         class="flex-1 h-1 rounded-full appearance-none cursor-pointer"
                         style="background: var(--t-border); accent-color: #F59E0B;" />
                  <span class="font-mono text-sm w-8 text-right" style="color: #F59E0B;">{{ params.rsiOversold }}</span>
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">
                  超买阈值 (卖出信号 ≥ {{ params.rsiOverbought }})
                </label>
                <div class="flex items-center gap-3">
                  <input type="range" v-model.number="params.rsiOverbought"
                         min="60" max="90" step="1"
                         class="flex-1 h-1 rounded-full appearance-none cursor-pointer"
                         style="background: var(--t-border); accent-color: #FCD34D;" />
                  <span class="font-mono text-sm w-8 text-right" style="color: #FCD34D;">{{ params.rsiOverbought }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-5 pt-5 border-t flex items-center justify-between" style="border-color: var(--t-border);">
          <div class="text-xs" style="color: var(--t-text-muted);">
            参数修改后，需重新扫描信号才会生效
          </div>
          <button
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style="background: rgba(0,212,170,0.1); color: #00D4AA; border: 1px solid rgba(0,212,170,0.3);"
            @click="saveParams"
          >
            {{ paramSaved ? '✓ 已保存' : '保存参数' }}
          </button>
        </div>
      </section>

      <!-- About -->
      <section class="rounded-xl border p-5" style="background: var(--t-bg-card); border-color: var(--t-border);">
        <h3 class="text-sm font-semibold mb-3" style="color: var(--t-text-primary);">关于</h3>
        <div class="grid grid-cols-3 gap-4 text-xs font-mono">
          <div>
            <div style="color: var(--t-text-muted);">版本</div>
            <div style="color: var(--t-text-secondary);">v1.0.0</div>
          </div>
          <div>
            <div style="color: var(--t-text-muted);">后端地址</div>
            <div style="color: #3B82F6;">localhost:8888</div>
          </div>
          <div>
            <div style="color: var(--t-text-muted);">技术栈</div>
            <div style="color: var(--t-text-secondary);">Vue 3 + Pinia</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useMarketStore } from '@/stores/market'

const marketStore = useMarketStore()

const apiKey = ref('')
const showApiKey = ref(false)
const saved = ref(false)
const paramSaved = ref(false)

const params = reactive({
  ema20: 20,
  ema60: 60,
  rsiOversold: 30,
  rsiOverbought: 70,
})

function saveApiKey() {
  localStorage.setItem('quant_api_key', apiKey.value)
  saved.value = true
  setTimeout(() => { saved.value = false }, 2000)
}

function saveParams() {
  localStorage.setItem('quant_params', JSON.stringify(params))
  paramSaved.value = true
  setTimeout(() => { paramSaved.value = false }, 2000)
}

async function removeSymbol(symbol: string) {
  await marketStore.removeSymbol(symbol)
}

// Load persisted settings
const savedKey = localStorage.getItem('quant_api_key')
if (savedKey) apiKey.value = savedKey

const savedParams = localStorage.getItem('quant_params')
if (savedParams) {
  try {
    const p = JSON.parse(savedParams)
    Object.assign(params, p)
  } catch {}
}
</script>
