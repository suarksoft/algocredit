/**
 * Loan Application Page
 * Multi-step loan application with AI credit scoring
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/Button'
import { WalletConnect } from '@/components/WalletConnect'
import { useWalletStore } from '@/stores/walletStore'
import { useSecurityStore } from '@/stores/securityStore'
import SecurityDashboard from '@/components/SecurityDashboard'
import { 
  CreditCardIcon, 
  BuildingOffice2Icon, 
  ChartBarIcon, 
  UsersIcon, 
  CurrencyDollarIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  ArrowRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline'

interface LoanApplicationData {
  // Loan details
  requestedAmount: number
  loanTerm: number
  purpose: string
  
  // Business information
  companyName: string
  industry: string
  foundingDate: string
  monthlyRevenue: number
  userCount: number
  userGrowthRate: number
  
  // Team information
  teamSize: number
  teamExperience: number
  
  // Contact information
  contactEmail: string
  contactPhone: string
}

export default function ApplyPage() {
  const { isConnected, walletAddress } = useWalletStore()
  const { 
    getCreditScore, 
    isLoadingScore, 
    securityScore, 
    threatLevel,
    lastError,
    clearError 
  } = useSecurityStore()
  
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [creditScoreData, setCreditScoreData] = useState(null)
  const [showSecurityDashboard, setShowSecurityDashboard] = useState(false)
  const [applicationData, setApplicationData] = useState<LoanApplicationData>({
    requestedAmount: 50000,
    loanTerm: 12,
    purpose: '',
    companyName: '',
    industry: '',
    foundingDate: '',
    monthlyRevenue: 0,
    userCount: 0,
    userGrowthRate: 0,
    teamSize: 1,
    teamExperience: 0,
    contactEmail: '',
    contactPhone: ''
  })

  const totalSteps = 4

  const updateData = (field: keyof LoanApplicationData, value: any) => {
    setApplicationData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    clearError()
    
    try {
      if (!walletAddress) {
        throw new Error('Wallet not connected')
      }

      // Step 1: Get AI Credit Score with Security Validation
      console.log('🔍 Getting secure credit score for wallet:', walletAddress)
      const creditData = await getCreditScore(walletAddress)
      setCreditScoreData(creditData)
      
      console.log('✅ Credit Score Result:', creditData)

      // Step 2: Submit Loan Application with Business Data
      const loanApplicationPayload = {
        wallet_address: walletAddress,
        requested_amount: applicationData.requestedAmount * 1000000, // Convert to microAlgo
        loan_term_months: applicationData.loanTerm,
        purpose: applicationData.purpose,
        business_data: {
          company_name: applicationData.companyName,
          industry: applicationData.industry,
          founding_date: applicationData.foundingDate,
          monthly_revenue: applicationData.monthlyRevenue,
          user_count: applicationData.userCount,
          user_growth_rate: applicationData.userGrowthRate,
          team_size: applicationData.teamSize,
          team_experience: applicationData.teamExperience,
        }
      }

      console.log('📝 Submitting secure loan application:', loanApplicationPayload)
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8005'
      const loanResponse = await fetch(`${apiBaseUrl}/api/v1/loans/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_ALGOCREDIT_API_KEY || 'demo_key'}`
        },
        body: JSON.stringify(loanApplicationPayload)
      })

      if (!loanResponse.ok) {
        const errorData = await loanResponse.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to submit loan application')
      }

      const loanResult = await loanResponse.json()
      console.log('✅ Loan Application Result:', loanResult)

      // Show professional success modal with security info
      setShowSecurityDashboard(true)
      
      // Create detailed success message
      const successMessage = `🎉 Application Submitted Successfully!

🧠 AI Credit Analysis:
• Credit Score: ${creditData.credit_score}/850
• Risk Level: ${creditData.risk_level.toUpperCase()}
• Max Loan Amount: ${(creditData.max_loan_amount / 1000000).toFixed(2)} ALGO
• Recommended Rate: ${creditData.recommended_interest_rate}%

🔒 Security Validation:
• API Tier: ${creditData.security_context.api_key_tier.toUpperCase()}
• Threat Score: ${creditData.security_context.threat_score}/10
• Validation: PASSED ✅

💰 Loan Decision:
• Status: ${loanResult.status.toUpperCase()}
${loanResult.approved_amount ? `• Approved Amount: ${(loanResult.approved_amount / 1000000).toFixed(2)} ALGO` : ''}
${loanResult.monthly_payment ? `• Monthly Payment: ${(loanResult.monthly_payment / 1000000).toFixed(2)} ALGO` : ''}

🚀 Next Steps:
• Check your dashboard for updates
• Smart contract deployment will follow
• Funds will be available within 24 hours`

      alert(successMessage)
      
    } catch (error) {
      console.error('❌ Application submission failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      alert(`🚨 Security Error: ${errorMessage}

Please check:
• Wallet connection
• API key validity  
• Network connectivity
• Try again in a few moments`)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Show wallet connection requirement if not connected
  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900">
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-32 h-80 w-80 rounded-full bg-gradient-to-br from-blue-400/20 to-purple-600/20 blur-3xl"></div>
          <div className="absolute -bottom-40 -left-32 h-80 w-80 rounded-full bg-gradient-to-tr from-indigo-400/20 to-blue-600/20 blur-3xl"></div>
        </div>
        
        <div className="relative mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
          <div className="text-center mb-8 sm:mb-12">
            <div className="mb-4">
              <div className="mx-auto h-16 w-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center mb-6">
                <CurrencyDollarIcon className="h-8 w-8 text-white" />
              </div>
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              Apply for a Loan
            </h1>
            <p className="mt-4 text-base sm:text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Connect your Algorand wallet to start your loan application with AI-powered instant assessment
            </p>
          </div>

          <div className="mx-auto max-w-2xl">
            <div className="backdrop-blur-sm bg-white/70 dark:bg-slate-800/70 rounded-2xl p-6 sm:p-8 shadow-xl border border-white/20 dark:border-slate-700/50">
              <WalletConnect />
            </div>
            
            <div className="mt-6 sm:mt-8 backdrop-blur-sm bg-blue-50/80 dark:bg-blue-900/30 rounded-2xl p-6 sm:p-8 border border-blue-200/50 dark:border-blue-800/50">
              <h3 className="text-lg sm:text-xl font-semibold text-blue-900 dark:text-blue-100 mb-4">
                Why do I need to connect my wallet?
              </h3>
              <ul className="space-y-3 text-sm sm:text-base">
                <li className="flex items-start gap-3 text-blue-800 dark:text-blue-200">
                  <div className="flex-shrink-0 mt-0.5">
                    <CheckCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <span>AI analysis of your transaction history for credit scoring</span>
                </li>
                <li className="flex items-start gap-3 text-blue-800 dark:text-blue-200">
                  <div className="flex-shrink-0 mt-0.5">
                    <CheckCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <span>Secure loan disbursement directly to your wallet</span>
                </li>
                <li className="flex items-start gap-3 text-blue-800 dark:text-blue-200">
                  <div className="flex-shrink-0 mt-0.5">
                    <CheckCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <span>Transparent, on-chain loan management</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-32 h-80 w-80 rounded-full bg-gradient-to-br from-blue-400/20 to-purple-600/20 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-32 h-80 w-80 rounded-full bg-gradient-to-tr from-indigo-400/20 to-blue-600/20 blur-3xl"></div>
      </div>
      
      <div className="relative mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12">
          <div className="mb-4">
            <div className="mx-auto h-16 w-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center mb-6">
              <CurrencyDollarIcon className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Apply for a Loan
          </h1>
          <p className="mt-4 text-base sm:text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Get instant funding with AI-powered credit assessment and enterprise Web3 security
          </p>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-full">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              <p className="text-sm font-medium text-green-700 dark:text-green-300">
                Connected: {walletAddress && `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`}
              </p>
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 rounded-full">
              <div className="h-2 w-2 rounded-full bg-blue-500"></div>
              <p className="text-sm font-medium text-blue-700 dark:text-blue-300">
                Security: {securityScore > 0 ? `${securityScore.toFixed(1)}/10` : 'Protected'}
              </p>
            </div>
            {threatLevel > 5 && (
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 dark:bg-orange-900/30 rounded-full">
                <div className="h-2 w-2 rounded-full bg-orange-500 animate-pulse"></div>
                <p className="text-sm font-medium text-orange-700 dark:text-orange-300">
                  Threat Level: High
                </p>
              </div>
            )}
          </div>

          {/* Security Dashboard Toggle */}
          {(securityScore > 0 || creditScoreData) && (
            <div className="mt-6">
              <button
                onClick={() => setShowSecurityDashboard(!showSecurityDashboard)}
                className="mx-auto flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                🔒 {showSecurityDashboard ? 'Hide' : 'Show'} Security Analysis
              </button>
              
              {showSecurityDashboard && (
                <div className="mt-4 max-w-2xl mx-auto">
                  <SecurityDashboard compact={true} />
                  {creditScoreData && (
                    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-3">🧠 AI Credit Analysis</h4>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Credit Score:</span>
                          <span className="font-bold text-blue-600 dark:text-blue-400">{creditScoreData.credit_score}/850</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Risk Level:</span>
                          <span className="font-bold text-blue-600 dark:text-blue-400 capitalize">{creditScoreData.risk_level}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Max Loan:</span>
                          <span className="font-bold text-blue-600 dark:text-blue-400">{(creditScoreData.max_loan_amount / 1000000).toFixed(2)} ALGO</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Threat Score:</span>
                          <span className="font-bold text-blue-600 dark:text-blue-400">{creditScoreData.security_context.threat_score}/10</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mb-8 sm:mb-12">
          <div className="backdrop-blur-sm bg-white/60 dark:bg-slate-800/60 rounded-2xl p-4 sm:p-6 border border-white/30 dark:border-slate-700/50">
            <div className="flex items-center justify-between">
              {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
                <div key={step} className="flex items-center flex-1">
                  <div className="flex flex-col items-center">
                    <div
                      className={`flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-full border-2 transition-all duration-300 ${
                        step <= currentStep
                          ? 'border-blue-600 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg transform scale-105'
                          : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700 text-gray-500 dark:text-gray-400'
                      }`}
                    >
                      {step < currentStep ? (
                        <CheckCircleIcon className="h-5 w-5 sm:h-6 sm:w-6" />
                      ) : (
                        <span className="text-sm sm:text-base font-semibold">{step}</span>
                      )}
                    </div>
                  </div>
                  {step < totalSteps && (
                    <div className="flex-1 mx-2 sm:mx-4">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          step < currentStep 
                            ? 'bg-gradient-to-r from-blue-500 to-purple-600' 
                            : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs sm:text-sm text-center">
              <span className={`font-medium ${currentStep >= 1 ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'}`}>
                Loan Details
              </span>
              <span className={`font-medium ${currentStep >= 2 ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'}`}>
                Business Info
              </span>
              <span className={`font-medium ${currentStep >= 3 ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'}`}>
                Team Details
              </span>
              <span className={`font-medium ${currentStep >= 4 ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'}`}>
                Review & Submit
              </span>
            </div>
          </div>
        </div>

        {/* Form Content */}
        <div className="backdrop-blur-sm bg-white/70 dark:bg-slate-800/70 rounded-2xl p-6 sm:p-8 lg:p-10 shadow-2xl border border-white/30 dark:border-slate-700/50">
          {/* Step 1: Loan Details */}
          {currentStep === 1 && (
            <div className="space-y-6 sm:space-y-8">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <CurrencyDollarIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  Loan Details
                </h2>
              </div>

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Requested Amount (ALGO)
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={applicationData.requestedAmount}
                      onChange={(e) => updateData('requestedAmount', Number(e.target.value))}
                      className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 transition-all duration-200 text-lg font-medium"
                      min="1000"
                      max="1000000"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-4">
                      <span className="text-gray-500 dark:text-gray-400 text-sm font-medium">ALGO</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Minimum: 1,000 ALGO • Maximum: 1,000,000 ALGO</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Loan Term (Months)
                  </label>
                  <select
                    value={applicationData.loanTerm}
                    onChange={(e) => updateData('loanTerm', Number(e.target.value))}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:ring-2 focus:ring-inset focus:ring-blue-600 transition-all duration-200 text-lg font-medium"
                  >
                    <option value={6}>6 months</option>
                    <option value={12}>12 months</option>
                    <option value={24}>24 months</option>
                    <option value={36}>36 months</option>
                    <option value={48}>48 months</option>
                    <option value={60}>60 months</option>
                  </select>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Choose your preferred repayment period</p>
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Loan Purpose
                </label>
                <textarea
                  value={applicationData.purpose}
                  onChange={(e) => updateData('purpose', e.target.value)}
                  rows={4}
                  className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 transition-all duration-200 resize-none"
                  placeholder="Describe how you plan to use the loan funds (e.g., expand operations, purchase equipment, working capital)..."
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">Provide details about your intended use of funds</p>
              </div>
            </div>
          )}

          {/* Step 2: Business Information */}
          {currentStep === 2 && (
            <div className="space-y-6 sm:space-y-8">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <BuildingOffice2Icon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  Business Information
                </h2>
              </div>

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={applicationData.companyName}
                    onChange={(e) => updateData('companyName', e.target.value)}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition-all duration-200 text-lg font-medium"
                    placeholder="Enter your company name"
                    required
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">Legal name of your business</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Industry
                  </label>
                  <select
                    value={applicationData.industry}
                    onChange={(e) => updateData('industry', e.target.value)}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition-all duration-200 text-lg font-medium"
                    required
                  >
                    <option value="">Select Industry</option>
                    <option value="fintech">FinTech</option>
                    <option value="healthcare">Healthcare</option>
                    <option value="ecommerce">E-commerce</option>
                    <option value="saas">SaaS</option>
                    <option value="blockchain">Blockchain/Crypto</option>
                    <option value="ai">AI/Machine Learning</option>
                    <option value="gaming">Gaming</option>
                    <option value="other">Other</option>
                  </select>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Primary business sector</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Founding Date
                  </label>
                  <input
                    type="date"
                    value={applicationData.foundingDate}
                    onChange={(e) => updateData('foundingDate', e.target.value)}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition-all duration-200 text-lg font-medium"
                    required
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">When was your company founded?</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Monthly Revenue ($)
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={applicationData.monthlyRevenue}
                      onChange={(e) => updateData('monthlyRevenue', Number(e.target.value))}
                      className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 pl-8 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition-all duration-200 text-lg font-medium"
                      placeholder="0"
                      min="0"
                    />
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3">
                      <span className="text-gray-500 dark:text-gray-400 text-sm font-medium">$</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Average monthly revenue in USD</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    User Count
                  </label>
                  <input
                    type="number"
                    value={applicationData.userCount}
                    onChange={(e) => updateData('userCount', Number(e.target.value))}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition-all duration-200 text-lg font-medium"
                    placeholder="0"
                    min="0"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total number of active users</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Monthly User Growth Rate (%)
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={applicationData.userGrowthRate}
                      onChange={(e) => updateData('userGrowthRate', Number(e.target.value))}
                      className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition-all duration-200 text-lg font-medium"
                      placeholder="0.0"
                      min="0"
                      step="0.1"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-4">
                      <span className="text-gray-500 dark:text-gray-400 text-sm font-medium">%</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Average monthly growth percentage</p>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Team Details */}
          {currentStep === 3 && (
            <div className="space-y-6 sm:space-y-8">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <UsersIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  Team Details
                </h2>
              </div>

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Team Size
                  </label>
                  <input
                    type="number"
                    value={applicationData.teamSize}
                    onChange={(e) => updateData('teamSize', Number(e.target.value))}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-green-600 transition-all duration-200 text-lg font-medium"
                    placeholder="1"
                    min="1"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">Number of team members</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Average Team Experience (Years)
                  </label>
                  <input
                    type="number"
                    value={applicationData.teamExperience}
                    onChange={(e) => updateData('teamExperience', Number(e.target.value))}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-green-600 transition-all duration-200 text-lg font-medium"
                    placeholder="0.0"
                    min="0"
                    step="0.5"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">Years of relevant industry experience</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    value={applicationData.contactEmail}
                    onChange={(e) => updateData('contactEmail', e.target.value)}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-green-600 transition-all duration-200 text-lg font-medium"
                    placeholder="contact@company.com"
                    required
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">Primary contact email address</p>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    value={applicationData.contactPhone}
                    onChange={(e) => updateData('contactPhone', e.target.value)}
                    className="block w-full rounded-xl border-0 bg-white/50 dark:bg-slate-700/50 px-4 py-3 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-green-600 transition-all duration-200 text-lg font-medium"
                    placeholder="+1 (555) 123-4567"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400">Optional contact phone number</p>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review & Submit */}
          {currentStep === 4 && (
            <div className="space-y-6 sm:space-y-8">
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <CheckCircleIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  Review & Submit
                </h2>
              </div>

              <div className="backdrop-blur-sm bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-slate-800/50 dark:to-slate-700/50 rounded-2xl p-6 sm:p-8 border border-blue-200/30 dark:border-slate-600/30">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                  Application Summary
                </h3>
                
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-4 border border-white/40 dark:border-slate-700/40">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Requested Amount</span>
                    <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{applicationData.requestedAmount.toLocaleString()} ALGO</p>
                  </div>
                  <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-4 border border-white/40 dark:border-slate-700/40">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Loan Term</span>
                    <p className="text-xl font-bold text-purple-600 dark:text-purple-400">{applicationData.loanTerm} months</p>
                  </div>
                  <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-4 border border-white/40 dark:border-slate-700/40">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Company</span>
                    <p className="text-lg font-bold text-gray-900 dark:text-white truncate">{applicationData.companyName || 'Not specified'}</p>
                  </div>
                  <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-4 border border-white/40 dark:border-slate-700/40">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Industry</span>
                    <p className="text-lg font-bold text-gray-900 dark:text-white capitalize">{applicationData.industry || 'Not specified'}</p>
                  </div>
                  <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-4 border border-white/40 dark:border-slate-700/40">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Monthly Revenue</span>
                    <p className="text-lg font-bold text-green-600 dark:text-green-400">${applicationData.monthlyRevenue.toLocaleString()}</p>
                  </div>
                  <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-4 border border-white/40 dark:border-slate-700/40">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Team Size</span>
                    <p className="text-lg font-bold text-indigo-600 dark:text-indigo-400">{applicationData.teamSize} members</p>
                  </div>
                </div>
              </div>

              <div className="backdrop-blur-sm bg-gradient-to-r from-indigo-50/50 to-blue-50/50 dark:from-indigo-900/30 dark:to-blue-900/30 rounded-2xl p-6 sm:p-8 border border-indigo-200/30 dark:border-indigo-800/30 text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6">
                  <ChartBarIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  AI Credit Assessment
                </h3>
                <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
                  Your application will be analyzed using our AI-powered credit scoring system
                  that combines on-chain wallet analysis with business metrics for instant assessment.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm">
                  <div className="flex items-center gap-2 bg-white/40 dark:bg-slate-800/40 rounded-full px-4 py-2">
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    <span>Wallet Analysis</span>
                  </div>
                  <div className="flex items-center gap-2 bg-white/40 dark:bg-slate-800/40 rounded-full px-4 py-2">
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    <span>Business Metrics</span>
                  </div>
                  <div className="flex items-center gap-2 bg-white/40 dark:bg-slate-800/40 rounded-full px-4 py-2">
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    <span>Risk Assessment</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="mt-8 sm:mt-12 flex flex-col sm:flex-row justify-between gap-4">
            <Button
              onClick={prevStep}
              variant="secondary"
              disabled={currentStep === 1}
              className={`${currentStep === 1 ? 'invisible' : ''} backdrop-blur-sm bg-white/60 dark:bg-slate-700/60 border-gray-300 dark:border-slate-600 hover:bg-white/80 dark:hover:bg-slate-700/80 transition-all duration-200 px-6 py-3 text-base font-semibold`}
            >
              <ArrowLeftIcon className="mr-2 h-5 w-5" />
              Previous
            </Button>

            {currentStep < totalSteps ? (
              <Button 
                onClick={nextStep}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3 text-base font-semibold"
              >
                Next Step
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3 text-base font-semibold"
              >
                {isSubmitting ? (
                  <>
                    <ArrowPathIcon className="mr-2 h-5 w-5 animate-spin" />
                    Processing Application...
                  </>
                ) : (
                  <>
                    Submit Application
                    <CheckCircleIcon className="ml-2 h-5 w-5" />
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
