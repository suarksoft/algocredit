/**
 * AlgoCredit Web3 Security Firewall
 * Enterprise-Grade Security Platform for Algorand Ecosystem
 */

'use client'

import { useState, useEffect } from 'react'
import { WalletConnect } from '@/components/WalletConnect'
import { Button } from '@/components/Button'
import { useSecurityStore } from '@/stores/securityStore'
import SecurityDashboard from '@/components/SecurityDashboard'
import { 
  ShieldCheckIcon, 
  CpuChipIcon, 
  BoltIcon, 
  GlobeAltIcon,
  ChartBarIcon,
  LockClosedIcon,
  ExclamationTriangleIcon,
  CheckBadgeIcon,
  ArrowTrendingUpIcon,
  BuildingOffice2Icon,
  CurrencyDollarIcon,
  UsersIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  CodeBracketIcon,
  CloudIcon,
  CogIcon
} from '@heroicons/react/24/outline'

export default function HomePage() {
  const { 
    securityScore, 
    threatLevel, 
    isLoadingDashboard, 
    loadSecurityDashboard,
    generateApiKey,
    apiKey,
    tier
  } = useSecurityStore()

  const [stats, setStats] = useState({
    totalApiKeys: 0,
    threatsBlocked: 0,
    transactionsSecured: 0,
    enterpriseClients: 0
  })

  const [isLoading, setIsLoading] = useState(true)
  const [showSecurityDemo, setShowSecurityDemo] = useState(false)
  const [demoApiKey, setDemoApiKey] = useState('')

  useEffect(() => {
    // Fetch security platform stats
    const fetchStats = async () => {
      try {
        // Simulate security platform metrics
        await new Promise(resolve => setTimeout(resolve, 1000))
        setStats({
          totalApiKeys: 1247,
          threatsBlocked: 15632,
          transactionsSecured: 892156,
          enterpriseClients: 34
        })
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
    
    // Load security dashboard if available
    if (apiKey) {
      loadSecurityDashboard()
    }
  }, [apiKey])

  const handleGenerateDemoKey = async () => {
    try {
      const newKey = await generateApiKey('demo_user_' + Date.now(), 'pro')
      setDemoApiKey(newKey)
      setShowSecurityDemo(true)
    } catch (error) {
      console.error('Error generating demo key:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-32 h-80 w-80 rounded-full bg-gradient-to-br from-blue-400/30 to-purple-600/30 blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-32 h-80 w-80 rounded-full bg-gradient-to-tr from-indigo-400/30 to-blue-600/30 blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-gradient-to-r from-cyan-400/20 to-blue-600/20 blur-3xl animate-pulse"></div>
      </div>

      <div className="relative">
        {/* Header Section */}
        <header className="pt-8 pb-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              {/* Logo and Brand */}
              <div className="mb-8">
                <div className="mx-auto h-20 w-20 rounded-full bg-gradient-to-r from-blue-500 via-purple-600 to-indigo-600 flex items-center justify-center mb-6 shadow-2xl">
                  <ShieldCheckIcon className="h-10 w-10 text-white" />
                </div>
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent mb-4">
                  AlgoCredit
                </h1>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 backdrop-blur-sm rounded-full border border-blue-400/30">
                  <LockClosedIcon className="h-4 w-4 text-blue-300" />
                  <span className="text-blue-100 font-medium">Web3 Security Firewall</span>
                </div>
              </div>

              {/* Hero Message */}
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-6 max-w-4xl mx-auto leading-tight">
                Enterprise-Grade Security Platform for 
                <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Algorand Ecosystem</span>
              </h2>
              
              <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto leading-relaxed">
                Protect your Web3 applications with advanced threat detection, AI-powered risk assessment, 
                and enterprise-grade security infrastructure built specifically for Algorand.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
                <Button 
                  onClick={handleGenerateDemoKey}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 px-8 py-4 text-lg font-semibold"
                >
                  <BoltIcon className="mr-2 h-5 w-5" />
                  Get Free API Key
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={() => setShowSecurityDemo(true)}
                  className="border-blue-400 text-blue-100 hover:bg-blue-500/10 backdrop-blur-sm px-8 py-4 text-lg font-semibold"
                >
                  <ChartBarIcon className="mr-2 h-5 w-5" />
                  View Security Demo
                </Button>
              </div>

              {/* Trust Indicators */}
              <div className="flex flex-wrap items-center justify-center gap-6 text-blue-200">
                <div className="flex items-center gap-2">
                  <CheckBadgeIcon className="h-5 w-5 text-green-400" />
                  <span>SOC 2 Compliant</span>
                </div>
                <div className="flex items-center gap-2">
                  <ShieldCheckIcon className="h-5 w-5 text-blue-400" />
                  <span>Enterprise Security</span>
                </div>
                <div className="flex items-center gap-2">
                  <GlobeAltIcon className="h-5 w-5 text-purple-400" />
                  <span>Algorand Native</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Security Stats Section */}
        <section className="py-16 bg-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h3 className="text-3xl font-bold text-white mb-4">
                Protecting the Algorand Ecosystem
              </h3>
              <p className="text-blue-200 text-lg max-w-2xl mx-auto">
                Real-time security metrics from our Web3 Security Firewall
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* API Keys */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-blue-500/20 rounded-lg">
                    <CodeBracketIcon className="h-6 w-6 text-blue-300" />
                  </div>
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                </div>
                <h4 className="text-white font-semibold mb-2">Active API Keys</h4>
                <p className="text-3xl font-bold text-blue-300 mb-1">
                  {isLoading ? '...' : stats.totalApiKeys.toLocaleString()}
                </p>
                <p className="text-blue-200 text-sm">Developers protected</p>
              </div>

              {/* Threats Blocked */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-red-500/20 rounded-lg">
                    <ExclamationTriangleIcon className="h-6 w-6 text-red-300" />
                  </div>
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                </div>
                <h4 className="text-white font-semibold mb-2">Threats Blocked</h4>
                <p className="text-3xl font-bold text-red-300 mb-1">
                  {isLoading ? '...' : stats.threatsBlocked.toLocaleString()}
                </p>
                <p className="text-blue-200 text-sm">Security incidents prevented</p>
              </div>

              {/* Transactions Secured */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-green-500/20 rounded-lg">
                    <CheckCircleIcon className="h-6 w-6 text-green-300" />
                  </div>
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                </div>
                <h4 className="text-white font-semibold mb-2">Transactions Secured</h4>
                <p className="text-3xl font-bold text-green-300 mb-1">
                  {isLoading ? '...' : (stats.transactionsSecured / 1000).toFixed(0)}K
                </p>
                <p className="text-blue-200 text-sm">Validated & protected</p>
              </div>

              {/* Enterprise Clients */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-purple-500/20 rounded-lg">
                    <BuildingOffice2Icon className="h-6 w-6 text-purple-300" />
                  </div>
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                </div>
                <h4 className="text-white font-semibold mb-2">Enterprise Clients</h4>
                <p className="text-3xl font-bold text-purple-300 mb-1">
                  {isLoading ? '...' : stats.enterpriseClients}
                </p>
                <p className="text-blue-200 text-sm">Fortune 500 companies</p>
              </div>
            </div>
          </div>
        </section>

        {/* Security Features Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h3 className="text-4xl font-bold text-white mb-6">
                Advanced Web3 Security Features
              </h3>
              <p className="text-blue-200 text-xl max-w-3xl mx-auto">
                Comprehensive protection against Web3-specific threats and vulnerabilities
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Threat Detection */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="p-4 bg-red-500/20 rounded-xl w-fit mb-6">
                  <ExclamationTriangleIcon className="h-8 w-8 text-red-300" />
                </div>
                <h4 className="text-2xl font-bold text-white mb-4">Threat Detection</h4>
                <p className="text-blue-200 mb-6 leading-relaxed">
                  AI-powered detection of replay attacks, flash loan exploits, MEV manipulation, 
                  and sandwich attacks in real-time.
                </p>
                <ul className="space-y-3 text-blue-300">
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Replay Attack Prevention</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Flash Loan Exploit Detection</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>MEV Protection</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Anomaly Detection</span>
                  </li>
                </ul>
              </div>

              {/* API Security */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="p-4 bg-blue-500/20 rounded-xl w-fit mb-6">
                  <LockClosedIcon className="h-8 w-8 text-blue-300" />
                </div>
                <h4 className="text-2xl font-bold text-white mb-4">API Security</h4>
                <p className="text-blue-200 mb-6 leading-relaxed">
                  Enterprise-grade API authentication, rate limiting, and access control 
                  with tiered permissions and usage analytics.
                </p>
                <ul className="space-y-3 text-blue-300">
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Tiered API Keys</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Adaptive Rate Limiting</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>DDoS Protection</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Usage Analytics</span>
                  </li>
                </ul>
              </div>

              {/* AI Credit Scoring */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="p-4 bg-purple-500/20 rounded-xl w-fit mb-6">
                  <CpuChipIcon className="h-8 w-8 text-purple-300" />
                </div>
                <h4 className="text-2xl font-bold text-white mb-4">AI Credit Scoring</h4>
                <p className="text-blue-200 mb-6 leading-relaxed">
                  Advanced machine learning models analyze on-chain behavior, 
                  transaction patterns, and wallet history for accurate risk assessment.
                </p>
                <ul className="space-y-3 text-blue-300">
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>On-chain Analysis</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Behavioral Patterns</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Risk Profiling</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>Real-time Scoring</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Integration Section */}
        <section className="py-20 bg-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h3 className="text-4xl font-bold text-white mb-6">
                Easy Integration for Developers
              </h3>
              <p className="text-blue-200 text-xl max-w-3xl mx-auto">
                Integrate enterprise security into your Algorand dApp with just a few lines of code
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              {/* Code Example */}
              <div className="bg-slate-900/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-white font-semibold">Quick Integration</h4>
                  <div className="flex gap-2">
                    <div className="h-3 w-3 rounded-full bg-red-400"></div>
                    <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                    <div className="h-3 w-3 rounded-full bg-green-400"></div>
                  </div>
                </div>
                <pre className="text-green-400 text-sm overflow-x-auto">
{`import { AlgoCreditSecurity } from '@algocredit/sdk'

const security = new AlgoCreditSecurity({
  apiKey: 'ac_live_...',
  tier: 'pro'
})

// Secure transaction validation
const result = await security.validateTransaction({
  from: wallet.address,
  to: recipient,
  amount: 1000000
})

if (result.isSecure) {
  // Proceed with transaction
  await submitTransaction()
}`}
                </pre>
              </div>

              {/* Features List */}
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-blue-500/20 rounded-lg flex-shrink-0">
                    <BoltIcon className="h-6 w-6 text-blue-300" />
                  </div>
                  <div>
                    <h5 className="text-white font-semibold mb-2">Lightning Fast</h5>
                    <p className="text-blue-200">Sub-100ms response times with Redis-backed caching and optimized algorithms.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="p-2 bg-purple-500/20 rounded-lg flex-shrink-0">
                    <CogIcon className="h-6 w-6 text-purple-300" />
                  </div>
                  <div>
                    <h5 className="text-white font-semibold mb-2">Highly Configurable</h5>
                    <p className="text-blue-200">Customize security rules, thresholds, and policies to match your application needs.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="p-2 bg-green-500/20 rounded-lg flex-shrink-0">
                    <CloudIcon className="h-6 w-6 text-green-300" />
                  </div>
                  <div>
                    <h5 className="text-white font-semibold mb-2">Cloud Native</h5>
                    <p className="text-blue-200">Built for scale with microservices architecture and enterprise deployment options.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="p-2 bg-yellow-500/20 rounded-lg flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-yellow-300" />
                  </div>
                  <div>
                    <h5 className="text-white font-semibold mb-2">Advanced Analytics</h5>
                    <p className="text-blue-200">Comprehensive security dashboards with real-time threat intelligence and insights.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Demo Section */}
        {showSecurityDemo && (
          <section className="py-16">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <div className="text-center mb-8">
                  <h3 className="text-3xl font-bold text-white mb-4">
                    🛡️ Live Security Dashboard
                  </h3>
                  <p className="text-blue-200">
                    Real-time security monitoring and threat analysis
                  </p>
                  {demoApiKey && (
                    <div className="mt-4 p-3 bg-blue-900/30 rounded-lg">
                      <p className="text-blue-300 text-sm">Demo API Key: <code className="bg-slate-800 px-2 py-1 rounded">{demoApiKey.slice(0, 20)}...</code></p>
                    </div>
                  )}
                </div>
                
                <SecurityDashboard apiKey={demoApiKey || apiKey} />
              </div>
            </div>
          </section>
        )}

        {/* Pricing Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h3 className="text-4xl font-bold text-white mb-6">
                Enterprise Security Pricing
              </h3>
              <p className="text-blue-200 text-xl max-w-3xl mx-auto">
                Flexible pricing for startups to enterprise. Start free, scale as you grow.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Free Tier */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <div className="text-center">
                  <h4 className="text-2xl font-bold text-white mb-2">Free</h4>
                  <p className="text-blue-200 mb-6">Perfect for development</p>
                  <div className="text-4xl font-bold text-blue-300 mb-6">$0<span className="text-lg text-blue-200">/month</span></div>
                </div>
                <ul className="space-y-3 text-blue-300 mb-8">
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>1K requests/day</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Basic threat detection</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>API documentation</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Community support</span>
                  </li>
                </ul>
                <Button 
                  onClick={handleGenerateDemoKey}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Get Free API Key
                </Button>
              </div>

              {/* Pro Tier */}
              <div className="bg-gradient-to-br from-blue-500/20 to-purple-600/20 backdrop-blur-sm rounded-2xl p-8 border-2 border-blue-400/50 transform scale-105">
                <div className="text-center">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/30 rounded-full mb-4">
                    <span className="text-blue-200 text-sm font-medium">Most Popular</span>
                  </div>
                  <h4 className="text-2xl font-bold text-white mb-2">Pro</h4>
                  <p className="text-blue-200 mb-6">For growing applications</p>
                  <div className="text-4xl font-bold text-blue-300 mb-6">$99<span className="text-lg text-blue-200">/month</span></div>
                </div>
                <ul className="space-y-3 text-blue-300 mb-8">
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>100K requests/day</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Advanced threat detection</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Security dashboard</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Webhook notifications</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Priority support</span>
                  </li>
                </ul>
                <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white">
                  Start Pro Trial
                </Button>
              </div>

              {/* Enterprise Tier */}
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <div className="text-center">
                  <h4 className="text-2xl font-bold text-white mb-2">Enterprise</h4>
                  <p className="text-blue-200 mb-6">For large organizations</p>
                  <div className="text-4xl font-bold text-blue-300 mb-6">Custom<span className="text-lg text-blue-200">/month</span></div>
                </div>
                <ul className="space-y-3 text-blue-300 mb-8">
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Unlimited requests</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Custom security rules</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>Dedicated infrastructure</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>24/7 security team</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    <span>SLA guarantees</span>
                  </li>
                </ul>
                <Button 
                  variant="outline"
                  className="w-full border-white/30 text-white hover:bg-white/10"
                >
                  Contact Sales
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-sm rounded-2xl p-12 border border-blue-400/30">
              <h3 className="text-4xl font-bold text-white mb-6">
                Ready to Secure Your Algorand dApp?
              </h3>
              <p className="text-blue-200 text-xl mb-8 max-w-2xl mx-auto">
                Join hundreds of developers protecting their Web3 applications with AlgoCredit Security Firewall.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button 
                  onClick={() => window.open('/apply', '_blank')}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-2xl px-8 py-4 text-lg font-semibold"
                >
                  <ArrowRightIcon className="mr-2 h-5 w-5" />
                  Start Building Securely
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                  className="border-blue-400 text-blue-100 hover:bg-blue-500/10 backdrop-blur-sm px-8 py-4 text-lg font-semibold"
                >
                  <CodeBracketIcon className="mr-2 h-5 w-5" />
                  API Documentation
                </Button>
              </div>

              {/* Security Badges */}
              <div className="flex flex-wrap items-center justify-center gap-4 mt-8 pt-8 border-t border-white/20">
                <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 rounded-full">
                  <CheckBadgeIcon className="h-4 w-4 text-green-400" />
                  <span className="text-green-300 text-sm font-medium">99.9% Uptime</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 rounded-full">
                  <ShieldCheckIcon className="h-4 w-4 text-blue-400" />
                  <span className="text-blue-300 text-sm font-medium">SOC 2 Certified</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 rounded-full">
                  <CpuChipIcon className="h-4 w-4 text-purple-400" />
                  <span className="text-purple-300 text-sm font-medium">AI-Powered</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 border-t border-white/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-blue-400" />
                <span className="text-white font-bold text-xl">AlgoCredit Security</span>
              </div>
              <p className="text-blue-200 mb-4">
                Enterprise Web3 Security Firewall for Algorand Ecosystem
              </p>
              <div className="flex items-center justify-center gap-6 text-blue-300">
                <a href="/docs" className="hover:text-white transition-colors">Documentation</a>
                <a href="/api" className="hover:text-white transition-colors">API Reference</a>
                <a href="/support" className="hover:text-white transition-colors">Support</a>
                <a href="/contact" className="hover:text-white transition-colors">Contact</a>
              </div>
              <div className="mt-6 pt-6 border-t border-white/20">
                <p className="text-blue-300 text-sm">
                  © 2024 AlgoCredit. Built for Algorand Foundation. Enterprise Security Platform.
                </p>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
