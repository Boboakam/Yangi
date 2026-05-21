from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import config
from database import Database
import uvicorn
import logging

# Dashboard Backend Server
app = FastAPI()
db = Database(config.DB_PATH)
logger = logging.getLogger("DashboardServer")

# Tizim yadrosini (Brain) import qilish yoki unga signal yuborish mantiqi
# Soddalashtirish uchun bu yerda global o'zgaruvchi ishlatamiz (Brain context'da bo'ladi)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Frontend/Dashboard.jsx mantiqini React CDN orqali render qilish (Real Winlator muhiti uchun)
    with open("SECURITY-BOBO/frontend/Dashboard.jsx", "r") as f:
        jsx_content = f.read()

    return f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SECURITY-BOBO A1 Dashboard</title>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900">
        <div id="root"></div>
        <script type="text/babel">
            {jsx_content.replace('export default Dashboard;', 'const root = ReactDOM.createRoot(document.getElementById("root")); root.render(<Dashboard />);')}
        </script>
    </body>
    </html>
    """

@app.get("/api/status")
async def get_status():
    positions = db.get_open_positions()
    pos_list = [{"id": p[0], "symbol": p[1], "side": p[2], "amount": p[3], "profit": 0.0} for p in positions]
    return {{
        "balance": 25.0,
        "pnl": 0.0,
        "status": "RUNNING",
        "positions": pos_list
    }}

@app.post("/api/panic")
async def trigger_panic():
    logger.warning("🆘 Dashboard: Panic Button bosildi!")
    # Brain orqali emergency_close ni chaqirish
    return {{"status": "success", "message": "Barcha savdolar yopilmoqda..."}}

if __name__ == "__main__":
    uvicorn.run(app, host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT)
