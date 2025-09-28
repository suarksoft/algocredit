/**
 * Security Dashboard Page
 * Web3 Security Analytics and API Management
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/Button'
import { WalletConnect } from '@/components/WalletConnect'
import { useWalletStore } from '@/stores/walletStore'
import { useSecurityStore } from '@/stores/securityStore'
import SecurityDashboard from '@/components/SecurityDashboard'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  CreditCardIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  PlusIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface LoanData {
  id: string
  amount: number
  approvedAmount: number
  interestRate: number
  term: number
  status: 'pending' | 'approved' | 'active' | 'completed' | 'defaulted'
  applicationDate: string
  dueDate?: string
  remainingBalance: number
  nextPaymentDate?: string
  nextPaymentAmount: number
}

interface CreditScoreData {
  score: number
  onChainScore: number
  offChainScore: number
  riskLevel: string
  lastUpdated: string
}

export default function DashboardPage() {
  const { isConnected, walletAddress } = useWalletStore()
  const { 
    apiKey, 
    securityScore, 
    threatLevel, 
    dashboard,
    loadSecurityDashboard 
  } = useSecurityStore()
  
  const [loans, setLoans] = useState<LoanData[]>([])
  const [creditScore, setCreditScore] = useState<CreditScoreData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Mock data - replace with actual API calls
    const mockLoans: LoanData[] = [
      {
        id: 'loan_001',
        amount: 50000,
        approvedAmount: 45000,
        interestRate: 8.5,
        term: 12,
        status: 'active',
        applicationDate: '2025-09-15',
        dueDate: '2026-09-15',
        remainingBalance: 38000,
        nextPaymentDate: '2025-10-15',
        nextPaymentAmount: 4200
      },
      {
        id: 'loan_002',
        amount: 25000,
        approvedAmount: 25000,
        interestRate: 7.2,
        term: 24,
        status: 'completed',
        applicationDate: '2024-06-01',
        dueDate: '2026-06-01',
        remainingBalance: 0,
        nextPaymentAmount: 0
      },
      {
        id: 'loan_003',
        amount: 75000,
        approvedAmount: 0,
        interestRate: 0,
        term: 18,
        status: 'pending',
        applicationDate: '2025-09-20',
        remainingBalance: 0,
        nextPaymentAmount: 0
      }
    ]

    const mockCreditScore: CreditScoreData = {
      score: 742,
      onChainScore: 68.5,
      offChainScore: 81.2,
      riskLevel: 'medium',
      lastUpdated: '2025-09-23'
    }

    setTimeout(() => {
      setLoans(mockLoans)
      setCreditScore(mockCreditScore)
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-400'
      case 'active':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400'
      case 'completed':
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-300'
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'defaulted':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600'
      case 'medium':
        return 'text-yellow-600'
      case 'high':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  // Show wallet connection requirement if not connected
  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900/20">
        <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Dashboard
            </h1>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
              Connect your wallet to view your loan portfolio and credit score
            </p>
          </div>
          <div className="mx-auto max-w-2xl">
            <WalletConnect />
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <ArrowPathIcon className="mx-auto h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Loading your dashboard...
          </p>
        </div>
      </div>
    )
  }

  const activeLoans = loans.filter(loan => loan.status === 'active')
  const totalBorrowed = activeLoans.reduce((sum, loan) => sum + loan.approvedAmount, 0)
  const totalRemaining = activeLoans.reduce((sum, loan) => sum + loan.remainingBalance, 0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900/20">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Security Dashboard
            </h1>
            <p className="mt-2 text-lg text-gray-600 dark:text-gray-300">
              Web3 Security Analytics and API Management
            </p>
            {apiKey && (
              <div className="mt-2 flex items-center gap-2">
                <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600 dark:text-green-400 font-medium">
                  API Key Active: {apiKey.slice(0, 12)}...
                </span>
              </div>
            )}
          </div>
          <div className="flex gap-3">
            <Link href="/apply">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <PlusIcon className="mr-2 h-4 w-4" />
                Apply for Loan
              </Button>
            </Link>
            <Button variant="outline" onClick={() => loadSecurityDashboard()}>
              <ArrowPathIcon className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CreditCardIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Credit Score
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {creditScore?.score}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Total Borrowed
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {totalBorrowed.toLocaleString()} ALGO
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Remaining Balance
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {totalRemaining.toLocaleString()} ALGO
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Active Loans
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {activeLoans.length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Security Dashboard Integration */}
        {apiKey && (
          <div className="mb-8">
            <SecurityDashboard apiKey={apiKey} />
          </div>
        )}

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Credit Score Details */}
          <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Credit Score Details
            </h2>
            
            {creditScore && (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">
                    {creditScore.score}
                  </div>
                  <div className={`text-sm font-medium ${getRiskColor(creditScore.riskLevel)}`}>
                    {creditScore.riskLevel.toUpperCase()} RISK
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">On-Chain Score</span>
                    <span className="font-medium">{creditScore.onChainScore}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Off-Chain Score</span>
                    <span className="font-medium">{creditScore.offChainScore}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Last Updated</span>
                    <span className="font-medium">{creditScore.lastUpdated}</span>
                  </div>
                </div>

                <Button variant="secondary" className="w-full">
                  <ArrowPathIcon className="mr-2 h-4 w-4" />
                  Refresh Score
                </Button>
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Loan Portfolio
                </h2>
                <Button variant="secondary">
                  <ArrowDownTrayIcon className="mr-2 h-4 w-4" />
                  Export
                </Button>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Loan ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Remaining
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Next Payment
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
                    {loans.map((loan) => (
                      <tr key={loan.id}>
                        <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                          {loan.id}
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                          {loan.approvedAmount > 0 ? loan.approvedAmount.toLocaleString() : loan.amount.toLocaleString()} ALGO
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm">
                          <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(loan.status)}`}>
                            {loan.status}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                          {loan.remainingBalance.toLocaleString()} ALGO
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                          {loan.nextPaymentDate ? (
                            <div>
                              <div>{loan.nextPaymentDate}</div>
                              <div className="text-xs">{loan.nextPaymentAmount.toLocaleString()} ALGO</div>
                            </div>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-sm font-medium">
                          <Button variant="secondary">
                            <EyeIcon className="mr-1 h-3 w-3" />
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Next Payment Alert */}
        {activeLoans.length > 0 && (
          <div className="mt-8 rounded-lg border-l-4 border-yellow-400 bg-yellow-50 p-4 dark:bg-yellow-900/20">
            <div className="flex">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  <strong>Upcoming Payment:</strong> You have a payment of{' '}
                  {activeLoans[0].nextPaymentAmount.toLocaleString()} ALGO due on{' '}
                  {activeLoans[0].nextPaymentDate}
                </p>
                <div className="mt-2">
                  <Button className="bg-yellow-600 hover:bg-yellow-700">
                    Make Payment
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
