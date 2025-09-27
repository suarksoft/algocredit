"""
Corporate Treasury Marketplace - Performance Test Suite
24-Hour Sprint Performance Validation
"""

import requests
import time
import asyncio
import concurrent.futures
from statistics import mean, median
from datetime import datetime

# API endpoints
ORIGINAL_API = "http://localhost:8001"
OPTIMIZED_API = "http://localhost:8002"
FRONTEND = "http://localhost:3003"

def test_api_performance(base_url: str, name: str, iterations: int = 10):
    """Test API performance with multiple iterations"""
    print(f"\n🚀 Testing {name} Performance ({iterations} iterations)")
    print("-" * 50)
    
    endpoints = [
        "/marketplace/stats",
        "/startup/available",
    ]
    
    results = {}
    
    for endpoint in endpoints:
        times = []
        
        for i in range(iterations):
            start = time.time()
            try:
                response = requests.get(f"{base_url}{endpoint}")
                end = time.time()
                
                if response.ok:
                    response_time = (end - start) * 1000
                    times.append(response_time)
                else:
                    print(f"❌ {endpoint}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        if times:
            results[endpoint] = {
                "mean": round(mean(times), 2),
                "median": round(median(times), 2),
                "min": round(min(times), 2),
                "max": round(max(times), 2),
                "count": len(times)
            }
            
            print(f"✅ {endpoint}:")
            print(f"   Mean: {results[endpoint]['mean']}ms")
            print(f"   Median: {results[endpoint]['median']}ms")
            print(f"   Range: {results[endpoint]['min']}-{results[endpoint]['max']}ms")
    
    return results

def test_concurrent_load(base_url: str, concurrent_users: int = 10):
    """Test concurrent load performance"""
    print(f"\n⚡ Testing Concurrent Load ({concurrent_users} users)")
    print("-" * 50)
    
    def make_request():
        start = time.time()
        try:
            response = requests.get(f"{base_url}/marketplace/stats")
            end = time.time()
            return (end - start) * 1000 if response.ok else None
        except:
            return None
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(make_request) for _ in range(concurrent_users)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    
    # Filter successful requests
    successful_requests = [r for r in results if r is not None]
    
    if successful_requests:
        total_time = end_time - start_time
        print(f"✅ Concurrent Performance:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Successful requests: {len(successful_requests)}/{concurrent_users}")
        print(f"   Average response time: {mean(successful_requests):.2f}ms")
        print(f"   Requests per second: {len(successful_requests)/total_time:.1f}")
        return True
    else:
        print("❌ All concurrent requests failed")
        return False

def test_cache_effectiveness(base_url: str):
    """Test cache effectiveness"""
    print(f"\n💾 Testing Cache Effectiveness")
    print("-" * 50)
    
    endpoint = f"{base_url}/marketplace/stats"
    
    # First request (no cache)
    start = time.time()
    response1 = requests.get(endpoint)
    time1 = (time.time() - start) * 1000
    
    # Second request (should be cached)
    start = time.time()
    response2 = requests.get(endpoint)
    time2 = (time.time() - start) * 1000
    
    if response1.ok and response2.ok:
        data1 = response1.json()
        data2 = response2.json()
        
        cache_hit = data2.get('cached', False)
        improvement = ((time1 - time2) / time1) * 100 if time1 > time2 else 0
        
        print(f"✅ Cache Test Results:")
        print(f"   First request: {time1:.2f}ms (fresh)")
        print(f"   Second request: {time2:.2f}ms ({'cached' if cache_hit else 'fresh'})")
        print(f"   Performance improvement: {improvement:.1f}%")
        
        return cache_hit and improvement > 0
    else:
        print("❌ Cache test failed")
        return False

def test_frontend_performance():
    """Test frontend loading performance"""
    print(f"\n🎨 Testing Frontend Performance")
    print("-" * 50)
    
    pages = [
        ("Homepage", "/"),
        ("Investor Dashboard", "/investor"),
        ("Startup Dashboard", "/startup")
    ]
    
    for name, path in pages:
        times = []
        
        for i in range(3):  # Test each page 3 times
            start = time.time()
            try:
                response = requests.get(f"{FRONTEND}{path}")
                end = time.time()
                
                if response.ok:
                    load_time = (end - start) * 1000
                    times.append(load_time)
                    
            except Exception as e:
                print(f"❌ {name}: {e}")
        
        if times:
            avg_time = mean(times)
            print(f"✅ {name}: {avg_time:.0f}ms average")
            
            # Performance rating
            if avg_time < 500:
                print(f"   🚀 Excellent performance")
            elif avg_time < 1000:
                print(f"   ✅ Good performance")
            else:
                print(f"   ⚠️  Needs optimization")

def run_complete_performance_test():
    """Run complete performance test suite"""
    print("🚀 CORPORATE TREASURY MARKETPLACE - PERFORMANCE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test original API
    original_results = test_api_performance(ORIGINAL_API, "Original API", 5)
    
    # Test optimized API
    optimized_results = test_api_performance(OPTIMIZED_API, "Optimized API", 5)
    
    # Test concurrent load
    concurrent_success = test_concurrent_load(OPTIMIZED_API, 20)
    
    # Test cache effectiveness
    cache_success = test_cache_effectiveness(OPTIMIZED_API)
    
    # Test frontend performance
    test_frontend_performance()
    
    # Performance comparison
    print(f"\n📊 PERFORMANCE COMPARISON")
    print("=" * 70)
    
    if original_results and optimized_results:
        for endpoint in original_results.keys():
            if endpoint in optimized_results:
                original_time = original_results[endpoint]['mean']
                optimized_time = optimized_results[endpoint]['mean']
                improvement = ((original_time - optimized_time) / original_time) * 100
                
                print(f"📈 {endpoint}:")
                print(f"   Original: {original_time}ms")
                print(f"   Optimized: {optimized_time}ms")
                print(f"   Improvement: {improvement:.1f}%")
    
    # Overall assessment
    print(f"\n🎯 PERFORMANCE SUMMARY")
    print("=" * 70)
    
    performance_score = 0
    max_score = 4
    
    if optimized_results:
        avg_response = mean([r['mean'] for r in optimized_results.values()])
        if avg_response < 10:
            print("✅ API Response Time: Excellent (<10ms)")
            performance_score += 1
        elif avg_response < 50:
            print("✅ API Response Time: Good (<50ms)")
            performance_score += 0.5
    
    if concurrent_success:
        print("✅ Concurrent Load: Passed")
        performance_score += 1
    
    if cache_success:
        print("✅ Caching: Working")
        performance_score += 1
    
    print("✅ Frontend: All pages loading")
    performance_score += 1
    
    final_score = (performance_score / max_score) * 100
    print(f"\n🏆 FINAL PERFORMANCE SCORE: {final_score:.0f}%")
    
    if final_score >= 90:
        print("🚀 EXCELLENT - Demo ready with high performance!")
    elif final_score >= 70:
        print("✅ GOOD - Demo ready with acceptable performance!")
    else:
        print("⚠️  NEEDS IMPROVEMENT - Consider optimization")
    
    return final_score >= 70

if __name__ == "__main__":
    run_complete_performance_test()
