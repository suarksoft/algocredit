# AlgoCredit - Web3 Security Firewall

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Algorand](https://img.shields.io/badge/Built%20for-Algorand-blue)](https://algorand.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)

> Enterprise-Grade Security Platform for the Algorand Ecosystem

AlgoCredit is developing a compliance scoring library to help web3 startups fight against fraudulent low-credit users with AI-driven credit risk analysis.

## 🚀 Features

### 🛡️ Security & Compliance
- **AI-Powered Credit Scoring** - 95% accuracy in risk assessment
- **Real-time Threat Detection** - MEV protection, flash loan exploit detection
- **Enterprise API Security** - SOC 2 compliant with tiered access
- **Smart Contract Scanning** - Automated vulnerability detection
- **Compliance Monitoring** - Automated regulatory compliance tools

### 🔧 Developer Tools
- **Easy Integration** - Simple APIs for developers
- **Security Dashboard** - Real-time monitoring and analytics
- **AI Risk Calculator** - Advanced wallet risk assessment
- **Rate Limiting** - Adaptive rate limiting and DDoS protection
- **Webhook Notifications** - Real-time security alerts

### 🌐 Algorand Native
- **TestNet Ready** - Fully functional on Algorand TestNet
- **Smart Contracts** - Native Algorand smart contract integration
- **Wallet Integration** - Seamless wallet connection and management
- **Foundation Ready** - Built to Algorand Foundation standards

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Frontend Development](#frontend-development)
- [Backend Development](#backend-development)
- [Smart Contracts](#smart-contracts)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- Algorand TestNet account
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/suarksoft/algocredit.git
cd algocredit
```

### 2. Start Backend
```bash
cd algocredit-backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Start Frontend
```bash
cd algocredit-frontend
npm install
npm run dev
```

### 4. Access the Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🛠️ Installation

### Backend Setup
```bash
cd algocredit-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd algocredit-frontend
npm install
```

### Smart Contracts Setup
```bash
cd algo-contract
npm install
```

## ⚙️ Configuration

### Environment Variables
Create `.env` files in respective directories:

**Backend (.env)**
```env
ALGORAND_NETWORK=testnet
DATABASE_URL=sqlite:///./algocredit.db
REDIS_URL=redis://localhost:6379
API_SECRET_KEY=your-secret-key
```

**Frontend (.env.local)**


# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL_ALT=http://localhost:8000

# Algorand Network Configuration
NEXT_PUBLIC_ALGORAND_NETWORK=testnet
NEXT_PUBLIC_ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
NEXT_PUBLIC_ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud
NEXT_PUBLIC_ALGORAND_CHAIN_ID=416002

# Pera Wallet Configuration
NEXT_PUBLIC_PERAWALLET_CHAIN_ID=416002

# Application Configuration
NEXT_PUBLIC_APP_NAME=AlgoCredit
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_APP_ENVIRONMENT=development

# Feature Flags
NEXT_PUBLIC_ENABLE_BLOCKCHAIN=true
NEXT_PUBLIC_ENABLE_AI_SCORING=true
NEXT_PUBLIC_ENABLE_CACHING=true

# Performance Configuration
NEXT_PUBLIC_CACHE_TTL=30000
NEXT_PUBLIC_API_TIMEOUT=10000

# Demo Configuration
NEXT_PUBLIC_DEMO_MODE=false
NEXT_PUBLIC_MOCK_DATA=false
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ALGORAND_NETWORK=testnet
```

## 📚 API Documentation

### Core Endpoints

#### Security & Risk Analysis
```bash
# AI Risk Analysis
POST /api/v1/credit/ai-risk-analysis
{
  "wallet_address": "ALGO123...456"
}

# Threat Detection
POST /api/v1/security/validate-transaction
{
  "wallet_address": "ALGO123...456",
  "transaction_data": {...},
  "security_level": "enterprise"
}
```

#### API Key Management
```bash
# Generate API Key
POST /api/v1/security/generate-key
{
  "wallet_address": "ALGO123...456",
  "tier": "pro"
}

# Get Wallet API Key
GET /api/v1/security/wallet-key/{wallet_address}
```

### Authentication
All protected endpoints require API key authentication:
```bash
Authorization: Bearer ac_live_your_api_key_here
```

## 🎨 Frontend Development

### Tech Stack
- **Framework**: Next.js 15
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Icons**: Heroicons
- **Wallet Integration**: Algorand WalletConnect

### Key Components
- `AIRiskCalculator` - AI-powered risk assessment
- `SecurityDashboard` - Real-time security monitoring
- `WalletConnect` - Algorand wallet integration
- `AnimatedTerminal` - Code demonstration component

### Development Commands
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

## 🔧 Backend Development

### Tech Stack
- **Framework**: FastAPI
- **Database**: SQLite (with Alembic migrations)
- **AI/ML**: scikit-learn, pandas
- **Caching**: Redis
- **Security**: Custom middleware, rate limiting

### Key Services
- `credit_scoring_service` - AI credit scoring
- `algorand_service` - Blockchain integration
- `api_key_manager` - Security key management
- `threat_detector` - Real-time threat detection

### Development Commands
```bash
python main.py                    # Start development server
uvicorn main:app --reload         # Start with auto-reload
alembic upgrade head              # Run database migrations
python -m pytest tests/           # Run tests
```

## 🔗 Smart Contracts

### Algorand Smart Contracts
- **Contract**: `AlgoCreditPlatformTestNet`
- **Language**: Puya (Python-like)
- **Network**: Algorand TestNet
- **Features**: API key management, security validation

### Deployment
```bash
cd algo-contract/projects/algo-contract
algokit deploy
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- **Frontend**: ESLint + Prettier
- **Backend**: Black + isort
- **TypeScript**: Strict mode enabled

## 📊 Project Structure

```
algocredit/
├── algocredit-frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/                  # App router pages
│   │   ├── components/           # React components
│   │   ├── lib/                  # Utilities and API clients
│   │   └── stores/               # Zustand state management
├── algocredit-backend/           # FastAPI backend
│   ├── src/
│   │   ├── api/                  # API routes
│   │   ├── models/               # Database models
│   │   ├── services/             # Business logic
│   │   └── security/             # Security middleware
├── algo-contract/                # Algorand smart contracts
│   └── projects/algo-contract/
│       └── smart_contracts/      # Puya contracts
└── docs/                         # Documentation
```

## 🚀 Deployment

### Production Deployment
1. **Backend**: Deploy to cloud provider (AWS, GCP, Azure)
2. **Frontend**: Deploy to Vercel, Netlify, or similar
3. **Database**: Set up production database
4. **Redis**: Configure Redis for caching
5. **Smart Contracts**: Deploy to Algorand MainNet

### Docker Support
```bash
docker-compose up -d
```

## 📈 Roadmap

- [ ] MainNet deployment
- [ ] Additional blockchain support
- [ ] Advanced ML models
- [ ] Mobile app
- [ ] Enterprise features
- [ ] API marketplace

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Redis connection
redis-cli ping

# Check Python dependencies
pip install -r requirements.txt
```

**Frontend build errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

**Wallet connection issues:**
- Ensure you're on Algorand TestNet
- Check wallet permissions
- Verify network configuration

## 📞 Support


- **Issues**: [GitHub Issues](https://github.com/suarksoft/algocredit/issues)

- **Email**: dev.bugrakurnaz@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Algorand Foundation](https://algorand.org) for blockchain infrastructure
- [AlgoKit](https://github.com/algorandfoundation/algokit) for development tools
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework
- [Next.js](https://nextjs.org) for the frontend framework

---

**Built with ❤️ for the Algorand ecosystem**

[Website](https://algocredit.io) • [Documentation](https://docs.algocredit.io) • [GitHub](https://github.com/suarksoft/algocredit)
