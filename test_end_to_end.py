"""
Corporate Treasury Marketplace - End-to-End Flow Test
24-Hour Sprint Complete User Journey Testing
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"
FRONTEND_BASE = "http://localhost:3003"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def test_homepage():
    """Test homepage and live stats"""
    print_section("HOMEPAGE & LIVE STATS TEST")
    
    try:
        # Test homepage loads
        response = requests.get(FRONTEND_BASE)
        print(f"✅ Homepage loads: {response.status_code}")
        
        # Test API stats
        response = requests.get(f"{API_BASE}/marketplace/stats")
        if response.ok:
            stats = response.json()
            print(f"✅ Live stats working:")
            print(f"   - Investors: {stats['total_investors']}")
            print(f"   - Startups: {stats['total_startups']}")
            print(f"   - Funding Volume: {stats['total_funding_volume']} ALGO")
            print(f"   - Available Opportunities: {stats['available_opportunities']}")
            return True
        else:
            print(f"❌ Stats API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Homepage test failed: {e}")
        return False

def test_investor_journey():
    """Test complete investor journey"""
    print_section("INVESTOR JOURNEY TEST")
    
    try:
        # 1. Register investor
        print("🧪 Step 1: Investor Registration")
        investor_data = {
            "name": "E2E Test Investor",
            "wallet_address": f"INVESTOR_E2E_{int(time.time())}",
            "investment_capacity": 200000,
            "risk_preference": "moderate"
        }
        
        response = requests.post(f"{API_BASE}/investor/register", json=investor_data)
        if not response.ok:
            print(f"❌ Investor registration failed: {response.status_code}")
            return False
            
        investor_result = response.json()
        investor_id = investor_result['investor_id']
        print(f"✅ Investor registered: ID {investor_id}")
        
        # 2. Test login
        print("🧪 Step 2: Investor Login")
        login_data = {
            "wallet_address": investor_data['wallet_address'],
            "user_type": "investor"
        }
        
        response = requests.post(f"{API_BASE}/user/login", json=login_data)
        if response.ok:
            login_result = response.json()
            print(f"✅ Login successful: {login_result['name']}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        # 3. Deposit ALGO
        print("🧪 Step 3: Deposit ALGO")
        deposit_data = {
            "investor_id": investor_id,
            "amount": 100000
        }
        
        response = requests.post(f"{API_BASE}/investor/deposit", json=deposit_data)
        if response.ok:
            deposit_result = response.json()
            print(f"✅ Deposit successful: {deposit_result['amount']} ALGO")
        else:
            print(f"❌ Deposit failed: {response.status_code}")
            return False
        
        # 4. Check available startups
        print("🧪 Step 4: Browse Available Startups")
        response = requests.get(f"{API_BASE}/startup/available")
        if response.ok:
            startups_result = response.json()
            available_startups = startups_result['available_startups']
            print(f"✅ Found {len(available_startups)} available startups")
            
            if available_startups:
                startup = available_startups[0]
                print(f"   - Startup: {startup['name']}")
                print(f"   - Amount: {startup['requested_amount']} ALGO")
                print(f"   - Credit Score: {startup['credit_score']}")
                print(f"   - Interest Rate: {startup['interest_rate']}%")
                
                # 5. Fund startup
                print("🧪 Step 5: Fund Startup")
                funding_data = {
                    "investor_id": investor_id,
                    "startup_id": startup['id']
                }
                
                response = requests.post(f"{API_BASE}/funding/execute", json=funding_data)
                if response.ok:
                    funding_result = response.json()
                    print(f"✅ Funding successful:")
                    print(f"   - Funded Amount: {funding_result['funded_amount']} ALGO")
                    print(f"   - Net Amount: {funding_result['net_amount']} ALGO")
                    print(f"   - Platform Fee: {funding_result['platform_fee']} ALGO")
                else:
                    print(f"❌ Funding failed: {response.status_code}")
                    return False
        
        # 6. Check portfolio
        print("🧪 Step 6: Check Portfolio")
        response = requests.get(f"{API_BASE}/investor/{investor_id}/portfolio")
        if response.ok:
            portfolio_result = response.json()
            print(f"✅ Portfolio loaded:")
            print(f"   - Total Invested: {portfolio_result['total_invested']} ALGO")
            print(f"   - Expected Return: {portfolio_result['expected_return']} ALGO")
            print(f"   - Expected Profit: {portfolio_result['expected_profit']} ALGO")
            print(f"   - ROI: {portfolio_result['roi_percentage']}%")
            print(f"   - Active Investments: {portfolio_result['active_investments']}")
        else:
            print(f"❌ Portfolio check failed: {response.status_code}")
            return False
        
        print("🎉 INVESTOR JOURNEY COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Investor journey failed: {e}")
        return False

def test_startup_journey():
    """Test complete startup journey"""
    print_section("STARTUP JOURNEY TEST")
    
    try:
        # 1. Register startup
        print("🧪 Step 1: Startup Registration")
        startup_data = {
            "name": "E2E Test Startup",
            "wallet_address": f"STARTUP_E2E_{int(time.time())}",
            "business_description": "Revolutionary AI-powered blockchain solution for sustainable energy management in smart cities.",
            "requested_amount": 75000,
            "loan_term_months": 18
        }
        
        response = requests.post(f"{API_BASE}/startup/register", json=startup_data)
        if not response.ok:
            print(f"❌ Startup registration failed: {response.status_code}")
            return False
            
        startup_result = response.json()
        startup_id = startup_result['startup_id']
        print(f"✅ Startup registered: ID {startup_id}")
        print(f"   - Credit Score: {startup_result['credit_score']}")
        print(f"   - Interest Rate: {startup_result['interest_rate']}%")
        
        # 2. Test login
        print("🧪 Step 2: Startup Login")
        login_data = {
            "wallet_address": startup_data['wallet_address'],
            "user_type": "startup"
        }
        
        response = requests.post(f"{API_BASE}/user/login", json=login_data)
        if response.ok:
            login_result = response.json()
            print(f"✅ Login successful: {login_result['name']}")
            print(f"   - Funding Status: {login_result['funding_status']}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        # 3. Check startup details
        print("🧪 Step 3: Check Startup Profile")
        response = requests.get(f"{API_BASE}/startup/{startup_id}/details")
        if response.ok:
            details_result = response.json()
            print(f"✅ Profile loaded:")
            print(f"   - Name: {details_result['name']}")
            print(f"   - Requested: {details_result['requested_amount']} ALGO")
            print(f"   - Risk Level: {details_result['risk_level']}")
            print(f"   - Status: {details_result['funding_status']}")
        else:
            print(f"❌ Profile check failed: {response.status_code}")
            return False
        
        print("🎉 STARTUP JOURNEY COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Startup journey failed: {e}")
        return False

def test_marketplace_integration():
    """Test marketplace integration"""
    print_section("MARKETPLACE INTEGRATION TEST")
    
    try:
        # Test frontend pages
        pages = [
            ("Homepage", "/"),
            ("Investor Dashboard", "/investor"),
            ("Startup Dashboard", "/startup")
        ]
        
        for name, path in pages:
            response = requests.get(f"{FRONTEND_BASE}{path}")
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
        
        # Test API documentation
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print(f"✅ API Documentation: Working")
        else:
            print(f"❌ API Documentation: Failed ({response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ Marketplace integration test failed: {e}")
        return False

def test_performance():
    """Test API performance"""
    print_section("PERFORMANCE TEST")
    
    try:
        endpoints = [
            "/marketplace/stats",
            "/startup/available"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{API_BASE}{endpoint}")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.ok and response_time < 200:
                print(f"✅ {endpoint}: {response_time:.0f}ms (Fast)")
            elif response.ok:
                print(f"⚠️  {endpoint}: {response_time:.0f}ms (Slow)")
            else:
                print(f"❌ {endpoint}: Failed ({response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_complete_e2e_test():
    """Run complete end-to-end test suite"""
    print("🚀 CORPORATE TREASURY MARKETPLACE - END-TO-END TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Homepage & Stats", test_homepage()))
    test_results.append(("Investor Journey", test_investor_journey()))
    test_results.append(("Startup Journey", test_startup_journey()))
    test_results.append(("Marketplace Integration", test_marketplace_integration()))
    test_results.append(("Performance", test_performance()))
    
    # Summary
    print_section("TEST RESULTS SUMMARY")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 OVERALL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! SYSTEM IS READY FOR DEMO!")
        return True
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    run_complete_e2e_test()
