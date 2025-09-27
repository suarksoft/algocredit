/**
 * Corporate Treasury Marketplace - 24 Hour Sprint
 * Connecting Investors with Startups on Algorand
 */

'use client'

import { useState, useEffect } from 'react'
import { WalletConnect } from '@/components/WalletConnect'
import { Button } from '@/components/Button'
import { 
  ChartBarIcon, 
  ShieldCheckIcon, 
  BoltIcon, 
  CpuChipIcon, 
  CurrencyDollarIcon, 
  UsersIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  BuildingOfficeIcon,
  TrophyIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'

interface MarketplaceStats {
  total_investors: number
  total_startups: number
  total_funding_volume: number
  available_opportunities: number
}

export default function HomePage() {
  const [stats, setStats] = useState<MarketplaceStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMarketplaceStats()
  }, [])

  const fetchMarketplaceStats = async () => {
    try {
      const response = await fetch('http://localhost:8002/marketplace/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      } else {
        console.error('Failed to fetch stats:', response.status)
        // Set mock data for demo
        setStats({
          total_investors: 0,
          total_startups: 0,
          total_funding_volume: 0,
          available_opportunities: 0
        })
      }
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch marketplace stats:', error)
      // Set mock data for demo
      setStats({
        total_investors: 0,
        total_startups: 0,
        total_funding_volume: 0,
        available_opportunities: 0
      })
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900/20">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="text-center">
            {/* Logo and Title */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Corporate Treasury
                </span>
              </h1>
              <p className="mt-4 text-xl text-gray-600 dark:text-gray-300">
                Connecting Investors with Startups on Algorand
              </p>
              <p className="mt-2 text-lg text-gray-500 dark:text-gray-400">
                24-Hour Sprint Marketplace 🚀
              </p>
            </div>

            {/* Value Proposition */}
            <div className="mb-12">
              <p className="mx-auto max-w-3xl text-lg leading-8 text-gray-700 dark:text-gray-300">
                Investors fund promising startups directly on Algorand blockchain. 
                AI-powered matching, instant settlements, and transparent returns. 
                Join the future of startup financing.
              </p>
            </div>

            {/* Wallet Connection */}
            <div className="mb-12">
              <WalletConnect />
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Link href="/investor">
                <Button className="bg-blue-600 text-white hover:bg-blue-700">
                  <CurrencyDollarIcon className="mr-2 h-5 w-5" />
                  I'm an Investor
                  <ArrowRightIcon className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/startup">
                <Button className="bg-purple-600 text-white hover:bg-purple-700">
                  <BuildingOfficeIcon className="mr-2 h-5 w-5" />
                  I'm a Startup
                  <ArrowRightIcon className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Live Stats Section */}
      <div className="bg-white/50 py-16 backdrop-blur dark:bg-gray-800/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Live Marketplace Stats
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Real-time data from our 24-hour sprint
            </p>
          </div>
          
          {loading ? (
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="text-center">
                  <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded w-16 mx-auto mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-24 mx-auto"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {stats?.total_investors || 0}
                </div>
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Active Investors
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {stats?.total_startups || 0}
                </div>
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Registered Startups
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {stats?.total_funding_volume || 0} ALGO
                </div>
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Total Funding Volume
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                  {stats?.available_opportunities || 0}
                </div>
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Available Opportunities
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
              Why Corporate Treasury?
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
              The fastest way to connect capital with innovation
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 - For Investors */}
            <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
              <div className="mb-4 inline-flex rounded-lg bg-blue-100 p-3 dark:bg-blue-900/40">
                <CurrencyDollarIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                High Yield Investments
              </h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Earn 6-12% returns by funding promising startups. 
                AI-powered risk assessment ensures quality opportunities.
              </p>
            </div>

            {/* Feature 2 - For Startups */}
            <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
              <div className="mb-4 inline-flex rounded-lg bg-purple-100 p-3 dark:bg-purple-900/40">
                <BoltIcon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Instant Funding
              </h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Get funded in minutes, not months. Smart contracts 
                automate the entire process from application to funding.
              </p>
            </div>

            {/* Feature 3 - Algorand */}
            <div className="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
              <div className="mb-4 inline-flex rounded-lg bg-green-100 p-3 dark:bg-green-900/40">
                <ShieldCheckIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Algorand Powered
              </h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                3-second finality, $0.001 transaction fees, and carbon-negative 
                operations. The future of sustainable finance.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* How it Works Section */}
      <div className="bg-gray-50 py-16 dark:bg-gray-900/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
              How It Works
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
              Simple 3-step process for both investors and startups
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-2">
            {/* Investor Flow */}
            <div className="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
              <h3 className="text-xl font-semibold text-blue-600 mb-6">
                For Investors 💰
              </h3>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white text-sm font-semibold">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">Register & Deposit</h4>
                    <p className="text-gray-600 dark:text-gray-400">Connect wallet, register as investor, deposit ALGO</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white text-sm font-semibold">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">Browse Opportunities</h4>
                    <p className="text-gray-600 dark:text-gray-400">Review AI-scored startups and their funding requests</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white text-sm font-semibold">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">Fund & Earn</h4>
                    <p className="text-gray-600 dark:text-gray-400">One-click funding with automatic returns</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Startup Flow */}
            <div className="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
              <h3 className="text-xl font-semibold text-purple-600 mb-6">
                For Startups 🚀
              </h3>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-white text-sm font-semibold">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">Apply & Get Scored</h4>
                    <p className="text-gray-600 dark:text-gray-400">Submit application, get AI credit score instantly</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-white text-sm font-semibold">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">Get Matched</h4>
                    <p className="text-gray-600 dark:text-gray-400">AI matches you with suitable investors</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-white text-sm font-semibold">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">Receive Funds</h4>
                    <p className="text-gray-600 dark:text-gray-400">Instant funding via smart contract</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white">
            Ready to Start?
          </h2>
          <p className="mt-4 text-xl text-blue-100">
            Join the 24-hour sprint marketplace revolution
          </p>
          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/investor">
              <Button className="bg-white text-blue-600 hover:bg-gray-100">
                <CurrencyDollarIcon className="mr-2 h-5 w-5" />
                Start Investing
              </Button>
            </Link>
            <Link href="/startup">
              <Button variant="secondary" className="border-white text-white hover:bg-white/10">
                <BuildingOfficeIcon className="mr-2 h-5 w-5" />
                Get Funding
              </Button>
            </Link>
          </div>
          
          <div className="mt-8 text-center">
            <p className="text-blue-100 text-sm">
              🚀 Built in 24 hours for Algorand Hackathon
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
