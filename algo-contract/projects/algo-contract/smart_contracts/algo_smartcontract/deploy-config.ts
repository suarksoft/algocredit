import { AlgorandClient } from '@algorandfoundation/algokit-utils'
import { AlgoCreditPlatformTestNetFactory } from '../artifacts/algo_smartcontract/AlgoCreditPlatformTestNetClient'

// Deploy configuration for AlgoCredit Platform Contract
export async function deploy() {
  console.log('=== Deploying AlgoCredit Platform Contract ===')

  // Check if we're on TestNet
  const network = process.env.NETWORK || 'testnet'
  console.log(`🌐 Deploying to: ${network}`)

  const algorand = AlgorandClient.fromEnvironment()
  const deployer = await algorand.account.fromEnvironment('DEPLOYER')

  const factory = algorand.client.getTypedAppFactory(AlgoCreditPlatformTestNetFactory, {
    defaultSender: deployer.addr,
  })

  const { appClient, result } = await factory.deploy({ 
    onUpdate: 'replace', 
    onSchemaBreak: 'replace'
  })

  // If app was just created fund the app account
  if (['create', 'replace'].includes(result.operationPerformed)) {
    await algorand.send.payment({
      amount: (2).algo(), // Fund with 2 ALGO for operations
      sender: deployer.addr,
      receiver: appClient.appAddress,
    })
  }

  console.log(`✅ AlgoCredit Platform Contract deployed successfully!`)
  console.log(`📋 Contract ID: ${appClient.appClient.appId}`)
  console.log(`📍 Contract Address: ${appClient.appAddress}`)
  console.log(`👤 Admin Address: ${deployer.addr}`)

  // Test platform functionality with both investors and startups
  try {
    console.log('\n🧪 Testing AlgoCredit Platform functionality...')
    
    // Test hello method
    const helloResponse = await appClient.send.hello({
      args: { name: network === 'testnet' ? 'AlgoCredit Platform' : 'LocalNet Platform' }
    })
    console.log(`✅ Hello test: ${helloResponse.return}`)
    
    // Test contract status
    const statusResponse = await appClient.send.isContractActive({ args: [] })
    console.log(`🔄 Platform active: ${statusResponse.return === 1n ? 'Yes' : 'No'}`)
    
    // Test investor registration
    const investorResponse = await appClient.send.registerInvestor({
      args: { 
        investorType: 'institutional',
        riskLevel: 8
      }
    })
    console.log(`🏦 Investor registration: ${investorResponse.return}`)
    
    // Test startup registration
    const startupResponse = await appClient.send.registerStartup({
      args: { 
        startupName: 'TechStart',
        industry: 'AI',
        requestedAmount: 10000000 // 10 ALGO
      }
    })
    console.log(`🚀 Startup registration: ${startupResponse.return}`)
    
    // Test startup tokenization
    const tokenizeResponse = await appClient.send.tokenizeStartup({
      args: { 
        startupName: 'TechStart',
        tokenPrice: 1000000, // 1 ALGO per token
        totalSupply: 1000000, // 1M tokens
        industry: 'AI'
      }
    })
    console.log(`🪙 Startup tokenization: ${tokenizeResponse.return}`)
    
    // Test investment in tokenized startup
    const investmentResponse = await appClient.send.investInStartup({
      args: { 
        startupId: 1,
        investmentAmount: 5000000, // 5 ALGO
        tokenAmount: 5000000 // 5M tokens
      }
    })
    console.log(`💰 Investment in startup: ${investmentResponse.return}`)
    
    // Test loan request
    const loanResponse = await appClient.send.requestLoan({
      args: { 
        amount: 5000000, // 5 ALGO
        duration: 12, // 12 months
        interestRate: 15 // 15%
      }
    })
    console.log(`💳 Loan request: ${loanResponse.return}`)
    
    // Check counts
    const investorCount = await appClient.send.getInvestorCount({ args: [] })
    const startupCount = await appClient.send.getStartupCount({ args: [] })
    const tokenizedCount = await appClient.send.getTokenizedStartupsCount({ args: [] })
    const investmentCount = await appClient.send.getTotalInvestmentsCount({ args: [] })
    const loanCount = await appClient.send.getLoanRequestCount({ args: [] })
    
    console.log(`📊 Platform stats:`)
    console.log(`  • Investors: ${investorCount.return}`)
    console.log(`  • Startups: ${startupCount.return}`)
    console.log(`  • Tokenized Startups: ${tokenizedCount.return}`)
    console.log(`  • Total Investments: ${investmentCount.return}`)
    console.log(`  • Loan Requests: ${loanCount.return}`)
    
    // Test deposit simulation
    const depositResponse = await appClient.send.simulateDeposit({
      args: { amount: 20000000 } // 20 ALGO in microALGO
    })
    console.log(`💰 Deposit simulation: ${depositResponse.return}`)
    
    // Test real deposit
    const realDepositResponse = await appClient.send.realDeposit({ args: [] })
    console.log(`💎 Real deposit: ${realDepositResponse.return}`)
    
    // Test loan funding simulation
    const fundingResponse = await appClient.send.simulateLoanFunding({
      args: { 
        loanId: 1,
        amount: 5000000 // 5 ALGO
      }
    })
    console.log(`🤝 Loan funding simulation: ${fundingResponse.return}`)
    
    // Test real loan funding
    const realFundingResponse = await appClient.send.realLoanFunding({
      args: { 
        loanId: 1,
        amount: 3000000 // 3 ALGO
      }
    })
    console.log(`💎 Real loan funding: ${realFundingResponse.return}`)
    
    // Test API key registration
    const apiKeyResponse = await appClient.send.registerApiKey({
      args: { 
        walletAddress: 'RZ63HGZIZJ2DFK75NBPVGKZYBADAKDY3WENWKYJY7ISV2VDFQUHWHR7MXE',
        apiKeyHash: 'ac_live_test_key_hash',
        tier: 'enterprise'
      }
    })
    console.log(`🔑 API Key registration: ${apiKeyResponse.return}`)
    
    // Test API key count
    const apiKeyCountResponse = await appClient.send.getApiKeyCount({ args: [] })
    console.log(`📊 Total API keys: ${apiKeyCountResponse.return}`)
    
    // Test wallet API key permission
    const canGenerateResponse = await appClient.send.canGenerateApiKey({
      args: { 
        walletAddress: 'RZ63HGZIZJ2DFK75NBPVGKZYBADAKDY3WENWKYJY7ISV2VDFQUHWHR7MXE'
      }
    })
    console.log(`✅ Can generate API key: ${canGenerateResponse.return === 1 ? 'Yes' : 'No'}`)
    
    // Test platform fees
    const feesResponse = await appClient.send.getPlatformFeesAmount({ args: [] })
    console.log(`💰 Platform fees: ${feesResponse.return} microALGO`)
    
    // Test platform stats
    const platformStats = await appClient.send.getPlatformStats({ args: [] })
    console.log(`📈 Platform overview: ${platformStats.return}`)
    
    // Test contract info
    const infoResponse = await appClient.send.getContractInfo({ args: [] })
    console.log(`✅ Platform info: ${infoResponse.return}`)
    
  } catch (error) {
    console.log(`⚠️  Test failed: ${error}`)
  }
}
