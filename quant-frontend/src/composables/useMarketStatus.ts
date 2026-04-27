import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useMarketStatus() {
  const now = ref(new Date())
  let timer: ReturnType<typeof setInterval>

  onMounted(() => {
    timer = setInterval(() => { now.value = new Date() }, 1000)
  })
  onUnmounted(() => clearInterval(timer))

  const timeStr = computed(() => {
    return now.value.toLocaleTimeString('zh-CN', { hour12: false })
  })

  const dateStr = computed(() => {
    return now.value.toLocaleDateString('zh-CN', {
      year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short'
    })
  })

  const usStatus = computed(() => {
    const h = now.value.getUTCHours()
    const m = now.value.getUTCMinutes()
    const totalMin = h * 60 + m
    const dow = now.value.getUTCDay()
    // US Eastern: UTC-4 (EDT) → US market 9:30-16:00 ET = 13:30-20:00 UTC
    const isWeekday = dow >= 1 && dow <= 5
    const isOpen = isWeekday && totalMin >= 810 && totalMin < 1200
    return isOpen ? 'open' : 'closed'
  })

  const cnStatus = computed(() => {
    // China Standard Time: UTC+8
    const chinaMs = now.value.getTime() + 8 * 3600 * 1000
    const chinaDate = new Date(chinaMs)
    const h = chinaDate.getUTCHours()
    const m = chinaDate.getUTCMinutes()
    const totalMin = h * 60 + m
    const dow = chinaDate.getUTCDay()
    const isWeekday = dow >= 1 && dow <= 5
    // A-share: 9:30-11:30, 13:00-15:00
    const morning = totalMin >= 570 && totalMin < 690
    const afternoon = totalMin >= 780 && totalMin < 900
    return isWeekday && (morning || afternoon) ? 'open' : 'closed'
  })

  return { now, timeStr, dateStr, usStatus, cnStatus }
}
