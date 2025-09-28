/**
 * AlgoCredit Web3 Security Firewall API Client
 * Enterprise-grade security integration for frontend
 */

export interface SecurityConfig {
  apiKey: string
  baseUrl: string
  tier: 'free' | 'pro' | 'enterprise'
}

export interface CreditScoreResponse {
  wallet_address: string
  credit_score: number
  confidence: number
  risk_level: 'low' | 'medium' | 'high'
  max_loan_amount: number
  recommended_interest_rate: number
  insights: string[]
  assessment_breakdown: {
    on_chain_score: number
    stability_score: number
    activity_score: number
    diversity_score: number
    defi_score: number
  }
  wallet_metrics: {
    account_age_days: number
    total_transactions: number
    current_balance_algo: number
    total_volume_algo: number
  }
  model_info: {
    model_version: string
    scoring_method: string
    ai_enabled: boolean
    assessment_timestamp: string
  }
  security_context: {
    api_key_tier: string
    threat_score: number
    validation_timestamp: number
  }
}

export interface ThreatIntelligence {
  wallet_address: string
  risk_profile: {
    risk_level: string
    avg_risk_score: number
    validation_count: number
    malicious_count: number
  }
  threat_summary: {
    total_threats: number
    threats_by_type: Record<string, number>
  }
  security_recommendations: string[]
}

export interface ValidationResult {
  security_status: string
  api_key_tier: string
  threat_score: number
  validation_result: {
    result: 'valid' | 'suspicious' | 'malicious' | 'invalid'
    risk_score: number
    issues: string[]
    recommendations: string[]
  }
}

export interface SecurityDashboard {
  api_key: string
  tier: string
  usage_statistics: {
    usage_count: number
    last_used: string
    threat_score: number
    status: string
  }
  threat_analytics: {
    total_threats: number
    threats_by_type: Record<string, number>
  }
  rate_limit_status: {
    tokens: number
    status: string
  }
  security_score: number
}

class AlgoCreditSecurityAPI {
  private config: SecurityConfig
  private baseHeaders: Record<string, string>

  constructor(config: SecurityConfig) {
    this.config = config
    this.baseHeaders = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`,
      'X-API-Version': 'v1',
      'X-Client': 'AlgoCredit-Frontend'
    }
  }

  /**
   * Generate wallet-based API key
   */
  async generateWalletApiKey(walletAddress: string, tier: string = 'free'): Promise<{
    api_key: string
    tier: string
    wallet_address: string
    status: 'new' | 'existing'
    usage_instructions: any
  }> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/security/generate-key?wallet_address=${walletAddress}&tier=${tier}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Failed to generate API key: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error generating wallet API key:', error)
      throw error
    }
  }

  /**
   * Get existing API key for wallet
   */
  async getWalletApiKey(walletAddress: string): Promise<{
    wallet_address: string
    has_api_key: boolean
    api_key?: string
    usage_stats?: any
  }> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/security/wallet-key/${walletAddress}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to get wallet API key: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting wallet API key:', error)
      throw error
    }
  }

  /**
   * Get AI-powered credit score with security validation
   */
  async getCreditScore(walletAddress: string): Promise<CreditScoreResponse> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/credit/score?wallet_address=${walletAddress}`, {
        method: 'POST',
        headers: this.baseHeaders
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Credit scoring failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting credit score:', error)
      throw error
    }
  }

  /**
   * Validate transaction for security threats
   */
  async validateTransaction(transactionData: any): Promise<ValidationResult> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/security/validate-transaction`, {
        method: 'POST',
        headers: this.baseHeaders,
        body: JSON.stringify(transactionData)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Transaction validation failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error validating transaction:', error)
      throw error
    }
  }

  /**
   * Get threat intelligence for wallet
   */
  async getThreatIntelligence(walletAddress: string): Promise<ThreatIntelligence> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/security/threat-intel/${walletAddress}`, {
        method: 'GET',
        headers: this.baseHeaders
      })

      if (!response.ok) {
        throw new Error(`Failed to get threat intelligence: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting threat intelligence:', error)
      throw error
    }
  }

  /**
   * Generate API key for wallet
   */
  async generateApiKey(walletAddress: string, tier: string = 'pro'): Promise<{
    api_key: string
    tier: string
    usage_instructions: any
  }> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/security/generate-key?wallet_address=${walletAddress}&tier=${tier}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Failed to generate API key: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error generating API key:', error)
      throw error
    }
  }

  /**
   * Get security dashboard analytics
   */
  async getSecurityDashboard(apiKey: string, hours: number = 24): Promise<SecurityDashboard> {
    try {
      // Create headers with the specific API key for this request
      const dashboardHeaders = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'X-API-Key': apiKey,
        'X-API-Version': 'v1',
        'X-Client': 'AlgoCredit-Frontend'
      }

      const response = await fetch(`${this.config.baseUrl}/api/v1/security/dashboard/${apiKey}?hours=${hours}`, {
        method: 'GET',
        headers: dashboardHeaders
      })

      if (!response.ok) {
        throw new Error(`Failed to get security dashboard: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting security dashboard:', error)
      throw error
    }
  }

  /**
   * Submit loan application with security validation
   */
  async submitLoanApplication(applicationData: any): Promise<any> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/loans/apply`, {
        method: 'POST',
        headers: this.baseHeaders,
        body: JSON.stringify(applicationData)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Loan application failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error submitting loan application:', error)
      throw error
    }
  }

  /**
   * Check security system health
   */
  async getSystemHealth(): Promise<{
    status: string
    redis_status: string
    firewall_version: string
  }> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/security/health`, {
        method: 'GET',
        headers: this.baseHeaders
      })

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error checking system health:', error)
      throw error
    }
  }

  /**
   * Handle API errors with user-friendly messages
   */
  private handleApiError(error: any): string {
    if (error.message.includes('429')) {
      return 'Rate limit exceeded. Please wait a moment and try again.'
    }
    if (error.message.includes('401')) {
      return 'Invalid API key. Please check your credentials.'
    }
    if (error.message.includes('403')) {
      return 'Transaction blocked by security system for your protection.'
    }
    if (error.message.includes('500')) {
      return 'Security system temporarily unavailable. Please try again later.'
    }
    return error.message || 'An unexpected error occurred.'
  }
}

// Export singleton instance
export const securityAPI = new AlgoCreditSecurityAPI({
  apiKey: process.env.NEXT_PUBLIC_ALGOCREDIT_API_KEY || 'ac_live_915aa39a909e88d18f71c400bad2cfb0',
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  tier: 'pro'
})

// Export class for custom instances
export { AlgoCreditSecurityAPI }
