"""
Database Optimization Script
24-Hour Sprint Database Performance Enhancement
"""

import sqlite3
import time

def optimize_database():
    """Optimize database for better performance"""
    print("🔧 Optimizing Database Performance...")
    
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Enable performance optimizations
    optimizations = [
        "PRAGMA journal_mode=WAL",           # Write-Ahead Logging
        "PRAGMA synchronous=NORMAL",         # Faster writes
        "PRAGMA cache_size=10000",           # 10MB cache
        "PRAGMA temp_store=memory",          # Temp tables in memory
        "PRAGMA mmap_size=268435456",        # 256MB memory mapping
    ]
    
    for opt in optimizations:
        cursor.execute(opt)
        print(f"✅ Applied: {opt}")
    
    # Create performance indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_investors_wallet ON investors(wallet_address)",
        "CREATE INDEX IF NOT EXISTS idx_investors_balance ON investors(current_balance)",
        "CREATE INDEX IF NOT EXISTS idx_startups_wallet ON startups(wallet_address)",
        "CREATE INDEX IF NOT EXISTS idx_startups_status ON startups(funding_status)",
        "CREATE INDEX IF NOT EXISTS idx_startups_score ON startups(credit_score)",
        "CREATE INDEX IF NOT EXISTS idx_startups_amount ON startups(requested_amount)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_investor ON transactions(investor_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_startup ON transactions(startup_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)",
    ]
    
    for index in indexes:
        cursor.execute(index)
        print(f"✅ Created index: {index.split('idx_')[1].split(' ')[0]}")
    
    # Analyze tables for query optimization
    cursor.execute("ANALYZE")
    print("✅ Analyzed tables for query optimization")
    
    # Vacuum database to reclaim space
    cursor.execute("VACUUM")
    print("✅ Vacuumed database")
    
    conn.commit()
    conn.close()
    
    print("🎉 Database optimization completed!")

def benchmark_database():
    """Benchmark database performance"""
    print("\n📊 Database Performance Benchmark")
    print("-" * 50)
    
    conn = sqlite3.connect('marketplace.db')
    cursor = conn.cursor()
    
    # Test query performance
    queries = [
        ("Count investors", "SELECT COUNT(*) FROM investors"),
        ("Count startups", "SELECT COUNT(*) FROM startups"),
        ("Available startups", "SELECT * FROM startups WHERE funding_status = 'seeking'"),
        ("Investor portfolio", "SELECT * FROM startups WHERE investor_id = 1"),
        ("Transaction history", "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"),
    ]
    
    for name, query in queries:
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        end = time.time()
        
        query_time = (end - start) * 1000
        print(f"✅ {name}: {query_time:.2f}ms ({len(results)} rows)")
    
    conn.close()

if __name__ == "__main__":
    optimize_database()
    benchmark_database()
