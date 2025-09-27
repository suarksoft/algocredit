# 🏦 Corporate Treasury on Algorand - MVP Roadmap

## 🎯 **PROJE VİZYONU**
**Corporate Treasury**: Şirketlerin nakitlerini Algorand'da değerlendiren basit ama çalışan platform. Deposit → Yield → Instant Credit Line.

---

## 📅 **4 HAFTALIK MVP PLANI**

### 🏗️ **WEEK 1: SMART CONTRACTS** (23-29 Eylül)
**Hedef**: PyTeal ile temel treasury kontratları

#### **Gün 1-2: Treasury Vault Contract**
```python
# treasury_vault.py - EN BASİT HALİ
def deposit():
    # Accept ALGO
    # Record balance
    # Update company balance
    
def withdraw():
    # Check balance
    # Send ALGO back
    # Update records

def get_balance(company_id):
    # Return current balance
```

#### **Gün 3-4: Loan Manager Contract**
```python
# loan_manager.py
def calculate_credit_limit(deposit_amount):
    # 50% of deposit as credit limit
    return deposit_amount * 0.5

def issue_loan(company_id, amount):
    # Check credit limit
    # Transfer ALGO
    # Record loan

def repay_loan(company_id, amount):
    # Accept payment
    # Update loan balance
```

#### **Gün 5: Yield Tracker Contract**
```python
# yield_tracker.py
def calculate_yield(balance, days):
    # Simple 5% APY calculation
    return balance * 0.05 * (days / 365)

def distribute_yield():
    # Calculate and distribute yield
    # Update balances
```

---

### 🔧 **WEEK 2: BACKEND API** (30 Eylül - 6 Ekim)
**Hedef**: FastAPI ile REST endpoints

#### **Gün 1-2: Core API Structure**
```python
# main.py
from fastapi import FastAPI
from algosdk import *

app = FastAPI()

@app.post("/auth/company-login")
async def company_login(wallet_address: str):
    # Verify wallet
    # Create/update company record
    # Return company_id

@app.get("/treasury/balance/{company_id}")
async def get_balance(company_id: int):
    # Query smart contract
    # Return current balance
```

#### **Gün 3-4: Treasury Operations**
```python
@app.post("/treasury/deposit")
async def deposit(company_id: int, amount: int):
    # Call treasury_vault.deposit()
    # Save transaction to DB
    # Return transaction hash

@app.post("/treasury/withdraw")
async def withdraw(company_id: int, amount: int):
    # Check balance
    # Call treasury_vault.withdraw()
    # Return transaction hash

@app.get("/treasury/yield/{company_id}")
async def get_yield(company_id: int):
    # Calculate current yield
    # Return yield amount
```

#### **Gün 5: Loan Management**
```python
@app.get("/loan/calculate-limit/{company_id}")
async def calculate_limit(company_id: int):
    # Get deposit balance
    # Calculate 50% credit limit
    # Return limit

@app.post("/loan/draw")
async def draw_loan(company_id: int, amount: int):
    # Check credit limit
    # Call loan_manager.issue_loan()
    # Return transaction hash

@app.get("/analytics/summary/{company_id}")
async def get_summary(company_id: int):
    # Total deposits
    # Current yield
    # Active loans
    # Net profit
```

---

### 🎨 **WEEK 3: FRONTEND** (7-13 Ekim)
**Hedef**: Next.js ile basit ama güzel UI

#### **Gün 1-2: Core Components**
```jsx
// components/WalletConnect.jsx
function WalletConnect() {
  const [wallet, setWallet] = useState(null);
  
  const connectWallet = async () => {
    // Connect Pera Wallet
    // Get wallet address
    // Login to backend
  };
  
  return (
    <button onClick={connectWallet}>
      {wallet ? `Connected: ${wallet.slice(0,6)}...` : 'Connect Wallet'}
    </button>
  );
}

// components/BalanceCard.jsx
function BalanceCard({ balance, yield }) {
  return (
    <div className="bg-blue-100 p-4 rounded-lg">
      <h3>Total Balance</h3>
      <p className="text-2xl font-bold">{balance} ALGO</p>
      <p className="text-green-600">+{yield} ALGO yield</p>
    </div>
  );
}
```

#### **Gün 3-4: Main Pages**
```jsx
// pages/dashboard.jsx
function Dashboard() {
  return (
    <div>
      <h1>Corporate Treasury Dashboard</h1>
      <WalletConnect />
      <BalanceCard balance={10000} yield={58} />
      <div className="grid grid-cols-2 gap-4">
        <DepositModal />
        <LoanCalculator />
      </div>
    </div>
  );
}

// pages/treasury.jsx
function Treasury() {
  return (
    <div>
      <h1>Treasury Management</h1>
      <DepositForm />
      <WithdrawForm />
      <YieldTracker />
    </div>
  );
}
```

#### **Gün 5: Loan Interface**
```jsx
// pages/loans.jsx
function Loans() {
  return (
    <div>
      <h1>Credit Management</h1>
      <CreditLimitCard limit={5000} used={2000} />
      <LoanForm />
      <RepaymentSchedule />
    </div>
  );
}
```

---

### 🚀 **WEEK 4: DEMO & POLISH** (14-20 Ekim)
**Hedef**: Çalışan demo + wow factor

#### **Gün 1-2: Demo Scenario**
```javascript
// Demo Flow (5 minutes)
const demoFlow = async () => {
  // 1. CEO connects wallet
  console.log("1. CEO connects Pera Wallet");
  await connectWallet();
  
  // 2. Shows company dashboard
  console.log("2. Dashboard shows: 0 ALGO balance");
  
  // 3. Deposits 10,000 ALGO
  console.log("3. CEO deposits 10,000 ALGO");
  await deposit(10000);
  
  // 4. Shows allocation
  console.log("4. System shows:");
  console.log("   - 7,000 ALGO in yield (5% APY)");
  console.log("   - 3,000 ALGO liquid");
  
  // 5. Takes instant loan
  console.log("5. CEO takes 2,000 ALGO loan");
  await drawLoan(2000);
  
  // 6. Shows monthly report
  console.log("6. Monthly Report:");
  console.log("   - Earned: 58 ALGO (yield)");
  console.log("   - Paid: 16 ALGO (interest)");
  console.log("   - Net profit: 42 ALGO");
};
```

#### **Gün 3-4: Polish & Testing**
- [ ] **UI Polish**
  - Smooth animations
  - Professional colors
  - Mobile responsive
  - Loading states

- [ ] **Error Handling**
  - Wallet connection errors
  - Insufficient balance
  - Network issues
  - User feedback

- [ ] **Testing**
  - End-to-end flow test
  - Edge cases
  - Performance check
  - Mobile testing

#### **Gün 5: Demo Preparation**
- [ ] **Live Demo Setup**
  - Testnet ALGOs ready
  - Demo wallet prepared
  - Backup scenarios
  - Timing practice

- [ ] **Presentation Materials**
  - 5-minute pitch deck
  - Live demo script
  - Technical architecture
  - Business model

---

## 🎯 **BAŞARI KRİTERLERİ**

### **✅ MUST HAVE (Olmazsa olmaz)**
- [ ] Çalışan deposit/withdraw
- [ ] Basit kredi verme
- [ ] Algorand testnet entegrasyonu
- [ ] Temel dashboard

### **⭐ NICE TO HAVE (Olsa iyi)**
- [ ] Multi-sig support
- [ ] Yield optimization
- [ ] Mobile responsive
- [ ] Chart/graphs

### **🚀 WOW FACTOR (Jüri etkiler)**
- [ ] Gerçek ALGO transfer
- [ ] Canlı yield gösterimi
- [ ] Smooth animations
- [ ] Professional UI

---

## 🛠️ **TEKNİK STACK (SIMPLE)**

### **Backend**
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
py-algorand-sdk==2.6.0
pyteal==0.20.0
sqlite3  # Built-in
```

### **Frontend**
```json
// package.json
{
  "dependencies": {
    "next": "^14",
    "react": "^18",
    "algosdk": "^3.0.0",
    "@perawallet/connect": "^1.4.2",
    "tailwindcss": "^3.3.0"
  }
}
```

### **Database Schema**
```sql
-- Simple SQLite tables
CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  name TEXT,
  wallet_address TEXT UNIQUE,
  created_at TIMESTAMP
);

CREATE TABLE deposits (
  id INTEGER PRIMARY KEY,
  company_id INTEGER,
  amount INTEGER,
  timestamp TIMESTAMP
);

CREATE TABLE loans (
  id INTEGER PRIMARY KEY,
  company_id INTEGER,
  amount INTEGER,
  interest_rate REAL,
  status TEXT,
  created_at TIMESTAMP
);
```

---

## 🚀 **İLK ADIMLAR (BUGÜN)**

### **Step 1: Project Setup**
```bash
# Create project structure
mkdir corporate-treasury
cd corporate-treasury

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn py-algorand-sdk pyteal

# Frontend setup
npx create-next-app@latest frontend --typescript --tailwind
cd frontend
npm install algosdk @perawallet/connect
```

### **Step 2: First Smart Contract**
```python
# contracts/treasury_vault.py
from pyteal import *

def treasury_vault():
    # Simple deposit/withdraw logic
    # This is where we start!
    pass

if __name__ == "__main__":
    print(compileTeal(treasury_vault(), Mode.Application))
```

### **Step 3: First API Endpoint**
```python
# backend/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Corporate Treasury API"}

@app.post("/treasury/deposit")
async def deposit(amount: int, wallet: str):
    # TODO: Implement deposit logic
    return {"status": "success", "amount": amount}
```

### **Step 4: First UI Component**
```jsx
// frontend/components/WalletConnect.jsx
export default function WalletConnect() {
  return (
    <div className="p-4 bg-blue-100 rounded-lg">
      <h2>Connect Your Corporate Wallet</h2>
      <button className="bg-blue-500 text-white px-4 py-2 rounded">
        Connect Pera Wallet
      </button>
    </div>
  );
}
```

---

## 📊 **HAFTALIK HEDEFLER**

### **Week 1 Success**
- ✅ 3 smart contracts deployed
- ✅ Basic deposit/withdraw working
- ✅ Testnet integration complete

### **Week 2 Success**
- ✅ 8+ API endpoints working
- ✅ Database integration complete
- ✅ Error handling implemented

### **Week 3 Success**
- ✅ 4 main pages functional
- ✅ Wallet connection working
- ✅ Responsive design complete

### **Week 4 Success**
- ✅ Live demo ready
- ✅ All features working
- ✅ Presentation materials ready

---

## 🎯 **DEMO SCRIPT (5 DAKİKA)**

### **Opening (30 seconds)**
"Corporate Treasury on Algorand - Şirketlerin nakitlerini değerlendiren platform. Deposit, yield, instant credit. 3 saniyede başlayalım."

### **Live Demo (4 minutes)**
1. **Wallet Connect** (30s)
   - "CEO wallet'ını bağlıyorum"
   - Pera Wallet popup
   - Dashboard açılıyor

2. **Deposit** (1 minute)
   - "10,000 ALGO deposit ediyorum"
   - Transaction confirmation
   - Balance update

3. **Yield Allocation** (30s)
   - "Otomatik %70 yield, %30 liquid"
   - Real-time calculation
   - APY gösterimi

4. **Instant Loan** (1 minute)
   - "5,000 ALGO kredi limiti"
   - "2,000 ALGO çekiyorum"
   - Instant transfer

5. **Monthly Report** (1 minute)
   - "Aylık rapor"
   - "58 ALGO kazandık, 16 ALGO ödedik"
   - "42 ALGO net kar"

### **Closing (30 seconds)**
"Corporate Treasury - Basit, hızlı, karlı. Algorand'ın gücüyle."

---

## 🏆 **HACKATHON WINNING STRATEGY**

### **Judging Criteria**
1. **Technical Excellence** (40%)
   - PyTeal smart contracts
   - Algorand SDK integration
   - Clean code structure

2. **Innovation** (30%)
   - Corporate treasury use case
   - Instant credit line
   - Yield optimization

3. **Impact** (20%)
   - Real business value
   - Algorand adoption
   - Corporate onboarding

4. **Presentation** (10%)
   - Live demo execution
   - Clear value proposition
   - Professional delivery

### **Key Messages**
- "Corporate treasury made simple"
- "3-second transactions"
- "5% APY + instant credit"
- "Built on Algorand"

---

**Last Updated**: 23 Eylül 2025  
**Status**: Ready to start - Smart Contracts  
**Next Action**: treasury_vault.py contract

---

*Bu roadmap KISS prensibini uygular: Keep It Simple, Stupid. Çalışan bir demo > Mükemmel fikir. Başla, tak tak ilerle! 🚀*
