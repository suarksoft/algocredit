'use client'

import React, { useState } from 'react'
import { PeraWalletConnect } from '@perawallet/connect'

export default function WalletTestPage() {
  const [status, setStatus] = useState('Not connected')
  const [address, setAddress] = useState('')
  const [error, setError] = useState('')

  // Initialize Pera Wallet for testing
  const initWallet = () => {
    try {
      // Try different initialization methods
      const wallet1 = new PeraWalletConnect({
        chainId: 416002
      })
      setStatus('Initialized with chainId')
      return wallet1
    } catch (e) {
      setError(`ChainId init failed: ${e}`)
      try {
        const wallet2 = new PeraWalletConnect()
        setStatus('Initialized without chainId')
        return wallet2
      } catch (e2) {
        setError(`All init failed: ${e2}`)
        return null
      }
    }
  }

  const testConnect = async () => {
    try {
      setStatus('Initializing...')
      setError('')
      
      const wallet = initWallet()
      if (!wallet) {
        setError('Failed to initialize wallet')
        return
      }

      setStatus('Connecting...')
      const accounts = await wallet.connect()
      
      if (accounts && accounts.length > 0) {
        setAddress(accounts[0])
        setStatus('Connected!')
      } else {
        setError('No accounts returned')
      }
      
    } catch (error: any) {
      console.error('Connection error:', error)
      setError(`Connection failed: ${error.message || error.toString()}`)
      setStatus('Connection failed')
    }
  }

  const testDisconnect = () => {
    try {
      const wallet = new PeraWalletConnect()
      wallet.disconnect()
      setStatus('Disconnected')
      setAddress('')
      setError('')
    } catch (error: any) {
      setError(`Disconnect failed: ${error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">
          🔧 Wallet Connection Debug
        </h1>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Connection Status</h2>
          
          <div className="space-y-4">
            <div>
              <strong className="text-gray-700 dark:text-gray-300">Status:</strong>
              <span className={`ml-2 px-3 py-1 rounded ${
                status.includes('Connected') 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : status.includes('failed')
                  ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
              }`}>
                {status}
              </span>
            </div>
            
            {address && (
              <div>
                <strong className="text-gray-700 dark:text-gray-300">Address:</strong>
                <code className="ml-2 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm">
                  {address}
                </code>
              </div>
            )}
            
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-4">
                <strong className="text-red-800 dark:text-red-200">Error:</strong>
                <p className="text-red-700 dark:text-red-300 mt-1 font-mono text-sm">
                  {error}
                </p>
              </div>
            )}
          </div>
          
          <div className="flex gap-4 mt-6">
            <button
              onClick={testConnect}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
            >
              Test Connect
            </button>
            
            <button
              onClick={testDisconnect}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors"
            >
              Disconnect
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Environment Info</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong className="text-gray-700 dark:text-gray-300">Chain ID:</strong>
              <span className="ml-2 text-gray-600 dark:text-gray-400">416002 (TestNet)</span>
            </div>
            <div>
              <strong className="text-gray-700 dark:text-gray-300">Network:</strong>
              <span className="ml-2 text-gray-600 dark:text-gray-400">Algorand TestNet</span>
            </div>
            <div>
              <strong className="text-gray-700 dark:text-gray-300">PeraWallet Version:</strong>
              <span className="ml-2 text-gray-600 dark:text-gray-400">1.4.2</span>
            </div>
            <div>
              <strong className="text-gray-700 dark:text-gray-300">AlgoSDK Version:</strong>
              <span className="ml-2 text-gray-600 dark:text-gray-400">3.0.0</span>
            </div>
            <div>
              <strong className="text-gray-700 dark:text-gray-300">User Agent:</strong>
              <span className="ml-2 text-gray-600 dark:text-gray-400 text-xs">
                {typeof window !== 'undefined' ? window.navigator.userAgent.slice(0, 50) + '...' : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}