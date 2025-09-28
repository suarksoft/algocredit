'use client'

import { useState, useEffect } from 'react'
import { ShieldCheckIcon, ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

interface RiskAnalysis {
  wallet_address: string
  ai_risk_score: number
  risk_level: string
  risk_color: string
  credit_score: number
  recommendation: string
  confidence: number
  analysis_timestamp: number
  risk_factors: {
    transaction_frequency: number
    wallet_age: number
    balance_stability: number
    network_activity: number
    reputation_score: number
  }
  analysis_details: {
    wallet_analysis: {
      address: string
      first_seen: string
      total_transactions: number
      unique_contracts: number
    }
    risk_indicators: {
      suspicious_patterns: number
      high_frequency_trading: boolean
      unusual_contract_interactions: number
    }
    positive_indicators: {
      consistent_activity: boolean
      diverse_portfolio: boolean
      long_term_holding: boolean
    }
  }
  ai_model_version: string
  processing_time_ms: number
}

interface AIRiskCalculatorProps {
  onAnalysisComplete?: (analysis: RiskAnalysis) => void
}

export default function AIRiskCalculator({ onAnalysisComplete }: AIRiskCalculatorProps) {
  const [walletAddress, setWalletAddress] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<RiskAnalysis | null>(null)
  const [error, setError] = useState('')

  const analyzeWallet = async () => {
    if (!walletAddress.trim()) {
      setError('Please enter a wallet address')
      return
    }

    setIsAnalyzing(true)
    setError('')
    setAnalysis(null)

    try {
      const response = await fetch('http://localhost:8001/api/v1/credit/ai-risk-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ wallet_address: walletAddress })
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const result = await response.json()
      setAnalysis(result)
      onAnalysisComplete?.(result)
    } catch (err) {
      setError('Failed to analyze wallet. Please try again.')
      console.error('AI Risk Analysis Error:', err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />
      case 'MEDIUM':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
      case 'HIGH':
        return <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
      default:
        return <ShieldCheckIcon className="h-6 w-6 text-gray-500" />
    }
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'HIGH':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* AI Risk Calculator Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-blue-100 rounded-full mr-4">
            <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI Risk Analysis
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Advanced AI-powered wallet risk assessment
            </p>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Wallet Address
            </label>
            <input
              type="text"
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              placeholder="Enter Algorand wallet address..."
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={analyzeWallet}
              disabled={isAnalyzing || !walletAddress.trim()}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <ShieldCheckIcon className="h-4 w-4" />
                  Analyze Risk
                </>
              )}
            </button>
          </div>
        </div>
        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Risk Score Overview */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Risk Assessment
              </h3>
              <div className="flex items-center gap-2">
                {getRiskIcon(analysis.risk_level)}
                <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(analysis.risk_level)}`}>
                  {analysis.risk_level} RISK
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {analysis.ai_risk_score}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  AI Risk Score
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      analysis.risk_level === 'LOW' ? 'bg-green-500' :
                      analysis.risk_level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${analysis.ai_risk_score}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {analysis.credit_score}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  Credit Score
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  (300-850 scale)
                </div>
              </div>

              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {Math.round(analysis.confidence * 100)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  AI Confidence
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Model v{analysis.ai_model_version}
                </div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-gray-700 dark:text-gray-300 font-medium">
                {analysis.recommendation}
              </p>
            </div>
          </div>

          {/* Risk Factors */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Risk Factor Analysis
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(analysis.risk_factors).map(([factor, score]) => (
                <div key={factor} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {factor.replace('_', ' ')}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: `${score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-400 w-8">
                      {Math.round(score * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Wallet Analysis Details */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Wallet Analysis
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">Activity Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">First Seen</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {analysis.analysis_details.wallet_analysis.first_seen}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Total Transactions</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {analysis.analysis_details.wallet_analysis.total_transactions.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Unique Contracts</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {analysis.analysis_details.wallet_analysis.unique_contracts}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">Risk Indicators</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Suspicious Patterns</span>
                    <span className={`text-sm font-medium ${
                      analysis.analysis_details.risk_indicators.suspicious_patterns > 0 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {analysis.analysis_details.risk_indicators.suspicious_patterns}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">High Frequency Trading</span>
                    <span className={`text-sm font-medium ${
                      analysis.analysis_details.risk_indicators.high_frequency_trading ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {analysis.analysis_details.risk_indicators.high_frequency_trading ? 'Yes' : 'No'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Unusual Interactions</span>
                    <span className={`text-sm font-medium ${
                      analysis.analysis_details.risk_indicators.unusual_contract_interactions > 0 ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {analysis.analysis_details.risk_indicators.unusual_contract_interactions}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Positive Indicators */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Positive Indicators
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(analysis.analysis_details.positive_indicators).map(([indicator, value]) => (
                <div key={indicator} className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${
                    value ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    {value ? (
                      <CheckCircleIcon className="h-5 w-5" />
                    ) : (
                      <ExclamationTriangleIcon className="h-5 w-5" />
                    )}
                  </div>
                  <span className={`text-sm font-medium ${
                    value ? 'text-green-700 dark:text-green-400' : 'text-gray-500'
                  }`}>
                    {indicator.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
