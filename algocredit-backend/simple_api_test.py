"""
Simple API Test - 24 Hour Sprint
Quick API validation and testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3

app = FastAPI(title="Corporate Treasury API Test", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🚀 Corporate Treasury API Test",
        "status": "running",
        "version": "24h-sprint-1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": "2025-09-27T15:30:00Z"}

@app.get("/test-db")
async def test_database():
    """Test database connection"""
    try:
        conn = sqlite3.connect('test_marketplace.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        return {"database": "connected", "test_result": result[0]}
    except Exception as e:
        return {"database": "error", "error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Simple API Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
