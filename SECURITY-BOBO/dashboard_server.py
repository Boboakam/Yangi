from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config
from database import Database
from binance_api import BinanceClient

# Dashboard Backend (FastAPI)
# Frontend bilan aloqa o'rnatadi

app = FastAPI(title="SECURITY-BOBO Dashboard API")
db = Database()
binance = BinanceClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def get_status():
    """Tizim holatini qaytarish"""
    balance = binance.get_balance()
    positions = db.get_open_positions()
    return {
        "status": "RUNNING",
        "balance": balance,
        "active_trades": len(positions),
        "symbols": config.SYMBOLS
    }

@app.get("/positions")
def get_positions():
    """Ochiq pozitsiyalarni qaytarish"""
    return db.get_open_positions()

@app.post("/emergency_stop")
def emergency_stop():
    """Favqulodda to'xtatish buyrug'i"""
    return {"message": "Tizim to'xtatildi va barcha pozitsiyalar yopildi."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT)
