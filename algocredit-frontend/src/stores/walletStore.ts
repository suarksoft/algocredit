/**
 * Wallet state management with Zustand
 * Handles Algorand wallet connection and state
 */

import { create } from 'zustand'
import { PeraWalletConnect } from '@perawallet/connect'
import algosdk from 'algosdk'

// Initialize Pera Wallet
const peraWallet = new PeraWalletConnect({
  chainId: 416002, // TestNet chain ID
})

export interface WalletState {
  // Connection state
  isConnected: boolean
  isConnecting: boolean
  walletAddress: string | null
  balance: number
  
  // Account info
  accountInfo: any | null
  
  // Actions
  connectWallet: () => Promise<void>
  disconnectWallet: () => void
  getAccountInfo: () => Promise<void>
  
  // Error handling
  error: string | null
  clearError: () => void
}

export const useWalletStore = create<WalletState>((set, get) => ({
  // Initial state
  isConnected: false,
  isConnecting: false,
  walletAddress: null,
  balance: 0,
  accountInfo: null,
  error: null,

  // Connect to Pera Wallet
  connectWallet: async () => {
    try {
      set({ isConnecting: true, error: null })

      // Connect to Pera Wallet
      const accounts = await peraWallet.connect()
      
      if (accounts.length === 0) {
        throw new Error('No accounts found')
      }

      const walletAddress = accounts[0]
      
      // Get account info
      await get().getAccountInfo()
      
      set({
        isConnected: true,
        isConnecting: false,
        walletAddress,
      })

      // Store in localStorage for persistence
      localStorage.setItem('algocredit_wallet_address', walletAddress)
      
    } catch (error: any) {
      console.error('Wallet connection error:', error)
      set({
        isConnecting: false,
        error: error.message || 'Failed to connect wallet',
      })
    }
  },

  // Disconnect wallet
  disconnectWallet: () => {
    try {
      peraWallet.disconnect()
      localStorage.removeItem('algocredit_wallet_address')
      
      set({
        isConnected: false,
        walletAddress: null,
        balance: 0,
        accountInfo: null,
        error: null,
      })
    } catch (error: any) {
      console.error('Disconnect error:', error)
      set({ error: error.message || 'Failed to disconnect' })
    }
  },

  // Get account information from Algorand
  getAccountInfo: async () => {
    const { walletAddress } = get()
    
    if (!walletAddress) return

    try {
      // Initialize Algorand client
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      )

      // Get account info
      const accountInfo = await algodClient.accountInformation(walletAddress).do()
      
      set({
        accountInfo,
        balance: Number(accountInfo.amount || 0),
      })
      
    } catch (error: any) {
      console.error('Error fetching account info:', error)
      set({ error: 'Failed to fetch account information' })
    }
  },

  // Clear error
  clearError: () => set({ error: null }),
}))

// Auto-reconnect on page load
if (typeof window !== 'undefined') {
  const savedAddress = localStorage.getItem('algocredit_wallet_address')
  
  if (savedAddress) {
    // Check if wallet is still connected
    peraWallet.connector?.on('connect', () => {
      useWalletStore.getState().getAccountInfo()
      useWalletStore.setState({
        isConnected: true,
        walletAddress: savedAddress,
      })
    })
  }
}

// Listen for wallet events
peraWallet.connector?.on('disconnect', () => {
  useWalletStore.getState().disconnectWallet()
})

