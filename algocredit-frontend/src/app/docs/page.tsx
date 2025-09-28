/**
 * API Documentation Page
 * Interactive documentation for AlgoCredit API endpoints
 */

'use client'

import { useState } from 'react'
import { Button } from '@/components/Button'
import { 
  CodeBracketIcon,
  CubeIcon,
  DocumentTextIcon,
  PlayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClipboardIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline'

interface APIEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  path: string
  title: string
  description: string
  parameters?: Array<{
    name: string
    type: string
    required: boolean
    description: string
    example?: any
  }>
  requestBody?: {
    type: string
    properties: Record<string, any>
    example: any
  }
  responses: Array<{
    status: number
    description: string
    example: any
  }>
  tags: string[]
}

const apiEndpoints: APIEndpoint[] = [
  {
    method: 'GET',
    path: '/health',
    title: 'Health Check',
    description: 'Check API server health and status',
    responses: [
      {
        status: 200,
        description: 'Server is healthy',
        example: {
          status: 'healthy',
          service: 'AlgoCredit API',
          version: '1.0.0',
          algorand_network: 'testnet',
          database: 'connected',
          ai_model: 'loaded'
        }
      }
    ],
    tags: ['Health']
  },
  {
    method: 'POST',
    path: '/api/v1/credit/score',
    title: 'AI Credit Scoring',
    description: 'Get AI-powered credit score analysis for wallet address',
    parameters: [
      {
        name: 'wallet_address',
        type: 'string',
        required: true,
        description: 'Algorand wallet address to analyze',
        example: '6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U'
      },
      {
        name: 'requested_amount',
        type: 'number',
        required: false,
        description: 'Loan amount in microAlgos',
        example: 50000000
      },
      {
        name: 'loan_term_months',
        type: 'number',
        required: false,
        description: 'Loan term in months',
        example: 12
      }
    ],
    responses: [
      {
        status: 200,
        description: 'Credit assessment completed',
        example: {
          wallet_address: '6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U',
          credit_score: 720,
          confidence: 85.5,
          risk_level: 'medium',
          max_loan_amount: 75000000,
          recommended_interest_rate: 8.5,
          insights: [
            '🟢 Strong financial position',
            '🟡 Moderate transaction history',
            '🟢 Stable balance patterns'
          ],
          wallet_metrics: {
            account_age_days: 365,
            total_transactions: 150,
            current_balance_algo: 5.0,
            total_volume_algo: 250.0
          },
          model_info: {
            model_version: 'AlgoCredit AI v1.0',
            scoring_method: 'AI Model',
            ai_enabled: true
          }
        }
      }
    ],
    tags: ['Credit Scoring', 'AI']
  },
  {
    method: 'GET',
    path: '/api/v1/credit/wallet/{wallet_address}',
    title: 'Wallet Analysis',
    description: 'Get detailed blockchain analysis for wallet',
    parameters: [
      {
        name: 'wallet_address',
        type: 'string',
        required: true,
        description: 'Algorand wallet address',
        example: '6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U'
      }
    ],
    responses: [
      {
        status: 200,
        description: 'Wallet analysis completed',
        example: {
          wallet_address: '6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U',
          account_age_days: 365,
          total_transactions: 150,
          total_volume: 250000000,
          current_balance: 5000000,
          balance_stability_score: 85.5,
          transaction_frequency_score: 72.3,
          asset_diversity_score: 45.2,
          dapp_usage_score: 60.8
        }
      }
    ],
    tags: ['Wallet Analysis']
  },
  {
    method: 'GET',
    path: '/marketplace/stats',
    title: 'Marketplace Statistics',
    description: 'Get platform marketplace statistics',
    responses: [
      {
        status: 200,
        description: 'Marketplace statistics',
        example: {
          total_startups: 12,
          total_investors: 8,
          total_funding: 2500000,
          active_deals: 5,
          success_rate: 85.5,
          avg_funding_time: '7.2 days'
        }
      }
    ],
    tags: ['Marketplace']
  },
  {
    method: 'POST',
    path: '/user/login',
    title: 'User Login',
    description: 'Login user with wallet address',
    parameters: [
      {
        name: 'wallet',
        type: 'string',
        required: true,
        description: 'User wallet address',
        example: '6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U'
      },
      {
        name: 'type',
        type: 'string',
        required: true,
        description: 'User type: startup or investor',
        example: 'startup'
      }
    ],
    responses: [
      {
        status: 200,
        description: 'Login successful',
        example: {
          success: true,
          user_id: 'startup_12345',
          wallet_address: '6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U',
          user_type: 'startup'
        }
      }
    ],
    tags: ['Authentication']
  }
]

export default function DocsPage() {
  const [expandedEndpoints, setExpandedEndpoints] = useState<Set<string>>(new Set())
  const [activeTab, setActiveTab] = useState<'overview' | 'endpoints' | 'examples'>('overview')
  const [selectedTag, setSelectedTag] = useState<string>('all')
  const [testResults, setTestResults] = useState<Record<string, any>>({})

  const toggleEndpoint = (path: string) => {
    const newExpanded = new Set(expandedEndpoints)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedEndpoints(newExpanded)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const testEndpoint = async (endpoint: APIEndpoint) => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8005'
      let url = baseUrl + endpoint.path
      
      // Replace path parameters with example values
      if (endpoint.parameters) {
        endpoint.parameters.forEach(param => {
          if (param.example) {
            url = url.replace(`{${param.name}}`, param.example.toString())
          }
        })
      }

      // Add query parameters for GET requests
      if (endpoint.method === 'GET' && endpoint.parameters) {
        const queryParams = new URLSearchParams()
        endpoint.parameters.forEach(param => {
          if (param.example) {
            queryParams.append(param.name, param.example.toString())
          }
        })
        if (queryParams.toString()) {
          url += '?' + queryParams.toString()
        }
      }

      const response = await fetch(url, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_ALGOCREDIT_API_KEY || 'demo_key'}`
        },
        body: endpoint.method === 'POST' && endpoint.requestBody 
          ? JSON.stringify(endpoint.requestBody.example) 
          : undefined
      })

      const data = await response.json()
      setTestResults(prev => ({
        ...prev,
        [endpoint.path]: {
          status: response.status,
          data,
          success: response.ok
        }
      }))
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [endpoint.path]: {
          status: 500,
          error: error instanceof Error ? error.message : 'Network error',
          success: false
        }
      }))
    }
  }

  const allTags = ['all', ...Array.from(new Set(apiEndpoints.flatMap(e => e.tags)))]
  const filteredEndpoints = selectedTag === 'all' 
    ? apiEndpoints 
    : apiEndpoints.filter(e => e.tags.includes(selectedTag))

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-green-100 text-green-800 border-green-200'
      case 'POST': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'PUT': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'DELETE': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900">
      {/* Header */}
      <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        <div className="text-center mb-12">
          <div className="mb-4">
            <div className="mx-auto h-16 w-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center mb-6">
              <DocumentTextIcon className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            API Documentation
          </h1>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Interactive documentation for AlgoCredit AI-powered DeFi lending platform APIs
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="flex justify-center">
            <nav className="flex space-x-8 bg-white/60 dark:bg-slate-800/60 rounded-xl p-2 backdrop-blur-sm">
              {(['overview', 'endpoints', 'examples'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 capitalize ${
                    activeTab === tab
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-slate-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-white/70 dark:bg-slate-800/70 rounded-2xl p-6 backdrop-blur-sm border border-white/30 dark:border-slate-700/50">
                <div className="flex items-center gap-3 mb-4">
                  <CubeIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Base URL</h3>
                </div>
                <div className="bg-gray-100 dark:bg-slate-700 rounded-lg p-3 font-mono text-sm">
                  http://localhost:8005
                </div>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Development server endpoint
                </p>
              </div>

              <div className="bg-white/70 dark:bg-slate-800/70 rounded-2xl p-6 backdrop-blur-sm border border-white/30 dark:border-slate-700/50">
                <div className="flex items-center gap-3 mb-4">
                  <CheckCircleIcon className="h-6 w-6 text-green-600" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Authentication</h3>
                </div>
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="font-medium">Header:</span> Authorization
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Format:</span> Bearer {'{token}'}
                  </div>
                </div>
              </div>

              <div className="bg-white/70 dark:bg-slate-800/70 rounded-2xl p-6 backdrop-blur-sm border border-white/30 dark:border-slate-700/50">
                <div className="flex items-center gap-3 mb-4">
                  <CodeBracketIcon className="h-6 w-6 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Response Format</h3>
                </div>
                <div className="text-sm space-y-1">
                  <div>Content-Type: application/json</div>
                  <div>UTF-8 encoding</div>
                  <div>HTTP status codes</div>
                </div>
              </div>
            </div>

            <div className="bg-white/70 dark:bg-slate-800/70 rounded-2xl p-8 backdrop-blur-sm border border-white/30 dark:border-slate-700/50">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Quick Start</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">1. Health Check</h3>
                  <div className="bg-slate-900 rounded-lg p-4 text-green-400 font-mono text-sm overflow-x-auto">
                    curl -X GET http://localhost:8005/health
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">2. Get Credit Score</h3>
                  <div className="bg-slate-900 rounded-lg p-4 text-green-400 font-mono text-sm overflow-x-auto">
                    curl -X POST http://localhost:8005/api/v1/credit/score \\<br />
                    &nbsp;&nbsp;-H "Content-Type: application/json" \\<br />
                    &nbsp;&nbsp;-d '{`{"wallet_address": "YOUR_WALLET_ADDRESS"}`}'
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Endpoints Tab */}
        {activeTab === 'endpoints' && (
          <div className="space-y-8">
            {/* Tag Filter */}
            <div className="flex flex-wrap gap-2">
              {allTags.map(tag => (
                <button
                  key={tag}
                  onClick={() => setSelectedTag(tag)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-200 capitalize ${
                    selectedTag === tag
                      ? 'bg-blue-600 text-white'
                      : 'bg-white/60 text-gray-700 hover:bg-blue-50 dark:bg-slate-700/60 dark:text-gray-300'
                  }`}
                >
                  {tag} ({tag === 'all' ? apiEndpoints.length : apiEndpoints.filter(e => e.tags.includes(tag)).length})
                </button>
              ))}
            </div>

            {/* API Endpoints */}
            <div className="space-y-4">
              {filteredEndpoints.map((endpoint) => (
                <div key={endpoint.path} className="bg-white/70 dark:bg-slate-800/70 rounded-2xl backdrop-blur-sm border border-white/30 dark:border-slate-700/50 overflow-hidden">
                  <div className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <span className={`px-3 py-1 rounded-lg border font-mono text-sm font-semibold ${getMethodColor(endpoint.method)}`}>
                          {endpoint.method}
                        </span>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {endpoint.title}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                            {endpoint.path}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          onClick={() => testEndpoint(endpoint)}
                          className="h-8 px-3 bg-green-600 hover:bg-green-700 text-white"
                        >
                          <PlayIcon className="h-3 w-3 mr-1" />
                          Test
                        </Button>
                        <button
                          onClick={() => toggleEndpoint(endpoint.path)}
                          className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                          {expandedEndpoints.has(endpoint.path) ? (
                            <ChevronDownIcon className="h-5 w-5" />
                          ) : (
                            <ChevronRightIcon className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                    </div>
                    <p className="mt-2 text-gray-600 dark:text-gray-300">
                      {endpoint.description}
                    </p>
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mt-3">
                      {endpoint.tags.map(tag => (
                        <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Expanded Content */}
                  {expandedEndpoints.has(endpoint.path) && (
                    <div className="border-t border-gray-200 dark:border-gray-700">
                      <div className="p-6 space-y-6">
                        {/* Parameters */}
                        {endpoint.parameters && (
                          <div>
                            <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3">Parameters</h4>
                            <div className="space-y-2">
                              {endpoint.parameters.map(param => (
                                <div key={param.name} className="flex items-start gap-4 p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <span className="font-mono text-sm font-medium">{param.name}</span>
                                      <span className="text-xs text-gray-500 dark:text-gray-400">{param.type}</span>
                                      {param.required && (
                                        <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">required</span>
                                      )}
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{param.description}</p>
                                    {param.example && (
                                      <div className="mt-2">
                                        <span className="text-xs text-gray-500">Example:</span>
                                        <code className="ml-2 text-xs bg-gray-200 dark:bg-slate-800 px-2 py-1 rounded">
                                          {JSON.stringify(param.example)}
                                        </code>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Response Examples */}
                        <div>
                          <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3">Responses</h4>
                          <div className="space-y-3">
                            {endpoint.responses.map(response => (
                              <div key={response.status} className="border rounded-lg overflow-hidden">
                                <div className="bg-gray-50 dark:bg-slate-700 px-4 py-2 flex items-center justify-between">
                                  <span className={`px-2 py-1 rounded text-sm font-semibold ${
                                    response.status < 300 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                  }`}>
                                    {response.status}
                                  </span>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">{response.description}</span>
                                  <button
                                    onClick={() => copyToClipboard(JSON.stringify(response.example, null, 2))}
                                    className="p-1 text-gray-500 hover:text-gray-700"
                                  >
                                    <ClipboardIcon className="h-4 w-4" />
                                  </button>
                                </div>
                                <div className="p-4">
                                  <pre className="text-xs bg-slate-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                                    {JSON.stringify(response.example, null, 2)}
                                  </pre>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Test Results */}
                        {testResults[endpoint.path] && (
                          <div>
                            <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-3">Test Result</h4>
                            <div className={`p-4 rounded-lg ${
                              testResults[endpoint.path].success 
                                ? 'bg-green-50 border-green-200 dark:bg-green-900/20' 
                                : 'bg-red-50 border-red-200 dark:bg-red-900/20'
                            }`}>
                              <div className="flex items-center gap-2 mb-2">
                                {testResults[endpoint.path].success ? (
                                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                                ) : (
                                  <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                                )}
                                <span className="font-semibold">
                                  Status: {testResults[endpoint.path].status}
                                </span>
                              </div>
                              <pre className="text-xs bg-slate-900 text-green-400 p-3 rounded overflow-x-auto">
                                {JSON.stringify(testResults[endpoint.path].data || testResults[endpoint.path].error, null, 2)}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Examples Tab */}
        {activeTab === 'examples' && (
          <div className="space-y-8">
            <div className="bg-white/70 dark:bg-slate-800/70 rounded-2xl p-8 backdrop-blur-sm border border-white/30 dark:border-slate-700/50">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Code Examples</h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">JavaScript/TypeScript</h3>
                  <pre className="bg-slate-900 text-green-400 p-6 rounded-lg overflow-x-auto text-sm">
{`// Get credit score
const getCreditScore = async (walletAddress: string) => {
  const response = await fetch('http://localhost:8005/api/v1/credit/score', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: JSON.stringify({
      wallet_address: walletAddress,
      requested_amount: 50000000, // 50 ALGO in microAlgos
      loan_term_months: 12
    })
  })
  
  const data = await response.json()
  return data
}`}
                  </pre>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Python</h3>
                  <pre className="bg-slate-900 text-green-400 p-6 rounded-lg overflow-x-auto text-sm">
{`import requests

def get_credit_score(wallet_address: str):
    url = "http://localhost:8005/api/v1/credit/score"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
    }
    data = {
        "wallet_address": wallet_address,
        "requested_amount": 50000000,  # 50 ALGO in microAlgos
        "loan_term_months": 12
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()`}
                  </pre>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">cURL</h3>
                  <pre className="bg-slate-900 text-green-400 p-6 rounded-lg overflow-x-auto text-sm">
{`curl -X POST "http://localhost:8005/api/v1/credit/score" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{
    "wallet_address": "6APFHMFGVPRLYZ6EOGYJLBCBHPL2AP7RRWMAGUGL4EKNFDTB5WIBAC2Y7U",
    "requested_amount": 50000000,
    "loan_term_months": 12
  }'`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}