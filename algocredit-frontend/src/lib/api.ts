/**
 * Optimized API Client with Caching
 * 24-Hour Sprint Performance Enhancement
 */

interface CacheItem {
  data: any
  timestamp: number
  ttl: number
}

class OptimizedApiClient {
  private baseUrl: string
  private cache: Map<string, CacheItem> = new Map()
  private defaultTTL: number = 30000 // 30 seconds

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl
    
    // Clean expired cache every minute
    setInterval(() => this.cleanExpiredCache(), 60000)
  }

  private getCacheKey(endpoint: string, params?: any): string {
    const paramStr = params ? JSON.stringify(params) : ''
    return `${endpoint}:${paramStr}`
  }

  private isValidCache(item: CacheItem): boolean {
    return Date.now() - item.timestamp < item.ttl
  }

  private cleanExpiredCache(): void {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp >= item.ttl) {
        this.cache.delete(key)
      }
    }
  }

  private setCache(key: string, data: any, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    })
  }

  private getCache(key: string): any | null {
    const item = this.cache.get(key)
    if (item && this.isValidCache(item)) {
      return item.data
    }
    if (item) {
      this.cache.delete(key) // Remove expired
    }
    return null
  }

  async get(endpoint: string, options?: { cache?: boolean, ttl?: number }): Promise<any> {
    const cacheKey = this.getCacheKey(endpoint)
    
    // Check cache first
    if (options?.cache !== false) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        return { ...cached, cached: true }
      }
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Cache successful responses
      if (options?.cache !== false) {
        this.setCache(cacheKey, data, options?.ttl)
      }

      return { ...data, cached: false }
    } catch (error) {
      console.error(`API GET ${endpoint} failed:`, error)
      throw error
    }
  }

  async post(endpoint: string, body: any, options?: { invalidateCache?: string[] }): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      // Invalidate related caches
      if (options?.invalidateCache) {
        options.invalidateCache.forEach(pattern => {
          for (const key of this.cache.keys()) {
            if (key.includes(pattern)) {
              this.cache.delete(key)
            }
          }
        })
      }

      return data
    } catch (error) {
      console.error(`API POST ${endpoint} failed:`, error)
      throw error
    }
  }

  // Marketplace-specific methods
  async getMarketplaceStats() {
    return this.get('/marketplace/stats', { cache: true, ttl: 10000 }) // 10s cache
  }

  async getAvailableStartups() {
    return this.get('/startup/available', { cache: true, ttl: 15000 }) // 15s cache
  }

  async registerInvestor(data: any) {
    return this.post('/investor/register', data, { 
      invalidateCache: ['marketplace_stats'] 
    })
  }

  async registerStartup(data: any) {
    return this.post('/startup/register', data, { 
      invalidateCache: ['marketplace_stats', 'startup/available'] 
    })
  }

  async userLogin(data: any) {
    return this.get(`/user/login?wallet=${data.wallet_address}&type=${data.user_type}`, { 
      cache: true, 
      ttl: 60000 // 1 minute cache for user data
    })
  }

  async investorDeposit(data: any) {
    return this.post('/investor/deposit', data, { 
      invalidateCache: ['marketplace_stats', `investor_${data.investor_id}`] 
    })
  }

  async executeFunding(data: any) {
    return this.post('/funding/execute', data, { 
      invalidateCache: ['marketplace_stats', 'startup/available', `investor_${data.investor_id}`] 
    })
  }

  async getInvestorPortfolio(investorId: number) {
    return this.get(`/investor/${investorId}/portfolio`, { 
      cache: true, 
      ttl: 20000 // 20s cache
    })
  }

  async getStartupDetails(startupId: number) {
    return this.get(`/startup/${startupId}/details`, { 
      cache: true, 
      ttl: 30000 // 30s cache
    })
  }

  // Cache management
  clearCache(): void {
    this.cache.clear()
  }

  getCacheSize(): number {
    return this.cache.size
  }
}

// Export singleton instance
export const apiClient = new OptimizedApiClient()

// Export types
export type { CacheItem }
