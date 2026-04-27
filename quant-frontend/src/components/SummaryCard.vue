<template>
  <div class="rounded-xl border p-4" style="background: var(--t-bg-card); border-color: var(--t-border);">
    <div class="text-xs mb-2" style="color: var(--t-text-muted);">{{ label }}</div>
    <div
      class="font-mono font-bold"
      :class="large ? 'text-2xl' : 'text-base'"
      :style="{
        color: positive === true ? '#00D4AA' : positive === false ? '#FF4D4D' : 'var(--t-text-primary)'
      }"
    >
      {{ value }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string
  positive?: boolean
  icon?: string
  large?: boolean
}>()
</script>
