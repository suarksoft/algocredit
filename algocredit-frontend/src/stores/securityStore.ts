/**
 * Security Store for Web3 Security Firewall
 * Manages security state, API keys, and threat intelligence
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { securityAPI, SecurityDashboard, ThreatIntelligence, CreditScoreResponse } from '@/lib/security-api'

interface SecurityState {
  // API Key Management
  apiKey: string | null
  tier: 'free' | 'pro' | 'enterprise'
  isAuthenticated: boolean
  
  // Security Analytics
  securityScore: number
  threatLevel: number
  lastThreatCheck: number | null
  
  // Dashboard Data
  dashboard: SecurityDashboard | null
  threatIntel: Record<string, ThreatIntelligence>
  
  // Loading States
  isLoadingScore: boolean
  isLoadingThreat: boolean
  isLoadingDashboard: boolean
  
  // Error States
  lastError: string | null
  
  // Actions
  setApiKey: (apiKey: string, tier: string) => void
  generateApiKey: (userId: string, tier?: string) => Promise<string>
  getCreditScore: (walletAddress: string) => Promise<CreditScoreResponse>
  getThreatIntelligence: (walletAddress: string) => Promise<ThreatIntelligence>
  loadSecurityDashboard: (apiKey?: string) => Promise<SecurityDashboard>
  validateTransaction: (transactionData: any) => Promise<any>
  clearError: () => void
  reset: () => void
}

export const useSecurityStore = create<SecurityState>()(
  persist(
    (set, get) => ({
      // Initial state
      apiKey: null,
      tier: 'free',
      isAuthenticated: false,
      securityScore: 0,
      threatLevel: 0,
      lastThreatCheck: null,
      dashboard: null,
      threatIntel: {},
      isLoadingScore: false,
      isLoadingThreat: false,
      isLoadingDashboard: false,
      lastError: null,

      // Actions
      setApiKey: (apiKey: string, tier: string) => {
        set({
          apiKey,
          tier: tier as any,
          isAuthenticated: true,
          lastError: null
        })
      },

      generateApiKey: async (userId: string, tier: string = 'free') => {
        try {
          set({ lastError: null })
          
          const result = await securityAPI.generateApiKey(userId, tier)
          
          set({
            apiKey: result.api_key,
            tier: result.tier as any,
            isAuthenticated: true
          })
          
          return result.api_key
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to generate API key'
          set({ lastError: errorMessage })
          throw error
        }
      },

      getCreditScore: async (walletAddress: string): Promise<CreditScoreResponse> => {
        try {
          set({ isLoadingScore: true, lastError: null })
          
          const creditScore = await securityAPI.getCreditScore(walletAddress)
          
          // Update security metrics
          set({
            securityScore: creditScore.security_context?.threat_score || 0,
            threatLevel: creditScore.security_context?.threat_score || 0,
            lastThreatCheck: Date.now()
          })
          
          return creditScore
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to get credit score'
          set({ lastError: errorMessage })
          throw error
        } finally {
          set({ isLoadingScore: false })
        }
      },

      getThreatIntelligence: async (walletAddress: string): Promise<ThreatIntelligence> => {
        try {
          set({ isLoadingThreat: true, lastError: null })
          
          const threatIntel = await securityAPI.getThreatIntelligence(walletAddress)
          
          // Cache threat intelligence
          set(state => ({
            threatIntel: {
              ...state.threatIntel,
              [walletAddress]: threatIntel
            },
            lastThreatCheck: Date.now()
          }))
          
          return threatIntel
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to get threat intelligence'
          set({ lastError: errorMessage })
          throw error
        } finally {
          set({ isLoadingThreat: false })
        }
      },

      loadSecurityDashboard: async (apiKey?: string): Promise<SecurityDashboard> => {
        try {
          set({ isLoadingDashboard: true, lastError: null })
          
          const keyToUse = apiKey || get().apiKey
          if (!keyToUse) {
            throw new Error('No API key available')
          }
          
          const dashboard = await securityAPI.getSecurityDashboard(keyToUse)
          
          set({
            dashboard,
            securityScore: dashboard.security_score,
            threatLevel: dashboard.usage_statistics.threat_score
          })
          
          return dashboard
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to load security dashboard'
          set({ lastError: errorMessage })
          throw error
        } finally {
          set({ isLoadingDashboard: false })
        }
      },

      validateTransaction: async (transactionData: any) => {
        try {
          set({ lastError: null })
          
          const validation = await securityAPI.validateTransaction(transactionData)
          
          // Update threat level based on validation
          if (validation.validation_result?.risk_score) {
            set({ threatLevel: validation.validation_result.risk_score })
          }
          
          return validation
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Transaction validation failed'
          set({ lastError: errorMessage })
          throw error
        }
      },

      clearError: () => {
        set({ lastError: null })
      },

      reset: () => {
        set({
          apiKey: null,
          tier: 'free',
          isAuthenticated: false,
          securityScore: 0,
          threatLevel: 0,
          lastThreatCheck: null,
          dashboard: null,
          threatIntel: {},
          isLoadingScore: false,
          isLoadingThreat: false,
          isLoadingDashboard: false,
          lastError: null
        })
      }
    }),
    {
      name: 'algocredit-security-store',
      partialize: (state) => ({
        apiKey: state.apiKey,
        tier: state.tier,
        isAuthenticated: state.isAuthenticated,
        securityScore: state.securityScore,
        threatLevel: state.threatLevel
      })
    }
  )
)

// Helper hooks
export const useSecurityAuth = () => {
  const { apiKey, tier, isAuthenticated, setApiKey, generateApiKey, reset } = useSecurityStore()
  return { apiKey, tier, isAuthenticated, setApiKey, generateApiKey, reset }
}

export const useSecurityAnalytics = () => {
  const { 
    securityScore, 
    threatLevel, 
    dashboard, 
    isLoadingDashboard, 
    loadSecurityDashboard 
  } = useSecurityStore()
  
  return { 
    securityScore, 
    threatLevel, 
    dashboard, 
    isLoadingDashboard, 
    loadSecurityDashboard 
  }
}

export const useThreatIntelligence = () => {
  const { 
    threatIntel, 
    isLoadingThreat, 
    getThreatIntelligence 
  } = useSecurityStore()
  
  return { 
    threatIntel, 
    isLoadingThreat, 
    getThreatIntelligence 
  }
}
