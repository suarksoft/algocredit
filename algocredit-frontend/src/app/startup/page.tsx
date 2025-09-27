/**
 * Startup Dashboard - 24 Hour Sprint
 * Funding request, credit scoring, and status tracking
 */

'use client'

import { useState, useEffect } from 'react'
import { WalletConnect } from '@/components/WalletConnect'
import { Button } from '@/components/Button'
import { 
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  DocumentTextIcon,
  TrophyIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'

interface StartupData {
  user_id: number
  name: string
  wallet_address: string
  business_description: string
  requested_amount: number
  credit_score: number
  interest_rate: number
  funding_status: string
  funded_amount: number
}

interface RegistrationForm {
  name: string
  business_description: string
  requested_amount: string
  loan_term_months: string
}

export default function StartupDashboard() {
  const [isConnected, setIsConnected] = useState(false)
  const [walletAddress, setWalletAddress] = useState('')
  const [startupData, setStartupData] = useState<StartupData | null>(null)
  const [loading, setLoading] = useState(false)
  const [showRegistration, setShowRegistration] = useState(false)
  const [registrationForm, setRegistrationForm] = useState<RegistrationForm>({
    name: '',
    business_description: '',
    requested_amount: '',
    loan_term_months: '12'
  })

  useEffect(() => {
    if (isConnected && walletAddress) {
      checkStartupStatus()
    }
  }, [isConnected, walletAddress])

  const checkStartupStatus = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8001/user/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wallet_address: walletAddress,
          user_type: 'startup'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setStartupData(data)
      } else {
        // User not registered as startup
        setShowRegistration(true)
      }
    } catch (error) {
      console.error('Failed to check startup status:', error)
      setShowRegistration(true)
    } finally {
      setLoading(false)
    }
  }

  const handleRegistration = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8001/startup/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: registrationForm.name,
          wallet_address: walletAddress,
          business_description: registrationForm.business_description,
          requested_amount: parseInt(registrationForm.requested_amount),
          loan_term_months: parseInt(registrationForm.loan_term_months)
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Registration successful! Credit Score: ${data.credit_score}, Interest Rate: ${data.interest_rate}%`)
        setShowRegistration(false)
        checkStartupStatus()
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'seeking': return 'text-orange-600 bg-orange-100'
      case 'funded': return 'text-green-600 bg-green-100'
      case 'repaid': return 'text-blue-600 bg-blue-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'seeking': return <ClockIcon className="h-5 w-5" />
      case 'funded': return <CheckCircleIcon className="h-5 w-5" />
      case 'repaid': return <TrophyIcon className="h-5 w-5" />
      default: return <ExclamationTriangleIcon className="h-5 w-5" />
    }
  }

  const getCreditScoreColor = (score: number) => {
    if (score >= 750) return 'text-green-600'
    if (score >= 650) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <BuildingOfficeIcon className="h-8 w-8 text-purple-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">
                Startup Dashboard
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
                setStartupData(null)
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
            <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h2 className="mt-4 text-lg font-medium text-gray-900">
              Connect Your Wallet
            </h2>
            <p className="mt-2 text-gray-600">
              Connect your Algorand wallet to access the startup dashboard
            </p>
          </div>
        ) : loading ? (
          // Loading State
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your startup data...</p>
          </div>
        ) : showRegistration ? (
          // Registration Form
          <div className="max-w-2xl mx-auto">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Register Your Startup
              </h2>
              <p className="text-gray-600 mb-6">
                Complete your startup profile to get AI credit scoring and access funding opportunities.
              </p>

              <form onSubmit={handleRegistration} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Startup Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={registrationForm.name}
                    onChange={(e) => setRegistrationForm(prev => ({...prev, name: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Enter your startup name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Description *
                  </label>
                  <textarea
                    required
                    rows={4}
                    value={registrationForm.business_description}
                    onChange={(e) => setRegistrationForm(prev => ({...prev, business_description: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Describe your business, market, and how you'll use the funding..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Requested Amount (ALGO) *
                    </label>
                    <input
                      type="number"
                      required
                      min="1000"
                      max="1000000"
                      value={registrationForm.requested_amount}
                      onChange={(e) => setRegistrationForm(prev => ({...prev, requested_amount: e.target.value}))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="e.g., 50000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Loan Term (Months)
                    </label>
                    <select
                      value={registrationForm.loan_term_months}
                      onChange={(e) => setRegistrationForm(prev => ({...prev, loan_term_months: e.target.value}))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="6">6 months</option>
                      <option value="12">12 months</option>
                      <option value="18">18 months</option>
                      <option value="24">24 months</option>
                    </select>
                  </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">What happens next?</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• AI analyzes your request and generates a credit score</li>
                    <li>• Interest rate is calculated based on your score</li>
                    <li>• Your startup appears in investor marketplace</li>
                    <li>• Get matched with suitable investors</li>
                  </ul>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 font-semibold"
                >
                  {loading ? 'Registering...' : 'Register Startup'}
                </button>
              </form>
            </div>
          </div>
        ) : startupData ? (
          // Startup Dashboard
          <div className="space-y-6">
            {/* Welcome Header */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Welcome back, {startupData.name}! 👋
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Manage your funding request and track your progress
                  </p>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 ${getStatusColor(startupData.funding_status)}`}>
                  {getStatusIcon(startupData.funding_status)}
                  {startupData.funding_status.charAt(0).toUpperCase() + startupData.funding_status.slice(1)}
                </div>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <TrophyIcon className="h-8 w-8 text-yellow-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Credit Score</p>
                    <p className={`text-2xl font-bold ${getCreditScoreColor(startupData.credit_score)}`}>
                      {startupData.credit_score}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Requested Amount</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {startupData.requested_amount.toLocaleString()} ALGO
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <ChartBarIcon className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Interest Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {startupData.interest_rate}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <CheckCircleIcon className="h-8 w-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Funded Amount</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {startupData.funded_amount.toLocaleString()} ALGO
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Status-based Content */}
            {startupData.funding_status === 'seeking' && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🔍 Seeking Funding
                </h3>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
                  <p className="text-orange-800">
                    Your startup is now visible to investors in the marketplace. 
                    Investors can review your profile and fund your request.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Your Profile Highlights</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>✅ Credit Score: {startupData.credit_score} (AI-generated)</li>
                      <li>✅ Competitive Rate: {startupData.interest_rate}%</li>
                      <li>✅ Clear Business Plan</li>
                      <li>✅ Algorand Wallet Verified</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Next Steps</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• Wait for investor interest</li>
                      <li>• Review funding offers</li>
                      <li>• Accept suitable investor</li>
                      <li>• Receive instant funding</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {startupData.funding_status === 'funded' && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🎉 Congratulations! You're Funded
                </h3>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <p className="text-green-800">
                    Your startup has been successfully funded! The ALGO has been transferred to your wallet.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Funding Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Funded Amount:</span>
                        <span className="font-medium">{startupData.funded_amount.toLocaleString()} ALGO</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Interest Rate:</span>
                        <span className="font-medium">{startupData.interest_rate}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total to Repay:</span>
                        <span className="font-medium">
                          {Math.round(startupData.funded_amount * (1 + startupData.interest_rate/100)).toLocaleString()} ALGO
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Repayment</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      Use your funding wisely and repay when ready to build your credit history.
                    </p>
                    <Button className="bg-green-600 text-white hover:bg-green-700">
                      <CurrencyDollarIcon className="mr-2 h-4 w-4" />
                      Repay Loan
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {startupData.funding_status === 'repaid' && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🏆 Loan Successfully Repaid
                </h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <p className="text-blue-800">
                    Excellent! You've successfully repaid your loan. Your credit score has been updated.
                  </p>
                </div>
                
                <div className="text-center py-6">
                  <TrophyIcon className="mx-auto h-16 w-16 text-yellow-500 mb-4" />
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">
                    Ready for Your Next Funding Round?
                  </h4>
                  <p className="text-gray-600 mb-4">
                    Your successful repayment history makes you eligible for larger amounts at better rates.
                  </p>
                  <Button className="bg-purple-600 text-white hover:bg-purple-700">
                    <PlusIcon className="mr-2 h-4 w-4" />
                    Request New Funding
                  </Button>
                </div>
              </div>
            )}

            {/* Business Profile */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Business Profile
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Business Description
                  </label>
                  <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                    {startupData.business_description}
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Wallet Address
                    </label>
                    <p className="text-gray-900 font-mono text-sm bg-gray-50 p-2 rounded">
                      {startupData.wallet_address.slice(0, 6)}...{startupData.wallet_address.slice(-4)}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Risk Level
                    </label>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      startupData.credit_score > 700 ? 'bg-green-100 text-green-800' :
                      startupData.credit_score > 650 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {startupData.credit_score > 700 ? 'Low Risk' :
                       startupData.credit_score > 650 ? 'Medium Risk' : 'High Risk'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Error State
          <div className="text-center py-12">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
            <h2 className="mt-4 text-lg font-medium text-gray-900">
              Something went wrong
            </h2>
            <p className="mt-2 text-gray-600">
              Unable to load your startup data. Please try again.
            </p>
            <Button 
              onClick={() => window.location.reload()} 
              className="mt-4 bg-purple-600 text-white hover:bg-purple-700"
            >
              Retry
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
