'use client'

import { useState } from 'react'
import { Button } from '@/components/Button'
import { Callout } from '@/components/Callout'

export default function ApiPage() {
  const [apiKey, setApiKey] = useState('')
  const [testResult, setTestResult] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [copiedApiKey, setCopiedApiKey] = useState(false)

  const generateApiKey = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/security/generate-key`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setApiKey(data.api_key)
        setTestResult(null)
      } else {
        throw new Error('Failed to generate API key')
      }
    } catch (error) {
      console.error('API key generation failed:', error)
      alert('API key generation failed. Make sure the backend is running.')
    }
    setIsLoading(false)
  }

  const copyApiKey = async () => {
    if (apiKey) {
      await navigator.clipboard.writeText(apiKey)
      setCopiedApiKey(true)
      setTimeout(() => setCopiedApiKey(false), 2000)
    }
  }

  const testApiCall = async () => {
    if (!apiKey) {
      alert('Please generate an API key first')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/security/validate-transaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          transaction_hash: '0x1234567890abcdef',
          contract_address: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFG',
          function_name: 'transfer',
          parameters: [],
          value: 1000000
        })
      })

      if (response.ok) {
        const result = await response.json()
        setTestResult(JSON.stringify(result, null, 2))
      } else {
        const error = await response.json()
        setTestResult(`Error ${response.status}: ${error.detail}`)
      }
    } catch (error) {
      setTestResult(`Network Error: ${error}`)
    }
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            AlgoCredit Web3 Security API
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Geliştiriciler için profesyonel Web3 güvenlik analiz API'si. Smart contract'ları ve transaction'ları gerçek zamanlı analiz edin, 
            güvenlik açıklarını tespit edin ve blockchain uygulamalarınızı koruyun.
          </p>
        </div>

        {/* API Key Generation Section */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 mb-8 border border-gray-200 dark:border-slate-700">
          <div className="flex items-center mb-6">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m0 0a2 2 0 012 2m-2-2a2 2 0 00-2 2m0 0a2 2 0 002 2M9 7a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2V9a2 2 0 00-2-2H9z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">API Key Management</h2>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Your API Key
              </label>
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Generate or paste your API key here"
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white dark:bg-slate-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  readOnly={isLoading}
                />
                {apiKey && (
                  <Button
                    onClick={copyApiKey}
                    className={`px-4 py-3 ${copiedApiKey ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'}`}
                  >
                    {copiedApiKey ? '✓ Copied' : 'Copy'}
                  </Button>
                )}
                <Button
                  onClick={generateApiKey}
                  disabled={isLoading}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {isLoading ? (
                    <div className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating...
                    </div>
                  ) : 'Generate New Key'}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* API Documentation */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-200">
          <div className="flex items-center mb-6">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">API Endpoints</h2>
          </div>
          
          <div className="space-y-8">
            {/* Transaction Analysis */}
            <div className="border-l-4 border-blue-500 bg-blue-50 rounded-r-xl p-6">
              <div className="flex items-center mb-4">
                <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold mr-3">POST</span>
                <h3 className="font-bold text-lg text-gray-900">Transaction Security Analysis</h3>
              </div>
              <code className="bg-gray-900 text-green-400 px-4 py-2 rounded-lg text-sm block mb-4">
                /api/web3-security/analyze
              </code>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                    Request Body:
                  </h4>
                  <pre className="bg-gray-900 text-gray-300 p-4 rounded-xl text-sm overflow-x-auto">
{`{
  "transaction_hash": "string",
  "contract_address": "string", 
  "function_name": "string",
  "parameters": [...],
  "value": "number"
}`}
                  </pre>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Response:
                  </h4>
                  <pre className="bg-gray-900 text-gray-300 p-4 rounded-xl text-sm overflow-x-auto">
{`{
  "risk_score": 0-100,
  "security_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "threats": [
    {
      "type": "reentrancy|overflow|phishing",
      "severity": "low|medium|high", 
      "description": "Threat description"
    }
  ],
  "recommendations": ["..."],
  "analysis_time": "timestamp"
}`}
                  </pre>
                </div>
              </div>
            </div>

            {/* Contract Audit */}
            <div className="border-l-4 border-green-500 bg-green-50 rounded-r-xl p-6">
              <div className="flex items-center mb-4">
                <span className="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-semibold mr-3">POST</span>
                <h3 className="font-bold text-lg text-gray-900">Smart Contract Audit</h3>
              </div>
              <code className="bg-gray-900 text-green-400 px-4 py-2 rounded-lg text-sm block mb-4">
                /api/web3-security/audit-contract
              </code>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Request Body:
                </h4>
                <pre className="bg-gray-900 text-gray-300 p-4 rounded-xl text-sm overflow-x-auto">
{`{
  "contract_address": "string",
  "contract_source": "string (optional)",
  "audit_depth": "basic|detailed|comprehensive"
}`}
                </pre>
              </div>
            </div>

            {/* Real-time Monitoring */}
            <div className="border-l-4 border-purple-500 bg-purple-50 rounded-r-xl p-6">
              <div className="flex items-center mb-4">
                <span className="bg-purple-600 text-white px-3 py-1 rounded-full text-sm font-semibold mr-3">WS</span>
                <h3 className="font-bold text-lg text-gray-900">Real-time Security Monitoring</h3>
              </div>
              <code className="bg-gray-900 text-green-400 px-4 py-2 rounded-lg text-sm block mb-4">
                /api/web3-security/monitor
              </code>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  WebSocket Connection:
                </h4>
                <pre className="bg-gray-900 text-gray-300 p-4 rounded-xl text-sm overflow-x-auto">
{`ws://localhost:8000/ws/security-monitor?api_key=YOUR_API_KEY`}
                </pre>
              </div>
            </div>
          </div>
        </div>

        {/* Test Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-200">
          <div className="flex items-center mb-6">
            <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">API Test Console</h2>
          </div>
          
          <div className="space-y-6">
            <Button
              onClick={testApiCall}
              disabled={isLoading || !apiKey}
              className="px-8 py-4 text-lg bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Testing API...
                </div>
              ) : '🚀 Test Transaction Analysis'}
            </Button>

            {testResult && (
              <div className="bg-gray-900 rounded-xl p-6 border">
                <h4 className="font-semibold text-green-400 mb-3 flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  Test Result:
                </h4>
                <pre className="text-gray-300 text-sm overflow-x-auto leading-relaxed">
                  {testResult}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Rate Limits & Pricing */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-200">
          <div className="flex items-center mb-8">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Pricing & Rate Limits</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
              <div className="text-center">
                <h3 className="font-bold text-xl mb-4 text-gray-900">Free Tier</h3>
                <div className="text-4xl font-bold text-gray-900 mb-4">$0</div>
                <div className="text-gray-600 text-sm mb-6">Perfect for testing</div>
              </div>
              <ul className="space-y-3 text-sm">
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  1,000 requests/month
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Basic security analysis
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Community support
                </li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-500 relative">
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">Most Popular</span>
              </div>
              <div className="text-center">
                <h3 className="font-bold text-xl mb-4 text-gray-900">Developer</h3>
                <div className="text-4xl font-bold text-blue-600 mb-4">$29</div>
                <div className="text-gray-600 text-sm mb-6">per month</div>
              </div>
              <ul className="space-y-3 text-sm">
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  50,000 requests/month
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Advanced threat detection
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Real-time monitoring
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Email support
                </li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-gray-200">
              <div className="text-center">
                <h3 className="font-bold text-xl mb-4 text-gray-900">Enterprise</h3>
                <div className="text-4xl font-bold text-purple-600 mb-4">Custom</div>
                <div className="text-gray-600 text-sm mb-6">Contact us</div>
              </div>
              <ul className="space-y-3 text-sm">
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Unlimited requests
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Custom security rules
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Dedicated support
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  SLA guarantee
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Security Features */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-200">
          <div className="flex items-center mb-8">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Security Features</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border border-red-200">
              <div className="flex items-center mb-4">
                <span className="text-2xl mr-3">🛡️</span>
                <h3 className="font-bold text-lg text-gray-900">Threat Detection</h3>
              </div>
              <ul className="space-y-3 text-sm">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                  Reentrancy attacks
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                  Integer overflow/underflow
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                  Phishing contracts
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                  Malicious functions
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                  Suspicious patterns
                </li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
              <div className="flex items-center mb-4">
                <span className="text-2xl mr-3">⚡</span>
                <h3 className="font-bold text-lg text-gray-900">Real-time Analysis</h3>
              </div>
              <ul className="space-y-3 text-sm">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Transaction monitoring
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Contract behavior analysis
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Risk scoring
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Automated alerts
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Historical tracking
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom Notice */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white text-center">
          <div className="max-w-3xl mx-auto">
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold mb-3">Development Notice</h3>
            <p className="text-blue-100 text-lg leading-relaxed">
              Bu API şu anda geliştirme aşamasındadır. Production kullanımı için lütfen bizimle iletişime geçin. 
              Güvenlik analiz sonuçları sürekli geliştirilmektedir ve %100 doğruluğu garanti edilmemektedir.
            </p>
            <div className="mt-6">
              <Button className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold">
                İletişime Geç
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
