/**
 * Format a number with thousands separators and fixed decimals.
 * e.g. 1234567.8 → "1,234,567.80"
 */
export function formatNumber(value: number, decimals = 2): string {
  if (isNaN(value) || value === null || value === undefined) return '—'
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

/**
 * Format a price change percent with leading + for positives.
 * e.g. 1.234 → "+1.23%"  |  -3.456 → "-3.46%"
 */
export function formatChangePercent(value: number): string {
  if (isNaN(value)) return '—'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

/**
 * Format a price change (absolute) with sign.
 */
export function formatChange(value: number, decimals = 2): string {
  if (isNaN(value)) return '—'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${formatNumber(value, decimals)}`
}

/**
 * Format volume: if >= 1M show "1.23M", if >= 1K show "123K"
 */
export function formatVolume(value: number): string {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B`
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`
  return value.toString()
}

/**
 * Return CSS class for positive/negative value.
 */
export function changeClass(value: number): string {
  if (value > 0) return 'num-positive'
  if (value < 0) return 'num-negative'
  return 'num-neutral'
}

/**
 * Format unix timestamp or date string to "MM-DD HH:mm"
 */
export function formatTime(value: string | number, full = false): string {
  const d = typeof value === 'number' ? new Date(value * 1000) : new Date(value)
  if (full) {
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

/**
 * Format PnL value with currency
 */
export function formatPnL(value: number, currency = '$'): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${currency}${formatNumber(Math.abs(value))}`
}

/**
 * Get display symbol for a stock (strip exchange suffix for US stocks)
 */
export function displaySymbol(symbol: string): string {
  return symbol
}

/**
 * Get exchange badge text
 */
export function exchangeBadge(symbol: string): string {
  if (symbol.endsWith('.SH')) return 'SH'
  if (symbol.endsWith('.SZ')) return 'SZ'
  return 'US'
}
