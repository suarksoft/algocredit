/**
 * Investor Dashboard - 24 Hour Sprint
 * Portfolio management, startup browsing, and funding execution
 */

'use client'

import { useState, useEffect } from 'react'
import { WalletConnect } from '@/components/WalletConnect'
import { Button } from '@/components/Button'
import { 
  CurrencyDollarIcon,
  ChartBarIcon,
  BuildingOfficeIcon,
  TrophyIcon,
  EyeIcon,
  PlusIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

interface InvestorData {
  user_id: number
  name: string
  wallet_address: string
  current_balance: number
  total_invested: number
  yield_earned: number
  active_investments: number
}

interface StartupOpportunity {
  id: number
  name: string
  business_description: string
  requested_amount: number
  credit_score: number
  interest_rate: number
  loan_term_months: number
  risk_level: string
  created_at: string
}

interface PortfolioInvestment {
  startup_id: number
  startup_name: string
  invested_amount: number
  interest_rate: number
  status: string
  loan_term: number
  expected_return: number
  profit: number
}

interface RegistrationForm {
  name: string
  investment_capacity: string
  risk_preference: string
}

export default function InvestorDashboard() {
  const [isConnected, setIsConnected] = useState(false)
  const [walletAddress, setWalletAddress] = useState('')
  const [investorData, setInvestorData] = useState<InvestorData | null>(null)
  const [availableStartups, setAvailableStartups] = useState<StartupOpportunity[]>([])
  const [portfolio, setPortfolio] = useState<PortfolioInvestment[]>([])
  const [loading, setLoading] = useState(false)
  const [showRegistration, setShowRegistration] = useState(false)
  const [showDepositModal, setShowDepositModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'opportunities' | 'portfolio'>('overview')
  const [depositAmount, setDepositAmount] = useState('')
  const [registrationForm, setRegistrationForm] = useState<RegistrationForm>({
    name: '',
    investment_capacity: '',
    risk_preference: 'moderate'
  })

  useEffect(() => {
    if (isConnected && walletAddress) {
      checkInvestorStatus()
    }
  }, [isConnected, walletAddress])

  useEffect(() => {
    if (investorData) {
      fetchAvailableStartups()
      fetchPortfolio()
    }
  }, [investorData])

  const checkInvestorStatus = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/user/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wallet_address: walletAddress,
          user_type: 'investor'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setInvestorData(data)
      } else {
        setShowRegistration(true)
      }
    } catch (error) {
      console.error('Failed to check investor status:', error)
      setShowRegistration(true)
    } finally {
      setLoading(false)
    }
  }

  const handleRegistration = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/investor/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: registrationForm.name,
          wallet_address: walletAddress,
          investment_capacity: parseInt(registrationForm.investment_capacity),
          risk_preference: registrationForm.risk_preference
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Registration successful! Investor ID: ${data.investor_id}`)
        setShowRegistration(false)
        checkInvestorStatus()
      } else {
        const error = await response.json()
        alert(`Registration failed: ${error.detail}`)
      }
    } catch (error) {
      console.error('Registration failed:', error)
      alert('Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!investorData) return

    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/investor/deposit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          investor_id: investorData.user_id,
          amount: parseInt(depositAmount)
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Deposit successful! Amount: ${data.amount} ALGO`)
        setShowDepositModal(false)
        setDepositAmount('')
        checkInvestorStatus() // Refresh data
      } else {
        alert('Deposit failed')
      }
    } catch (error) {
      console.error('Deposit failed:', error)
      alert('Deposit failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const fetchAvailableStartups = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/startup/available`)
      if (response.ok) {
        const data = await response.json()
        setAvailableStartups(data.available_startups)
      }
    } catch (error) {
      console.error('Failed to fetch startups:', error)
    }
  }

  const fetchPortfolio = async () => {
    if (!investorData) return
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/investor/${investorData.user_id}/portfolio`)
      if (response.ok) {
        const data = await response.json()
        setPortfolio(data.investments)
      }
    } catch (error) {
      console.error('Failed to fetch portfolio:', error)
    }
  }

  const handleFunding = async (startupId: number) => {
    if (!investorData) return

    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/funding/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          investor_id: investorData.user_id,
          startup_id: startupId
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Funding successful! Amount: ${data.funded_amount} ALGO`)
        checkInvestorStatus()
        fetchAvailableStartups()
        fetchPortfolio()
      } else {
        const error = await response.json()
        alert(`Funding failed: ${error.detail}`)
      }
    } catch (error) {
      console.error('Funding failed:', error)
      alert('Funding failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'high': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">
                Investor Dashboard
              </h1>
            </div>
            <WalletConnect 
              onConnect={(address) => {
                setIsConnected(true)
                setWalletAddress(address)
              }}
              onDisconnect={() => {
                setIsConnected(false)
                setWalletAddress('')
                setInvestorData(null)
                setShowRegistration(false)
              }}
            />
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {!isConnected ? (
          // Not Connected State
          <div className="text-center py-12">
            <CurrencyDollarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h2 className="mt-4 text-lg font-medium text-gray-900">
              Connect Your Wallet
            </h2>
            <p className="mt-2 text-gray-600">
              Connect your Algorand wallet to access the investor dashboard
            </p>
          </div>
        ) : loading && !investorData ? (
          // Loading State
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your investor data...</p>
          </div>
        ) : showRegistration ? (
          // Registration Form
          <div className="max-w-2xl mx-auto">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Register as Investor
              </h2>
              <p className="text-gray-600 mb-6">
                Join our marketplace and start funding promising startups on Algorand.
              </p>

              <form onSubmit={handleRegistration} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={registrationForm.name}
                    onChange={(e) => setRegistrationForm(prev => ({...prev, name: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Investment Capacity (ALGO) *
                  </label>
                  <input
                    type="number"
                    required
                    min="1000"
                    value={registrationForm.investment_capacity}
                    onChange={(e) => setRegistrationForm(prev => ({...prev, investment_capacity: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 100000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Risk Preference
                  </label>
                  <select
                    value={registrationForm.risk_preference}
                    onChange={(e) => setRegistrationForm(prev => ({...prev, risk_preference: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="conservative">Conservative (Low risk, 6-8% returns)</option>
                    <option value="moderate">Moderate (Medium risk, 8-12% returns)</option>
                    <option value="aggressive">Aggressive (High risk, 12%+ returns)</option>
                  </select>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Investor Benefits</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• AI-powered startup screening</li>
                    <li>• Transparent risk assessment</li>
                    <li>• Automated returns via smart contracts</li>
                    <li>• Diversified portfolio options</li>
                  </ul>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
                >
                  {loading ? 'Registering...' : 'Register as Investor'}
                </button>
              </form>
            </div>
          </div>
        ) : investorData ? (
          // Investor Dashboard
          <div className="space-y-6">
            {/* Welcome Header */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Welcome back, {investorData.name}! 💰
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Manage your investments and discover new opportunities
                  </p>
                </div>
                <Button 
                  onClick={() => setShowDepositModal(true)}
                  className="bg-green-600 text-white hover:bg-green-700"
                >
                  <PlusIcon className="mr-2 h-4 w-4" />
                  Deposit ALGO
                </Button>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Available Balance</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {investorData.current_balance.toLocaleString()} ALGO
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <ArrowUpIcon className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Total Invested</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {investorData.total_invested.toLocaleString()} ALGO
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <TrophyIcon className="h-8 w-8 text-yellow-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Yield Earned</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {investorData.yield_earned.toLocaleString()} ALGO
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <UserGroupIcon className="h-8 w-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Active Investments</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {investorData.active_investments}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div className="bg-white shadow rounded-lg">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8 px-6">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'overview'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('opportunities')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'opportunities'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Opportunities ({availableStartups.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('portfolio')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'portfolio'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Portfolio ({portfolio.length})
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-4">Quick Actions</h4>
                        <div className="space-y-3">
                          <Button 
                            onClick={() => setShowDepositModal(true)}
                            className="w-full bg-green-600 text-white hover:bg-green-700"
                          >
                            <PlusIcon className="mr-2 h-4 w-4" />
                            Deposit More ALGO
                          </Button>
                          <Button 
                            onClick={() => setActiveTab('opportunities')}
                            className="w-full bg-blue-600 text-white hover:bg-blue-700"
                          >
                            <EyeIcon className="mr-2 h-4 w-4" />
                            Browse Startups
                          </Button>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-900 mb-4">Investment Summary</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Total Portfolio Value:</span>
                            <span className="font-medium">
                              {(investorData.current_balance + investorData.total_invested).toLocaleString()} ALGO
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">ROI:</span>
                            <span className="font-medium text-green-600">
                              +{investorData.total_invested > 0 ? 
                                ((investorData.yield_earned / investorData.total_invested) * 100).toFixed(2) : 0}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Average Return:</span>
                            <span className="font-medium">8.5%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'opportunities' && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-4">
                      Available Investment Opportunities
                    </h4>
                    {availableStartups.length === 0 ? (
                      <div className="text-center py-8">
                        <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="mt-4 text-gray-600">No startups seeking funding at the moment</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 gap-6">
                        {availableStartups.map((startup) => (
                          <div key={startup.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h5 className="font-semibold text-gray-900">{startup.name}</h5>
                                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskColor(startup.risk_level)}`}>
                                    {startup.risk_level} Risk
                                  </span>
                                  <span className="text-sm text-gray-600">
                                    Score: {startup.credit_score}
                                  </span>
                                </div>
                                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                                  {startup.business_description}
                                </p>
                                <div className="grid grid-cols-3 gap-4 text-sm">
                                  <div>
                                    <span className="text-gray-600">Amount:</span>
                                    <p className="font-medium">{startup.requested_amount.toLocaleString()} ALGO</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-600">Interest Rate:</span>
                                    <p className="font-medium">{startup.interest_rate}%</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-600">Term:</span>
                                    <p className="font-medium">{startup.loan_term_months} months</p>
                                  </div>
                                </div>
                              </div>
                              <div className="ml-4">
                                <Button
                                  onClick={() => handleFunding(startup.id)}
                                  disabled={loading || investorData.current_balance < startup.requested_amount}
                                  className="bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                                >
                                  {investorData.current_balance < startup.requested_amount ? 'Insufficient Balance' : 'Fund Now'}
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'portfolio' && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-4">Your Investment Portfolio</h4>
                    {portfolio.length === 0 ? (
                      <div className="text-center py-8">
                        <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="mt-4 text-gray-600">No investments yet</p>
                        <Button 
                          onClick={() => setActiveTab('opportunities')}
                          className="mt-4 bg-blue-600 text-white hover:bg-blue-700"
                        >
                          Browse Opportunities
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {portfolio.map((investment, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <h5 className="font-semibold text-gray-900">{investment.startup_name}</h5>
                                <div className="grid grid-cols-4 gap-4 mt-2 text-sm">
                                  <div>
                                    <span className="text-gray-600">Invested:</span>
                                    <p className="font-medium">{investment.invested_amount.toLocaleString()} ALGO</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-600">Interest:</span>
                                    <p className="font-medium">{investment.interest_rate}%</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-600">Expected Return:</span>
                                    <p className="font-medium">{investment.expected_return.toLocaleString()} ALGO</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-600">Profit:</span>
                                    <p className="font-medium text-green-600">+{investment.profit.toLocaleString()} ALGO</p>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                  investment.status === 'funded' ? 'bg-green-100 text-green-800' :
                                  investment.status === 'repaid' ? 'bg-blue-100 text-blue-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {investment.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Deposit Modal */}
      {showDepositModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Deposit ALGO</h3>
            <form onSubmit={handleDeposit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount (ALGO)
                </label>
                <input
                  type="number"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter amount"
                  required
                  min="1"
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Processing...' : 'Deposit'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowDepositModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
