<template>
  <div class="flex items-center gap-1.5 px-2 py-1 rounded" style="background: var(--t-bg-card); border: 1px solid var(--t-border);">
    <div
      class="w-1.5 h-1.5 rounded-full"
      :class="status === 'open' ? 'animate-pulse' : ''"
      :style="{ background: status === 'open' ? '#00D4AA' : 'var(--t-text-muted)' }"
    ></div>
    <span class="text-xs font-mono" :style="{ color: status === 'open' ? '#00D4AA' : 'var(--t-text-muted)' }">
      {{ label }}
    </span>
    <span class="text-xs font-mono" :style="{ color: status === 'open' ? '#00D4AA' : 'var(--t-text-muted)' }">
      {{ status === 'open' ? '开盘中' : '已收盘' }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  status: 'open' | 'closed'
}>()
</script>
