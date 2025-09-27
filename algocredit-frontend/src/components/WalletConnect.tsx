/**
 * Wallet Connection Component
 * Handles Algorand wallet connection UI
 */

'use client'

import React, { useEffect } from 'react'
import { useWalletStore } from '@/stores/walletStore'
import { Button } from './Button'
import { 
  WalletIcon, 
  ArrowRightOnRectangleIcon, 
  ExclamationCircleIcon, 
  ArrowPathIcon 
} from '@heroicons/react/24/outline'

interface WalletConnectProps {
  onConnect?: (address: string) => void
  onDisconnect?: () => void
}

export function WalletConnect({ onConnect, onDisconnect }: WalletConnectProps = {}) {
  const {
    isConnected,
    isConnecting,
    walletAddress,
    balance,
    connectWallet,
    disconnectWallet,
    error,
    clearError,
  } = useWalletStore()

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  const formatBalance = (balance: number) => {
    return (balance / 1_000_000).toFixed(6) // Convert microAlgos to ALGO
  }

  // Handle connect/disconnect callbacks
  const handleConnect = async () => {
    try {
      await connectWallet()
      if (walletAddress && onConnect) {
        onConnect(walletAddress)
      }
    } catch (error) {
      console.error('Wallet connection failed:', error)
    }
  }

  const handleDisconnect = () => {
    disconnectWallet()
    if (onDisconnect) {
      onDisconnect()
    }
  }

  // Call onConnect when wallet becomes connected
  useEffect(() => {
    if (isConnected && walletAddress && onConnect) {
      onConnect(walletAddress)
    }
  }, [isConnected, walletAddress, onConnect])

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
        <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
          <ExclamationCircleIcon className="h-4 w-4" />
          <span className="text-sm font-medium">Wallet Error</span>
        </div>
        <p className="mt-1 text-sm text-red-700 dark:text-red-300">{error}</p>
        <Button
          onClick={clearError}
          variant="secondary"
          className="mt-2 border-red-200 text-red-800 hover:bg-red-100 dark:border-red-800 dark:text-red-200 dark:hover:bg-red-900/40"
        >
          Dismiss
        </Button>
      </div>
    )
  }

  if (isConnected && walletAddress) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-green-100 p-2 dark:bg-green-900/40">
              <WalletIcon className="h-4 w-4 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-green-800 dark:text-green-200">
                Wallet Connected
              </p>
              <p className="text-xs text-green-600 dark:text-green-400">
                {formatAddress(walletAddress)}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {formatBalance(balance)} ALGO
            </p>
            <Button
              onClick={handleDisconnect}
              variant="secondary"
              className="mt-1 h-6 border-green-200 px-2 text-xs text-green-700 hover:bg-green-100 dark:border-green-800 dark:text-green-300 dark:hover:bg-green-900/40"
            >
              <ArrowRightOnRectangleIcon className="mr-1 h-3 w-3" />
              Disconnect
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-gray-200/50 bg-gradient-to-r from-gray-50/80 to-blue-50/80 dark:from-slate-800/80 dark:to-slate-700/80 dark:border-slate-700/50 p-6 shadow-lg">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="rounded-full bg-gradient-to-r from-blue-500 to-purple-600 p-3 shadow-md">
            <WalletIcon className="h-6 w-6 text-white" />
          </div>
          <div className="text-center sm:text-left">
            <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Connect Algorand Wallet
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Connect to access AlgoCredit features
            </p>
          </div>
        </div>
        <Button
          onClick={handleConnect}
          disabled={isConnecting}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-6 py-3 text-base font-semibold whitespace-nowrap"
        >
          {isConnecting ? (
            <>
              <ArrowPathIcon className="mr-2 h-5 w-5 animate-spin" />
              Connecting...
            </>
          ) : (
            <>
              <WalletIcon className="mr-2 h-5 w-5" />
              Connect Pera Wallet
            </>
          )}
        </Button>
      </div>
    </div>
  )
}

/**
 * Compact Wallet Status Component for Header
 */
export function WalletStatus() {
  const {
    isConnected,
    isConnecting,
    walletAddress,
    balance,
    connectWallet,
    disconnectWallet,
  } = useWalletStore()

  if (isConnected && walletAddress) {
    return (
      <div className="flex items-center gap-2">
        <div className="rounded-lg bg-green-100 px-3 py-1 dark:bg-green-900/40">
          <span className="text-sm font-medium text-green-800 dark:text-green-200">
            {(balance / 1_000_000).toFixed(2)} ALGO
          </span>
        </div>
        <Button
          onClick={disconnectWallet}
          variant="secondary"
          className="h-8"
        >
          <ArrowRightOnRectangleIcon className="mr-1 h-3 w-3" />
          {formatAddress(walletAddress)}
        </Button>
      </div>
    )
  }

  return (
    <Button
      onClick={connectWallet}
      disabled={isConnecting}
      className="bg-blue-600 text-white hover:bg-blue-700"
    >
      {isConnecting ? (
        <ArrowPathIcon className="mr-2 h-3 w-3 animate-spin" />
      ) : (
        <WalletIcon className="mr-2 h-3 w-3" />
      )}
      {isConnecting ? 'Connecting...' : 'Connect Wallet'}
    </Button>
  )

  function formatAddress(address: string) {
    return `${address.slice(0, 4)}...${address.slice(-4)}`
  }
}
