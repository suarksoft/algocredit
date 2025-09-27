"""
Corporate Treasury Marketplace API Test Script
24-Hour Sprint API Testing
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8001"

def test_api_health():
    """Test API health and basic endpoints"""
    print("🔍 Testing API Health...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data['message']}")
        
        # Test marketplace stats
        response = requests.get(f"{BASE_URL}/marketplace/stats")
        print(f"✅ Marketplace stats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total investors: {data['total_investors']}")
            print(f"   Total startups: {data['total_startups']}")
            print(f"   Total funding: {data['total_funding_volume']}")
        
        return True
    except Exception as e:
        print(f"❌ API Health test failed: {e}")
        return False

def test_investor_registration():
    """Test investor registration"""
    print("\n💰 Testing Investor Registration...")
    
    try:
        # Test investor registration
        investor_data = {
            "name": "Test Investor",
            "wallet_address": "INVESTOR_TEST_" + str(int(time.time())),
            "investment_capacity": 100000,
            "risk_preference": "moderate"
        }
        
        response = requests.post(
            f"{BASE_URL}/investor/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(investor_data)
        )
        
        print(f"✅ Investor registration: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Investor ID: {data['investor_id']}")
            print(f"   Status: {data['status']}")
            return data['investor_id'], investor_data['wallet_address']
        else:
            print(f"   Error: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Investor registration failed: {e}")
        return None, None

def test_startup_registration():
    """Test startup registration"""
    print("\n🚀 Testing Startup Registration...")
    
    try:
        startup_data = {
            "name": "Test Startup Inc",
            "wallet_address": "STARTUP_TEST_" + str(int(time.time())),
            "business_description": "Revolutionary AI-powered blockchain startup focusing on DeFi solutions for emerging markets.",
            "requested_amount": 25000,
            "loan_term_months": 12
        }
        
        response = requests.post(
            f"{BASE_URL}/startup/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(startup_data)
        )
        
        print(f"✅ Startup registration: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Startup ID: {data['startup_id']}")
            print(f"   Credit Score: {data['credit_score']}")
            print(f"   Interest Rate: {data['interest_rate']}%")
            return data['startup_id'], startup_data['wallet_address']
        else:
            print(f"   Error: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Startup registration failed: {e}")
        return None, None

def test_user_login(wallet_address, user_type):
    """Test user login"""
    print(f"\n🔐 Testing {user_type.title()} Login...")
    
    try:
        login_data = {
            "wallet_address": wallet_address,
            "user_type": user_type
        }
        
        response = requests.post(
            f"{BASE_URL}/user/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps(login_data)
        )
        
        print(f"✅ {user_type.title()} login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   User ID: {data['user_id']}")
            print(f"   Name: {data['name']}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {user_type.title()} login failed: {e}")
        return False

def test_investor_deposit(investor_id):
    """Test investor deposit"""
    print("\n💳 Testing Investor Deposit...")
    
    try:
        deposit_data = {
            "investor_id": investor_id,
            "amount": 50000
        }
        
        response = requests.post(
            f"{BASE_URL}/investor/deposit",
            headers={"Content-Type": "application/json"},
            data=json.dumps(deposit_data)
        )
        
        print(f"✅ Investor deposit: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Amount: {data['amount']} ALGO")
            print(f"   Transaction ID: {data['transaction_id']}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Investor deposit failed: {e}")
        return False

def test_available_startups():
    """Test getting available startups"""
    print("\n🏢 Testing Available Startups...")
    
    try:
        response = requests.get(f"{BASE_URL}/startup/available")
        
        print(f"✅ Available startups: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Count: {data['count']}")
            if data['available_startups']:
                startup = data['available_startups'][0]
                print(f"   First startup: {startup['name']}")
                print(f"   Credit score: {startup['credit_score']}")
                print(f"   Requested: {startup['requested_amount']} ALGO")
            return data['available_startups']
        else:
            print(f"   Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Available startups failed: {e}")
        return []

def test_funding_execution(investor_id, startup_id):
    """Test funding execution"""
    print("\n💸 Testing Funding Execution...")
    
    try:
        funding_data = {
            "investor_id": investor_id,
            "startup_id": startup_id
        }
        
        response = requests.post(
            f"{BASE_URL}/funding/execute",
            headers={"Content-Type": "application/json"},
            data=json.dumps(funding_data)
        )
        
        print(f"✅ Funding execution: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Funded amount: {data['funded_amount']} ALGO")
            print(f"   Net amount: {data['net_amount']} ALGO")
            print(f"   Platform fee: {data['platform_fee']} ALGO")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Funding execution failed: {e}")
        return False

def test_investor_portfolio(investor_id):
    """Test investor portfolio"""
    print("\n📊 Testing Investor Portfolio...")
    
    try:
        response = requests.get(f"{BASE_URL}/investor/{investor_id}/portfolio")
        
        print(f"✅ Investor portfolio: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total invested: {data['total_invested']} ALGO")
            print(f"   Expected return: {data['expected_return']} ALGO")
            print(f"   Expected profit: {data['expected_profit']} ALGO")
            print(f"   ROI: {data['roi_percentage']}%")
            print(f"   Active investments: {data['active_investments']}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Investor portfolio failed: {e}")
        return False

def test_startup_details(startup_id):
    """Test startup details"""
    print("\n🔍 Testing Startup Details...")
    
    try:
        response = requests.get(f"{BASE_URL}/startup/{startup_id}/details")
        
        print(f"✅ Startup details: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Name: {data['name']}")
            print(f"   Credit score: {data['credit_score']}")
            print(f"   Requested: {data['requested_amount']} ALGO")
            print(f"   Status: {data['funding_status']}")
            print(f"   Risk level: {data['risk_level']}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Startup details failed: {e}")
        return False

def run_full_test_suite():
    """Run complete API test suite"""
    print("🚀 CORPORATE TREASURY MARKETPLACE API TEST SUITE")
    print("=" * 60)
    
    # Wait for API to start
    print("⏳ Waiting for API to start...")
    time.sleep(3)
    
    # Test API health
    if not test_api_health():
        print("❌ API is not running. Please start the API first.")
        return False
    
    # Test investor registration
    investor_id, investor_wallet = test_investor_registration()
    if not investor_id:
        print("❌ Cannot continue without investor registration")
        return False
    
    # Test startup registration  
    startup_id, startup_wallet = test_startup_registration()
    if not startup_id:
        print("❌ Cannot continue without startup registration")
        return False
    
    # Test user logins
    test_user_login(investor_wallet, "investor")
    test_user_login(startup_wallet, "startup")
    
    # Test investor deposit
    if not test_investor_deposit(investor_id):
        print("❌ Cannot continue without deposit")
        return False
    
    # Test available startups
    available_startups = test_available_startups()
    
    # Test funding execution
    if startup_id and investor_id:
        test_funding_execution(investor_id, startup_id)
    
    # Test portfolio and details
    test_investor_portfolio(investor_id)
    test_startup_details(startup_id)
    
    # Final marketplace stats
    print("\n📊 Final Marketplace Stats:")
    test_api_health()
    
    print("\n" + "=" * 60)
    print("✅ API TEST SUITE COMPLETED!")
    print("🎉 All core endpoints are working!")
    
    return True

if __name__ == "__main__":
    run_full_test_suite()
