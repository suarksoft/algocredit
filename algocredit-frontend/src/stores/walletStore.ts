/**
 * Wallet state management with Zustand
 * Handles Algorand wallet connection and state
 */

import { create } from 'zustand'
import { PeraWalletConnect } from '@perawallet/connect'
import algosdk from 'algosdk'

// Initialize Pera Wallet with fallback configurations
let peraWallet: PeraWalletConnect

try {
  peraWallet = new PeraWalletConnect({
    chainId: 416002, // TestNet chain ID
  })
  console.log('✅ PeraWallet initialized with chainId 416002')
} catch (error) {
  console.warn('⚠️ Failed to initialize with chainId, trying without:', error)
  try {
    // Fallback without chainId
    peraWallet = new PeraWalletConnect()
    console.log('✅ PeraWallet initialized without chainId')
  } catch (fallbackError) {
    console.error('❌ Failed to initialize PeraWallet:', fallbackError)
    throw new Error('Could not initialize Pera Wallet')
  }
}

// Add global error handler for PeraWallet
if (typeof window !== 'undefined') {
  peraWallet.connector?.on('error', (error: any) => {
    console.error('🔴 PeraWallet global error:', error)
    useWalletStore.setState({ 
      error: `Wallet Error: ${error.message || 'Unknown error'}`,
      isConnecting: false 
    })
  })
}

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
      console.log('🔵 Starting wallet connection...')
      set({ isConnecting: true, error: null })

      // Check if Pera Wallet is available
      if (!peraWallet) {
        throw new Error('Pera Wallet is not initialized')
      }

      // Disconnect any existing connections first
      try {
        peraWallet.disconnect()
      } catch (e) {
        console.log('🔄 No existing connection to disconnect')
      }

      console.log('🔵 Connecting to Pera Wallet...')
      
      // Add timeout for connection
      const connectPromise = peraWallet.connect()
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Connection timeout after 30 seconds')), 30000)
      })
      
      const accounts = await Promise.race([connectPromise, timeoutPromise]) as string[]
      
      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found. Please make sure you have accounts in your Pera Wallet.')
      }

      const walletAddress = accounts[0]
      console.log('✅ Wallet connected! Address:', walletAddress)
      
      // Validate the address format
      if (!walletAddress || typeof walletAddress !== 'string' || walletAddress.length !== 58) {
        throw new Error('Invalid wallet address format')
      }
      
      // Set wallet immediately but with 0 balance initially
      set({
        isConnected: true,
        isConnecting: false,
        walletAddress,
        balance: 0  // Will be updated by getAccountInfo
      })

      // Get account info AFTER setting the wallet
      console.log('🔵 Getting account info...')
      setTimeout(async () => {
        await get().getAccountInfo()
      }, 100) // Small delay to ensure state is set
      
      // Store in localStorage for persistence
      localStorage.setItem('algocredit_wallet_address', walletAddress)
      console.log('✅ Wallet connection complete!')
      
    } catch (error: any) {
      console.error('❌ Wallet connection error:', error)
      
      // More specific error messages
      let errorMessage = 'Failed to connect wallet'
      
      if (error.message?.includes('rejected')) {
        errorMessage = 'Wallet connection was rejected by user'
      } else if (error.message?.includes('timeout')) {
        errorMessage = 'Connection timed out. Please try again.'
      } else if (error.message?.includes('No accounts')) {
        errorMessage = 'No accounts found in wallet. Please create an account in Pera Wallet.'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      set({
        isConnecting: false,
        isConnected: false,
        walletAddress: null,
        error: errorMessage,
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
    
    if (!walletAddress) {
      console.log('🔍 No wallet address to fetch account info')
      return
    }

    console.log('🔍 Fetching account info for:', walletAddress)

    try {
      // Initialize Algorand client
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      )

      console.log('🔍 Making API request to TestNet...')
      // Get account info
      const accountInfo = await algodClient.accountInformation(walletAddress).do()
      
      console.log('✅ Account info received:', {
        amount: accountInfo.amount,
        balance_microAlgos: accountInfo.amount,
        balance_ALGO: Number(accountInfo.amount || 0) / 1_000_000
      })
      
      // Force update the state
      const newBalance = Number(accountInfo.amount || 0)
      set((state) => ({
        ...state,
        accountInfo,
        balance: newBalance,
      }))
      
      console.log('✅ Balance updated in store:', newBalance)
      
    } catch (error: any) {
      console.error('❌ Error fetching account info:', error)
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

