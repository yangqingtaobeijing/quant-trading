<template>
  <div>
    <label class="block text-xs font-medium mb-1.5" style="color: var(--t-text-secondary);">{{ label }}</label>
    <input
      :value="modelValue"
      :type="type || 'text'"
      :placeholder="placeholder"
      :step="step"
      class="w-full px-3 py-2 rounded-lg text-sm border outline-none transition-colors"
      :class="mono ? 'font-mono' : ''"
      style="background: var(--t-bg-card); border-color: var(--t-border); color: var(--t-text-primary);"
      :style="{ borderColor: focused ? '#3B82F6' : 'var(--t-border)' }"
      @focus="focused = true"
      @blur="focused = false"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @change="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  label: string
  modelValue?: string | number
  placeholder?: string
  type?: string
  step?: string
  mono?: boolean
}>()
defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const focused = ref(false)
</script>
