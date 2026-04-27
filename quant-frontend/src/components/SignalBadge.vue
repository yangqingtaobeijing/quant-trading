<template>
  <span class="badge" :class="badgeClass">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SignalType } from '@/api'

const props = defineProps<{ type: SignalType }>()

const badgeClass = computed(() => {
  switch (props.type) {
    case 'BUY': return 'badge-buy'
    case 'SELL': return 'badge-sell'
    case 'OVERSOLD': return 'badge-oversold'
    case 'OVERBOUGHT': return 'badge-overbought'
  }
})

const label = computed(() => {
  switch (props.type) {
    case 'BUY': return '买入'
    case 'SELL': return '卖出'
    case 'OVERSOLD': return '超卖'
    case 'OVERBOUGHT': return '超买'
  }
})
</script>
