<template>
  <RouterLink
    :to="item.path"
    class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative overflow-hidden"
    :style="active
      ? 'background: rgba(0,212,170,0.1); color: #00D4AA;'
      : 'color: var(--t-text-secondary);'"
    :class="active ? '' : 'hover:bg-white/5 hover:text-[#C0CDD8]'"
    :title="!expanded ? item.label : ''"
  >
    <!-- Active indicator -->
    <div v-if="active" class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full"
         style="background: #00D4AA;"></div>

    <!-- Icon -->
    <div class="shrink-0 w-5 h-5 flex items-center justify-center">
      <NavIcon :name="item.icon" />
    </div>

    <!-- Label -->
    <transition name="fade">
      <span v-if="expanded" class="text-sm font-medium whitespace-nowrap">{{ item.label }}</span>
    </transition>
  </RouterLink>
</template>

<script setup lang="ts">
import NavIcon from './NavIcon.vue'

defineProps<{
  item: { path: string; label: string; icon: string }
  expanded: boolean
  active: boolean
}>()
</script>
