import React, { useState, useEffect } from 'react';

// SECURITY-BOBO Dashboard v5.0
// Touch-First interfeys (Planshetlar va Sensorli ekranlar uchun optimallashgan)

const Dashboard = () => {
  const [data, setData] = useState({
    balance: 0,
    status: 'Yuklanmoqda...',
    active_trades: 0,
    symbols: []
  });
  const [positions, setPositions] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(new Date().toLocaleTimeString());

  const fetchData = async () => {
    try {
      const res = await fetch('http://localhost:8000/status');
      const json = await res.json();
      setData(json);

      const posRes = await fetch('http://localhost:8000/positions');
      const posJson = await posRes.json();
      setPositions(posJson);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Ma'lumot olishda xato:", err);
      setData(prev => ({ ...prev, status: 'XATOLIK: Backend ulanmadi' }));
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // 3 soniyada yangilash
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={containerStyle}>
      {/* Header */}
      <header style={headerStyle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px' }}>
          <div style={pulseIcon}></div>
          <h1 style={titleStyle}>SECURITY-BOBO <span style={{fontSize: '14px', color: '#8b949e'}}>GODMODE v5</span></h1>
        </div>
        <p style={{ color: '#8b949e', margin: '5px 0' }}>Binance USDT-M Futures Swarm Trading</p>
        <span style={{ fontSize: '12px', opacity: 0.6 }}>Oxirgi yangilanish: {lastUpdate}</span>
      </header>

      {/* Main Stats Grid */}
      <div style={statsGridStyle}>
        <div style={cardStyle}>
          <p style={cardLabelStyle}>💰 HAMYON BALANSI</p>
          <h2 style={cardValueStyle}>{data.balance.toLocaleString()} <span style={{fontSize: '16px'}}>USDT</span></h2>
        </div>
        <div style={{ ...cardStyle, borderColor: data.status === 'RUNNING' ? '#00e676' : '#ff1744' }}>
          <p style={cardLabelStyle}>📊 TIZIM HOLATI</p>
          <h2 style={{ ...cardValueStyle, color: data.status === 'RUNNING' ? '#00e676' : '#ff1744' }}>{data.status}</h2>
        </div>
        <div style={cardStyle}>
          <p style={cardLabelStyle}>📉 OCHIQ POZITSIYALAR</p>
          <h2 style={cardValueStyle}>{data.active_trades}</h2>
        </div>
      </div>

      {/* Active Symbols */}
      <div style={symbolsContainerStyle}>
        {data.symbols.map(s => (
          <div key={s} style={symbolBadgeStyle}>
            {s.replace('USDT', '')}
          </div>
        ))}
      </div>

      {/* Positions Table */}
      <div style={tableCardStyle}>
        <h3 style={{ marginBottom: '15px', color: '#2962ff' }}>📝 Faol Pozitsiyalar</h3>
        {positions.length === 0 ? (
          <p style={{ textAlign: 'center', padding: '40px', color: '#8b949e' }}>Hozircha ochiq pozitsiyalar yo'q.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyle}>
              <thead>
                <tr style={tableHeaderRowStyle}>
                  <th style={thStyle}>JUFTLIK</th>
                  <th style={thStyle}>TOMON</th>
                  <th style={thStyle}>HAJM</th>
                  <th style={thStyle}>KIRISH</th>
                  <th style={thStyle}>STOP LOSS</th>
                  <th style={thStyle}>TAKE PROFIT</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos, i) => (
                  <tr key={i} style={tableRowStyle}>
                    <td style={{ ...tdStyle, fontWeight: 'bold' }}>{pos[1]}</td>
                    <td style={{ ...tdStyle, color: pos[2] === 'BUY' ? '#00e676' : '#ff5252', fontWeight: 'bold' }}>{pos[2]}</td>
                    <td style={tdStyle}>{pos[3]}</td>
                    <td style={tdStyle}>{pos[4].toFixed(2)}</td>
                    <td style={{ ...tdStyle, color: '#ff5252' }}>{pos[5].toFixed(2)}</td>
                    <td style={{ ...tdStyle, color: '#00e676' }}>{pos[6].toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Emergency Control */}
      <div style={controlSectionStyle}>
        <button
          style={emergencyButtonStyle}
          onLongPress={() => alert('Favqulodda to\'xtatish buyrug\'i yuborildi!')}
          onClick={() => {
            if(window.confirm("Barcha pozitsiyalarni yopish va tizimni to'xtatishga aminmisiz?")) {
              fetch('http://localhost:8000/emergency_stop', { method: 'POST' });
            }
          }}
        >
          🆘 FAVQULODDA HAMMASINI YOPISH ( EMERGENCY STOP )
        </button>
        <p style={{ fontSize: '12px', color: '#8b949e', marginTop: '10px' }}>* Ushbu tugma barcha agentlarni to'xtatadi va Binance dagi ochiq orderlarni Market narxida yopadi.</p>
      </div>
    </div>
  );
};

// Styles
const containerStyle = {
  padding: '20px',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  backgroundColor: '#0d1117',
  color: '#c9d1d9',
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  gap: '20px'
};

const headerStyle = {
  textAlign: 'center',
  padding: '20px 0',
  borderBottom: '1px solid #30363d',
  marginBottom: '10px'
};

const titleStyle = {
  margin: 0,
  fontSize: '28px',
  letterSpacing: '1px',
  color: '#2962ff'
};

const pulseIcon = {
  width: '12px',
  height: '12px',
  backgroundColor: '#00e676',
  borderRadius: '50%',
  boxShadow: '0 0 0 0 rgba(0, 230, 118, 0.7)',
  animation: 'pulse 1.5s infinite'
};

const statsGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
  gap: '20px'
};

const cardStyle = {
  backgroundColor: '#161b22',
  padding: '25px',
  borderRadius: '16px',
  border: '1px solid #30363d',
  boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
  transition: 'transform 0.2s ease'
};

const cardLabelStyle = {
  fontSize: '12px',
  color: '#8b949e',
  margin: '0 0 10px 0',
  fontWeight: '600'
};

const cardValueStyle = {
  margin: 0,
  fontSize: '32px',
  fontWeight: '700'
};

const symbolsContainerStyle = {
  display: 'flex',
  gap: '10px',
  flexWrap: 'wrap',
  justifyContent: 'center'
};

const symbolBadgeStyle = {
  backgroundColor: '#21262d',
  padding: '8px 16px',
  borderRadius: '20px',
  fontSize: '14px',
  border: '1px solid #30363d'
};

const tableCardStyle = {
  backgroundColor: '#161b22',
  padding: '20px',
  borderRadius: '16px',
  border: '1px solid #30363d',
  flex: 1
};

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse'
};

const tableHeaderRowStyle = {
  borderBottom: '2px solid #30363d'
};

const thStyle = {
  textAlign: 'left',
  padding: '15px',
  fontSize: '12px',
  color: '#8b949e',
  textTransform: 'uppercase'
};

const tableRowStyle = {
  borderBottom: '1px solid #21262d'
};

const tdStyle = {
  padding: '15px',
  fontSize: '16px'
};

const controlSectionStyle = {
  textAlign: 'center',
  padding: '20px'
};

const emergencyButtonStyle = {
  width: '100%',
  maxWidth: '600px',
  padding: '25px',
  backgroundColor: '#da3633',
  color: 'white',
  border: 'none',
  borderRadius: '20px',
  fontSize: '20px',
  fontWeight: '800',
  cursor: 'pointer',
  boxShadow: '0 8px 0 #8e2a27',
  transition: 'all 0.1s active'
};

export default Dashboard;
