<template>
  <div class="rounded-xl border p-4 overflow-hidden" style="background: var(--t-bg-card); border-color: var(--t-border);">
    <div class="flex items-start justify-between mb-3">
      <div>
        <div class="skeleton h-4 w-20 mb-1.5"></div>
        <div class="skeleton h-3 w-28"></div>
      </div>
    </div>
    <div class="flex items-end justify-between mb-3">
      <div class="skeleton h-7 w-28"></div>
      <div class="text-right">
        <div class="skeleton h-4 w-16 mb-1"></div>
        <div class="skeleton h-3 w-12 ml-auto"></div>
      </div>
    </div>
    <div class="h-px mb-3" style="background: var(--t-border);"></div>
    <div class="grid grid-cols-3 gap-2">
      <div v-for="i in 3" :key="i">
        <div class="skeleton h-3 w-10 mb-1"></div>
        <div class="skeleton h-3.5 w-14"></div>
      </div>
    </div>
    <div class="mt-2 skeleton h-3 w-20"></div>
  </div>
</template>
