import axios from 'axios'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL || 'https://quant-trading-production-c80d.up.railway.app') + '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// ─── Market / Watchlist ────────────────────────────────────────────────────

export const marketApi = {
  /** GET /api/watchlist */
  getWatchlist: (): Promise<WatchlistItem[]> =>
    api.get('/watchlist'),

  /** POST /api/watchlist { symbol } */
  addSymbol: (symbol: string): Promise<{ success: boolean }> =>
    api.post('/watchlist', { symbol }),

  /** DELETE /api/watchlist/:symbol */
  removeSymbol: (symbol: string): Promise<{ success: boolean }> =>
    api.delete(`/watchlist/${symbol}`),

  /** POST /api/quotes/batch */
  getQuotes: (symbols: string[], watchlist: WatchlistItem[] = []): Promise<QuoteData[]> => {
    const items = watchlist.length
      ? watchlist
      : symbols.map(s => ({ symbol: s }))
    return api.post('/quotes/batch', { symbols: items })
  },

  /** No market-sentiment endpoint — derive from quotes */
  getSentiment: (): Promise<MarketSentiment> =>
    Promise.reject(new Error('no market-sentiment endpoint')),

  /** GET /api/kline/:symbol?interval=1d&limit=200 */
  getKline: (symbol: string, interval = '1d', limit = 200): Promise<KlineData[]> =>
    api.get(`/kline/${symbol}`, { params: { interval, limit } }),
}

// ─── Signals ──────────────────────────────────────────────────────────────

export const signalApi = {
  /** GET /api/signals */
  getSignals: (): Promise<Signal[]> =>
    api.get('/signals'),

  /** POST /api/signals/scan — longer timeout for multi-symbol scan */
  scanSignals: (): Promise<Signal[]> =>
    api.post('/signals/scan', {}, { timeout: 120000 }),
}

// ─── Portfolio ────────────────────────────────────────────────────────────

export const portfolioApi = {
  /** GET /api/portfolio */
  getPortfolio: (): Promise<Position[]> =>
    (api.get('/portfolio') as unknown as Promise<any[]>).then((rows: any[]) =>
      rows.map(r => ({
        id: r.id,
        symbol: r.symbol,
        name: r.symbol,
        market: (r.market || 'us').toUpperCase() as 'US' | 'CN',
        buyPrice: r.buy_price,
        currentPrice: r.current_price ?? r.buy_price,
        quantity: r.quantity,
        stopLoss: r.stop_loss,
        takeProfit: r.take_profit,
        buyDate: r.buy_date,
        notes: r.note,
      }))
    ),

  /** POST /api/portfolio */
  addPosition: (position: CreatePositionDto): Promise<Position> =>
    api.post('/portfolio', {
      symbol: position.symbol,
      market: position.market.toLowerCase(),
      buy_price: position.buyPrice,
      quantity: position.quantity,
      buy_date: position.buyDate,
      stop_loss: position.stopLoss,
      take_profit: position.takeProfit,
      note: position.notes,
    }),

  /** PUT /api/portfolio/:id */
  updatePosition: (id: string, data: Partial<Position>): Promise<Position> =>
    api.put(`/portfolio/${id}`, data),

  /** DELETE /api/portfolio/:id */
  deletePosition: (id: string): Promise<{ success: boolean }> =>
    api.delete(`/portfolio/${id}`),
}

// ─── Settings ─────────────────────────────────────────────────────────────

export const settingsApi = {
  /** GET /api/settings */
  getSettings: (): Promise<AppSettings> =>
    api.get('/settings'),

  /** PUT /api/settings */
  updateSettings: (settings: Partial<AppSettings>): Promise<AppSettings> =>
    api.put('/settings', settings),
}

// ─── Types ────────────────────────────────────────────────────────────────

export interface WatchlistItem {
  symbol: string
  name: string
  market: 'US' | 'CN'
}

export interface QuoteData {
  symbol: string
  name?: string
  market: string
  price: number
  change?: number
  change_pct?: number      // from backend
  changePercent?: number   // alias
  volume?: number
  ema20?: number
  ema60?: number
  rsi14?: number
  macd?: number
  signal_line?: number
  atr14?: number
  bb_upper?: number
  bb_lower?: number
  signal?: SignalType
  cached?: boolean
}

export interface MarketSentiment {
  vix: number
  vixChange: number
  indices: SentimentIndex[]
}

export interface SentimentIndex {
  symbol: string
  name: string
  price: number
  changePercent: number
}

export interface KlineData {
  time: number  // unix timestamp
  open: number
  high: number
  low: number
  close: number
  volume: number
  ema20?: number
  ema60?: number
  rsi14?: number
  signal?: SignalType
}

export type SignalType = 'BUY' | 'SELL' | 'OVERSOLD' | 'OVERBOUGHT'

export interface Signal {
  id: string | number
  created_at: string   // ISO string from backend
  time?: string        // alias, computed in store
  symbol: string
  name?: string
  market?: string
  signal_type: SignalType
  type?: SignalType     // alias
  price: number
  strategy: string
  description?: string
  is_triggered?: boolean
}

export interface Position {
  id: string
  symbol: string
  name: string
  market: 'US' | 'CN'
  buyPrice: number
  currentPrice: number
  quantity: number
  stopLoss?: number
  takeProfit?: number
  buyDate: string
  notes?: string
}

export interface CreatePositionDto {
  symbol: string
  name: string
  market: 'US' | 'CN'
  buyPrice: number
  quantity: number
  stopLoss?: number
  takeProfit?: number
  buyDate: string
  notes?: string
}

export interface AppSettings {
  apiKey: string
  ema20Period: number
  ema60Period: number
  rsiBuyThreshold: number
  rsiSellThreshold: number
  watchlist: string[]
}

export default api
