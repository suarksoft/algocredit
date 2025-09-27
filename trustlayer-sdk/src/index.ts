/**
 * TrustLayer Algorand Security SDK
 * Open Source Web3 Security APIs
 * 
 * @packageDocumentation
 */

import algosdk from 'algosdk'

export interface TrustLayerConfig {
  network?: 'testnet' | 'mainnet'
  apiKey?: string
  algorandNode?: string
  indexerNode?: string
}

export interface TrustScore {
  wallet_address: string
  trust_score: number
  risk_level: 'low' | 'medium' | 'high'
  confidence: number
  on_chain_analysis: OnChainAnalysis
  off_chain_analysis: OffChainAnalysis
  timestamp: string
}

export interface OnChainAnalysis {
  score: number
  factors: {
    wallet_age_days: number
    transaction_count: number
    avg_transaction_size: number
    defi_interactions: number
    nft_holdings: number
    governance_participation: number
  }
}

export interface OffChainAnalysis {
  score: number
  factors: {
    social_media_score: number
    github_activity: number
    business_verification: boolean
    kyc_status: string
  }
}

export interface FraudCheck {
  wallet_address: string
  fraud_score: number
  risk_level: 'low' | 'medium' | 'high'
  recommendation: string
  fraud_indicators: {
    mixer_usage: boolean
    rapid_transactions: boolean
    suspicious_patterns: boolean
    blacklist_connections: boolean
    sybil_attack_risk: boolean
  }
  confidence: number
  timestamp: string
}

/**
 * Main TrustLayer SDK Class
 * 
 * @example
 * ```typescript
 * import { TrustLayer } from '@trustlayer/algorand-security'
 * 
 * const trustLayer = new TrustLayer({
 *   network: 'testnet',
 *   apiKey: 'your_api_key' // Optional for open source features
 * })
 * 
 * // Get trust score (open source)
 * const score = await trustLayer.getTrustScore(walletAddress)
 * 
 * // Check fraud risk (open source)  
 * const fraudCheck = await trustLayer.checkFraud(walletAddress)
 * ```
 */
export class TrustLayer {
  private config: TrustLayerConfig
  private algodClient: algosdk.Algodv2
  private indexerClient: algosdk.Indexer
  private apiBaseUrl: string

  constructor(config: TrustLayerConfig = {}) {
    this.config = {
      network: 'testnet',
      algorandNode: 'https://testnet-api.algonode.cloud',
      indexerNode: 'https://testnet-idx.algonode.cloud',
      ...config
    }

    // Initialize Algorand clients
    this.algodClient = new algosdk.Algodv2('', this.config.algorandNode!, '')
    this.indexerClient = new algosdk.Indexer('', this.config.indexerNode!, '')
    
    // API base URL
    this.apiBaseUrl = config.network === 'mainnet' 
      ? 'https://api.trustlayer.io' 
      : 'http://localhost:8003'
  }

  /**
   * Get AI-powered trust score for a wallet address
   * 
   * @param walletAddress - Algorand wallet address
   * @param options - Additional options
   * @returns Trust score analysis
   * 
   * @example
   * ```typescript
   * const score = await trustLayer.getTrustScore('WALLET_ADDRESS_HERE')
   * console.log(`Trust Score: ${score.trust_score}/850`)
   * ```
   */
  async getTrustScore(
    walletAddress: string, 
    options: { includeHistory?: boolean } = {}
  ): Promise<TrustScore> {
    const response = await this.makeApiCall('/api/trust/score', {
      wallet_address: walletAddress,
      blockchain: 'algorand',
      include_history: options.includeHistory || false
    })

    return response
  }

  /**
   * Check fraud risk for wallet address
   * 
   * @param walletAddress - Algorand wallet address
   * @param transactionData - Optional transaction data for analysis
   * @returns Fraud risk analysis
   */
  async checkFraud(
    walletAddress: string,
    transactionData?: { hash?: string; amount?: number }
  ): Promise<FraudCheck> {
    const response = await this.makeApiCall('/api/fraud/check', {
      wallet_address: walletAddress,
      transaction_hash: transactionData?.hash,
      amount: transactionData?.amount
    })

    return response
  }

  /**
   * Analyze wallet using Algorand-specific on-chain data
   * This is the open source core functionality
   * 
   * @param walletAddress - Algorand wallet address
   * @returns On-chain analysis
   */
  async analyzeAlgorandWallet(walletAddress: string): Promise<OnChainAnalysis> {
    try {
      // Get account info
      const accountInfo = await this.algodClient.accountInformation(walletAddress).do()
      
      // Get transaction history
      const txnHistory = await this.indexerClient
        .lookupAccountTransactions(walletAddress)
        .limit(1000)
        .do()

      // Analyze on-chain data
      const analysis = this.calculateOnChainFactors(accountInfo, txnHistory)
      
      return {
        score: this.calculateOnChainScore(analysis),
        factors: analysis
      }
    } catch (error) {
      throw new Error(`Failed to analyze Algorand wallet: ${error}`)
    }
  }

  /**
   * Get comprehensive security profile (open source)
   * 
   * @param walletAddress - Algorand wallet address
   * @returns Complete security profile
   */
  async getSecurityProfile(walletAddress: string) {
    const [trustScore, fraudCheck, onChainAnalysis] = await Promise.all([
      this.getTrustScore(walletAddress),
      this.checkFraud(walletAddress),
      this.analyzeAlgorandWallet(walletAddress)
    ])

    return {
      wallet_address: walletAddress,
      trust_score: trustScore,
      fraud_check: fraudCheck,
      on_chain_analysis: onChainAnalysis,
      security_grade: this.calculateSecurityGrade(trustScore, fraudCheck),
      recommendations: this.generateRecommendations(trustScore, fraudCheck),
      timestamp: new Date().toISOString()
    }
  }

  // Private helper methods
  private async makeApiCall(endpoint: string, data: any): Promise<any> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`
    }

    const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  private calculateOnChainFactors(accountInfo: any, txnHistory: any) {
    // Open source on-chain analysis algorithms
    const transactions = txnHistory.transactions || []
    
    return {
      wallet_age_days: this.calculateWalletAge(transactions),
      transaction_count: transactions.length,
      avg_transaction_size: this.calculateAvgTxnSize(transactions),
      defi_interactions: this.countDefiInteractions(transactions),
      nft_holdings: accountInfo.assets?.length || 0,
      governance_participation: this.checkGovernanceParticipation(transactions)
    }
  }

  private calculateOnChainScore(factors: any): number {
    // Open source scoring algorithm
    let score = 300 // Base score

    // Wallet age bonus
    score += Math.min(100, factors.wallet_age_days / 10)
    
    // Transaction count bonus
    score += Math.min(100, factors.transaction_count / 100)
    
    // DeFi interaction bonus
    score += Math.min(150, factors.defi_interactions * 10)
    
    // Governance bonus
    score += Math.min(100, factors.governance_participation * 20)

    return Math.min(850, score)
  }

  private calculateWalletAge(transactions: any[]): number {
    if (transactions.length === 0) return 0
    
    const oldestTxn = transactions[transactions.length - 1]
    const creationTime = oldestTxn['round-time'] || 0
    const currentTime = Math.floor(Date.now() / 1000)
    
    return Math.floor((currentTime - creationTime) / (24 * 60 * 60))
  }

  private calculateAvgTxnSize(transactions: any[]): number {
    if (transactions.length === 0) return 0
    
    const totalAmount = transactions.reduce((sum, txn) => {
      return sum + (txn['payment-transaction']?.amount || 0)
    }, 0)
    
    return totalAmount / transactions.length / 1000000 // Convert to ALGO
  }

  private countDefiInteractions(transactions: any[]): number {
    // Count interactions with known DeFi applications
    const defiAppIds = [465818260, 552635992, 724480511] // Known Algorand DeFi apps
    
    return transactions.filter(txn => 
      txn['application-transaction'] && 
      defiAppIds.includes(txn['application-transaction']['application-id'])
    ).length
  }

  private checkGovernanceParticipation(transactions: any[]): number {
    // Check for governance participation transactions
    return transactions.filter(txn => 
      txn.note && 
      Buffer.from(txn.note, 'base64').toString().includes('governance')
    ).length
  }

  private calculateSecurityGrade(trustScore: TrustScore, fraudCheck: FraudCheck): string {
    const combinedScore = (trustScore.trust_score * 0.7) + ((100 - fraudCheck.fraud_score) * 0.3 * 8.5)
    
    if (combinedScore >= 750) return 'A+'
    if (combinedScore >= 700) return 'A'
    if (combinedScore >= 650) return 'B+'
    if (combinedScore >= 600) return 'B'
    if (combinedScore >= 550) return 'C+'
    return 'C'
  }

  private generateRecommendations(trustScore: TrustScore, fraudCheck: FraudCheck): string[] {
    const recommendations = []

    if (trustScore.trust_score < 650) {
      recommendations.push("Increase wallet activity to improve trust score")
    }

    if (fraudCheck.fraud_score > 30) {
      recommendations.push("Review transaction patterns for suspicious activity")
    }

    if (trustScore.on_chain_analysis.factors.defi_interactions < 5) {
      recommendations.push("Engage with DeFi protocols to build reputation")
    }

    if (trustScore.on_chain_analysis.factors.governance_participation === 0) {
      recommendations.push("Participate in Algorand governance to boost score")
    }

    return recommendations
  }
}

// Export types and main class
export default TrustLayer
export * from './types'
