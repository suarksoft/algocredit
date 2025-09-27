'use client'

import { useState } from 'react'
import { Button } from '@/components/Button'
import { Callout } from '@/components/Callout'

export default function ApiPage() {
  const [apiKey, setApiKey] = useState('')
  const [testResult, setTestResult] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const generateApiKey = async () => {
    setIsLoading(true)
    try {
      // Simulate API key generation
      const newKey = `ak_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
      setApiKey(newKey)
      setTestResult(null)
    } catch (error) {
      console.error('API key generation failed:', error)
    }
    setIsLoading(false)
  }

  const testApiCall = async () => {
    if (!apiKey) {
      alert('Please generate an API key first')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch('/api/web3-security/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          transaction_hash: '0x1234567890abcdef',
          contract_address: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFG',
          function_name: 'transfer'
        })
      })

      const result = await response.json()
      setTestResult(JSON.stringify(result, null, 2))
    } catch (error) {
      setTestResult(`Error: ${error}`)
    }
    setIsLoading(false)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          AlgoCredit Web3 Security API
        </h1>
        <p className="text-lg text-gray-600">
          Geliştiriciler için Web3 güvenlik analiz API'si. Smart contract'ları ve transaction'ları gerçek zamanlı analiz edin.
        </p>
      </div>

      {/* API Key Generation Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">API Key Management</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your API Key
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Generate or paste your API key here"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                readOnly={isLoading}
              />
              <Button
                onClick={generateApiKey}
                disabled={isLoading}
                className="px-4 py-2"
              >
                {isLoading ? 'Generating...' : 'Generate New Key'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* API Documentation */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">API Endpoints</h2>
        
        <div className="space-y-6">
          {/* Transaction Analysis */}
          <div className="border-l-4 border-blue-500 pl-4">
            <h3 className="font-semibold text-lg mb-2">Transaction Security Analysis</h3>
            <code className="bg-gray-100 px-2 py-1 rounded text-sm">
              POST /api/web3-security/analyze
            </code>
            
            <div className="mt-4">
              <h4 className="font-medium mb-2">Request Body:</h4>
              <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
{`{
  "transaction_hash": "string",
  "contract_address": "string",
  "function_name": "string",
  "parameters": [...],
  "value": "number"
}`}
              </pre>
            </div>

            <div className="mt-4">
              <h4 className="font-medium mb-2">Response:</h4>
              <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
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

          {/* Contract Audit */}
          <div className="border-l-4 border-green-500 pl-4">
            <h3 className="font-semibold text-lg mb-2">Smart Contract Audit</h3>
            <code className="bg-gray-100 px-2 py-1 rounded text-sm">
              POST /api/web3-security/audit-contract
            </code>
            
            <div className="mt-4">
              <h4 className="font-medium mb-2">Request Body:</h4>
              <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
{`{
  "contract_address": "string",
  "contract_source": "string (optional)",
  "audit_depth": "basic|detailed|comprehensive"
}`}
              </pre>
            </div>
          </div>

          {/* Real-time Monitoring */}
          <div className="border-l-4 border-purple-500 pl-4">
            <h3 className="font-semibold text-lg mb-2">Real-time Security Monitoring</h3>
            <code className="bg-gray-100 px-2 py-1 rounded text-sm">
              POST /api/web3-security/monitor
            </code>
            
            <div className="mt-4">
              <h4 className="font-medium mb-2">WebSocket Connection:</h4>
              <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
{`ws://localhost:8001/ws/security-monitor?api_key=YOUR_API_KEY`}
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* Test Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">API Test</h2>
        
        <div className="space-y-4">
          <Button
            onClick={testApiCall}
            disabled={isLoading || !apiKey}
            className="px-6 py-2"
          >
            {isLoading ? 'Testing...' : 'Test Transaction Analysis'}
          </Button>

          {testResult && (
            <div>
              <h4 className="font-medium mb-2">Test Result:</h4>
              <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto max-h-64">
                {testResult}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Rate Limits & Pricing */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Rate Limits & Pricing</h2>
        
        <div className="grid md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">Free Tier</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• 1,000 requests/month</li>
              <li>• Basic security analysis</li>
              <li>• Community support</li>
            </ul>
            <div className="mt-4 text-2xl font-bold">$0</div>
          </div>

          <div className="border rounded-lg p-4 border-blue-500">
            <h3 className="font-semibold text-lg mb-2">Developer</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• 50,000 requests/month</li>
              <li>• Advanced threat detection</li>
              <li>• Real-time monitoring</li>
              <li>• Email support</li>
            </ul>
            <div className="mt-4 text-2xl font-bold">$29/month</div>
          </div>

          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">Enterprise</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Unlimited requests</li>
              <li>• Custom security rules</li>
              <li>• Dedicated support</li>
              <li>• SLA guarantee</li>
            </ul>
            <div className="mt-4 text-2xl font-bold">Contact</div>
          </div>
        </div>
      </div>

      {/* Security Features */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Security Features</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-2">🛡️ Threat Detection</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Reentrancy attacks</li>
              <li>• Integer overflow/underflow</li>
              <li>• Phishing contracts</li>
              <li>• Malicious functions</li>
              <li>• Suspicious patterns</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-2">⚡ Real-time Analysis</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Transaction monitoring</li>
              <li>• Contract behavior analysis</li>
              <li>• Risk scoring</li>
              <li>• Automated alerts</li>
              <li>• Historical tracking</li>
            </ul>
          </div>
        </div>
      </div>

      <Callout type="note" className="mt-8">
        Bu API şu anda geliştirme aşamasındadır. Production kullanımı için lütfen bizimle iletişime geçin.
      </Callout>
    </div>
  )
}
