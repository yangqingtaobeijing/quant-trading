<template>
  <div class="flex items-center gap-1 group/inline">
    <template v-if="!editing">
      <span class="font-mono text-sm" :style="{ color: value ? 'var(--t-text-secondary)' : 'var(--t-border-light)' }">
        {{ value ? `${prefix}${formatNumber(value)}` : '—' }}
      </span>
      <button
        class="opacity-0 group-hover/inline:opacity-100 p-0.5 rounded transition-all"
        style="color: var(--t-text-muted);"
        @click="startEdit"
      >
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4z" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </template>
    <template v-else>
      <span class="text-xs font-mono" style="color: var(--t-text-muted);">{{ prefix }}</span>
      <input
        ref="inputRef"
        v-model.number="editValue"
        type="number"
        step="0.01"
        class="font-mono text-sm border rounded px-1.5 py-0.5 outline-none w-24"
        style="background: var(--t-bg-deep); border-color: #3B82F6; color: var(--t-text-primary);"
        @keydown.enter="confirm"
        @keydown.escape="cancel"
        @blur="confirm"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { formatNumber } from '@/utils/format'

const props = defineProps<{
  value?: number
  prefix?: string
}>()
const emit = defineEmits<{ (e: 'update', v: number): void }>()

const editing = ref(false)
const editValue = ref<number>(0)
const inputRef = ref<HTMLInputElement | null>(null)

async function startEdit() {
  editValue.value = props.value ?? 0
  editing.value = true
  await nextTick()
  inputRef.value?.select()
}

function confirm() {
  editing.value = false
  if (editValue.value > 0) emit('update', editValue.value)
}

function cancel() {
  editing.value = false
}
</script>
