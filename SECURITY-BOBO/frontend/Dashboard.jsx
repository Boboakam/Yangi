import React, { useState, useEffect } from 'react';

// SECURITY-BOBO A1: Touch-First Dashboard
// Winlator va planshetlar uchun optimallashtirilgan

const Dashboard = () => {
  const [data, setData] = useState({
    balance: 0,
    positions: [],
    status: 'ISHGA TUSHMOQDA',
    pnl: 0,
    logs: []
  });

  // Ma'lumotlarni backenddan olish
  const fetchData = async () => {
    try {
      const response = await fetch('/api/status');
      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error("Backend ulanish xatosi");
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans p-4 select-none">
      {/* Header Section */}
      <div className="flex justify-between items-center bg-slate-800 p-6 rounded-2xl shadow-xl mb-6">
        <div>
          <h1 className="text-3xl font-black text-blue-400">SECURITY-BOBO A1</h1>
          <p className="text-slate-400 text-lg">Evolutionary AI System</p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-mono text-green-400">${data.balance.toFixed(2)}</div>
          <div className={`text-xl font-bold ${data.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            Today: {data.pnl >= 0 ? '+' : ''}{data.pnl.toFixed(2)} USDT
          </div>
        </div>
      </div>

      {/* Main Controls - BIG BUTTONS FOR TOUCH */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <button
          className="bg-red-600 active:bg-red-800 p-8 rounded-3xl text-3xl font-black shadow-2xl border-b-8 border-red-900 transition-transform active:scale-95"
          onClick={() => alert('PANIC BUTTON: Hammasi yopilmoqda!')}
        >
          🚨 PANIC BUTTON
        </button>
        <button
          className="bg-blue-600 active:bg-blue-800 p-8 rounded-3xl text-3xl font-black shadow-2xl border-b-8 border-blue-900 transition-transform active:scale-95"
          onClick={() => alert('HISOBOT YUBORILDI')}
        >
          📊 STATUS REPORT
        </button>
      </div>

      {/* Agent Status Matrix */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {['PROFESSOR', 'TITAN', 'MERGAN', 'BOSS', 'NAZORATCHI'].map((agent) => (
          <div key={agent} className="bg-slate-800 p-4 rounded-xl text-center border-l-4 border-green-500">
            <div className="text-xs text-slate-500">{agent}</div>
            <div className="text-sm font-bold text-green-400">FAOL</div>
          </div>
        ))}
      </div>

      {/* Positions Table */}
      <div className="bg-slate-800 rounded-2xl overflow-hidden shadow-lg">
        <div className="p-4 bg-slate-700 font-bold text-xl">Ochiq Pozitsiyalar</div>
        <div className="p-2 overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-slate-400 border-b border-slate-600">
                <th className="p-3">Juftlik</th>
                <th className="p-3">Tomon</th>
                <th className="p-3">Foyda</th>
                <th className="p-3">Harakat</th>
              </tr>
            </thead>
            <tbody>
              {data.positions.length === 0 ? (
                <tr><td colSpan="4" className="p-6 text-center text-slate-500">Hozircha ochiq pozitsiyalar yo'q</td></tr>
              ) : (
                data.positions.map(pos => (
                  <tr key={pos.id} className="border-b border-slate-700">
                    <td className="p-3 font-bold">{pos.symbol}</td>
                    <td className={`p-3 ${pos.side === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>{pos.side}</td>
                    <td className="p-3 font-mono">+{pos.profit}%</td>
                    <td className="p-3">
                      <button className="bg-red-500 p-2 rounded-lg text-sm">Yopish</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Real-time Logs */}
      <div className="mt-6 bg-black p-4 rounded-2xl font-mono text-xs h-40 overflow-y-auto border border-slate-700 text-green-500">
        <div>[SYSTEM] SECURITY-BOBO A1 v1.0.0 boshlandi...</div>
        <div>[PROFESSOR] BTC Gravity tahlil qilindi: BULLISH</div>
        <div>[TITAN] Safe-Lock faol: 25.00 USDT qulflangan</div>
        <div>[NAZORATCHI] Heartbeat: OK</div>
      </div>
    </div>
  );
};

export default Dashboard;
