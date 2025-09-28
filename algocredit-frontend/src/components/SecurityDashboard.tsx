/**
 * Security Dashboard Component
 * Enterprise-grade security monitoring and analytics
 */

'use client'

import { useEffect, useState } from 'react'
import { useSecurityStore } from '@/stores/securityStore'
import { Button } from '@/components/Button'
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  ChartBarIcon,
  KeyIcon,
  ClockIcon,
  EyeIcon,
  BoltIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentDuplicateIcon,
  PlusIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline'

interface SecurityDashboardProps {
  apiKey?: string
  compact?: boolean
}

export function SecurityDashboard({ apiKey, compact = false }: SecurityDashboardProps) {
  const { 
    securityScore, 
    threatLevel, 
    dashboard, 
    isLoadingDashboard, 
    loadSecurityDashboard,
    lastError 
  } = useSecurityStore()

  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKeyVisible, setApiKeyVisible] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)

  useEffect(() => {
    // Load dashboard data on mount
    if (apiKey || dashboard) {
      loadSecurityDashboard(apiKey)
    }

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      if (apiKey || dashboard) {
        loadSecurityDashboard(apiKey)
      }
    }, 30000)

    setRefreshInterval(interval)

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [apiKey])

  // API Key Management Functions
  const generateNewApiKey = async () => {
    setIsGeneratingKey(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/security/generate-key?wallet_address=C57BAHYM3QSQZWYOWB5HMNJUSBFCIZTNEK6JZX3VL2NDZ3UQ5HPOINCABU`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        // Update local apiKey - you might want to update this via your store
        console.log('New API key generated:', data)
        // Refresh dashboard
        loadSecurityDashboard(data.api_key)
      } else {
        throw new Error('Failed to generate API key')
      }
    } catch (error) {
      console.error('API key generation failed:', error)
    } finally {
      setIsGeneratingKey(false)
    }
  }

  const copyApiKey = async () => {
    if (apiKey) {
      try {
        await navigator.clipboard.writeText(apiKey)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
      } catch (error) {
        console.error('Failed to copy API key:', error)
      }
    }
  }

  if (isLoadingDashboard && !dashboard) {
    return (
      <div className="animate-pulse">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    )
  }

  if (lastError) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
        <div className="flex items-center">
          <XCircleIcon className="h-5 w-5 text-red-500 mr-2" />
          <span className="text-red-700 dark:text-red-300">Security Dashboard Error: {lastError}</span>
        </div>
      </div>
    )
  }

  // Use mock data if no real dashboard data (for demo purposes)
  const mockDashboard = {
    api_key: apiKey?.slice(0, 20) + '...' || 'ac_live_demo...',
    tier: 'pro',
    usage_statistics: {
      usage_count: 247,
      last_used: new Date().toISOString(),
      threat_score: 1.2,
      status: 'active'
    },
    threat_analytics: {
      total_threats: 3,
      threats_by_type: {
        'replay_attack': 1,
        'suspicious_pattern': 2
      }
    },
    rate_limit_status: {
      tokens: 285,
      status: 'active'
    },
    security_score: 8.8,
    generated_at: Date.now() / 1000
  }

  const displayDashboard = dashboard || mockDashboard

  if (!displayDashboard) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 text-center">
        <ShieldCheckIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600 dark:text-gray-400">No security data available</p>
      </div>
    )
  }

  const getSecurityScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 dark:text-green-400'
    if (score >= 6) return 'text-yellow-600 dark:text-yellow-400'
    if (score >= 4) return 'text-orange-600 dark:text-orange-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getThreatLevelBadge = (level: number) => {
    if (level <= 2) return { color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', text: 'Low' }
    if (level <= 5) return { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', text: 'Medium' }
    if (level <= 8) return { color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200', text: 'High' }
    return { color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200', text: 'Critical' }
  }

  const currentSecurityScore = displayDashboard.security_score || securityScore
  const currentThreatLevel = displayDashboard.usage_statistics.threat_score || threatLevel
  const threatBadge = getThreatLevelBadge(currentThreatLevel)

  if (compact) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ShieldCheckIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Security Score</p>
              <p className={`text-lg font-bold ${getSecurityScoreColor(currentSecurityScore)}`}>
                {currentSecurityScore.toFixed(1)}/10
              </p>
            </div>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${threatBadge.color}`}>
            {threatBadge.text}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Web3 Security Dashboard
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Real-time security monitoring and threat analysis
              </p>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${threatBadge.color}`}>
            Threat Level: {threatBadge.text}
          </div>
        </div>

        {/* Security Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Security Score */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700 dark:text-green-300">Security Score</p>
                <p className={`text-2xl font-bold ${getSecurityScoreColor(currentSecurityScore)}`}>
                  {currentSecurityScore.toFixed(1)}/10
                </p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </div>

          {/* API Tier */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700 dark:text-blue-300">API Tier</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 capitalize">
                  {displayDashboard.tier}
                </p>
              </div>
              <KeyIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </div>

          {/* Usage Count */}
          <div className="bg-gradient-to-br from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-700 dark:text-purple-300">API Calls</p>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                  {displayDashboard.usage_statistics.usage_count.toLocaleString()}
                </p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </div>

          {/* Threats Detected */}
          <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-700 dark:text-orange-300">Threats Blocked</p>
                <p className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                  {displayDashboard.threat_analytics.total_threats}
                </p>
              </div>
              <ExclamationTriangleIcon className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
        </div>
      </div>

      {/* API Key Management */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
              <KeyIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                API Key Management
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Manage your Web3 Security API access
              </p>
            </div>
          </div>
          <Button
            onClick={generateNewApiKey}
            disabled={isGeneratingKey}
            variant="secondary"
            className="flex items-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>{isGeneratingKey ? 'Generating...' : 'Generate New'}</span>
          </Button>
        </div>

        <div className="space-y-4">
          {/* Current API Key */}
          <div className="bg-gradient-to-r from-gray-50 to-indigo-50 dark:from-gray-700 dark:to-indigo-900/30 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Current API Key
              </label>
              <div className="flex items-center space-x-2">
                <Button
                  onClick={() => setApiKeyVisible(!apiKeyVisible)}
                  variant="secondary"
                  className="p-1 h-6 w-6"
                >
                  {apiKeyVisible ? (
                    <EyeSlashIcon className="h-4 w-4" />
                  ) : (
                    <EyeIcon className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  onClick={copyApiKey}
                  variant="secondary"
                  className="p-1 h-6 w-6"
                >
                  <DocumentDuplicateIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="font-mono text-sm bg-white dark:bg-gray-800 rounded border p-3">
              {apiKey ? (
                apiKeyVisible ? apiKey : `${apiKey.slice(0, 12)}${'*'.repeat(20)}${apiKey.slice(-8)}`
              ) : (
                <span className="text-gray-500 dark:text-gray-400">No API key available</span>
              )}
            </div>
            {copySuccess && (
              <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                ✓ API key copied to clipboard
              </p>
            )}
          </div>

          {/* API Key Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-700 dark:text-blue-300">Usage Today</p>
                  <p className="text-xl font-bold text-blue-900 dark:text-blue-100">
                    {displayDashboard.usage_statistics.usage_count}
                  </p>
                </div>
                <ChartBarIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="mt-2">
                <div className="text-xs text-blue-600 dark:text-blue-400">
                  Last used: {new Date(displayDashboard.usage_statistics.last_used).toLocaleTimeString()}
                </div>
              </div>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-700 dark:text-green-300">Rate Limit</p>
                  <p className="text-xl font-bold text-green-900 dark:text-green-100">
                    {Math.round(displayDashboard.rate_limit_status.tokens)}
                  </p>
                </div>
                <BoltIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="mt-2">
                <div className="text-xs text-green-600 dark:text-green-400">
                  Status: {displayDashboard.rate_limit_status.status}
                </div>
              </div>
            </div>

            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-700 dark:text-purple-300">Tier</p>
                  <p className="text-xl font-bold text-purple-900 dark:text-purple-100 capitalize">
                    {displayDashboard.tier}
                  </p>
                </div>
                <KeyIcon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="mt-2">
                <div className="text-xs text-purple-600 dark:text-purple-400">
                  Smart Contract: Active
                </div>
              </div>
            </div>
          </div>

          {/* Usage Instructions */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Usage Instructions
            </h4>
            <div className="space-y-2 text-xs text-gray-600 dark:text-gray-400">
              <div className="flex items-start space-x-2">
                <span className="font-medium">cURL:</span>
                <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">
                  curl -H "Authorization: Bearer {apiKey}" https://api.algocredit.com/v1/security/analyze
                </code>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium">Header:</span>
                <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">
                  X-API-Key: {apiKey?.slice(0, 12)}...
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Threat Analytics */}
      {displayDashboard.threat_analytics && displayDashboard.threat_analytics.total_threats > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Threat Analytics (24h)
          </h3>
          <div className="space-y-3">
            {Object.entries(displayDashboard.threat_analytics.threats_by_type).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                    {type.replace('_', ' ')}
                  </span>
                </div>
                <span className="text-sm font-bold text-orange-600 dark:text-orange-400">
                  {count} blocked
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rate Limit Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Rate Limit Status
        </h3>
        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="flex items-center space-x-3">
            <BoltIcon className="h-5 w-5 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Available Tokens</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Requests remaining in current window</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {Math.round(displayDashboard.rate_limit_status.tokens)}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">
              {displayDashboard.rate_limit_status.status}
            </p>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">System Status</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Last updated: {new Date((displayDashboard as any).generated_at * 1000).toLocaleTimeString()}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-green-600 dark:text-green-400">Operational</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SecurityDashboard
