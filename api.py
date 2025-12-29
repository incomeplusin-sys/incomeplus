import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- ANGEL ONE CONFIG ---
API_KEY = os.getenv('API_KEY')
CLIENT_CODE = os.getenv('CLIENT_CODE')
PASSWORD = os.getenv('PASSWORD')
TOTP_SECRET = os.getenv('TOTP_SECRET')

def get_angel_session():
    try:
        smartApi = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = smartApi.generateSession(CLIENT_CODE, PASSWORD, totp)
        if data['status']:
            return smartApi
        return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

# --- PATTERN LOGIC ---
def detect_patterns(df):
    v_pattern = False
    u_pattern = False
    p_pattern = False
    
    if len(df) < 5: return v_pattern, u_pattern, p_pattern
    
    vol = df['volume'].tolist()
    # Simplified Pattern Logic (V, U, Pyramid)
    if vol[-3] < vol[-4] and vol[-2] > vol[-3] and vol[-1] > vol[-2]:
        v_pattern = True
    if vol[-4] > vol[-3] > vol[-2] and vol[-1] > vol[-2]:
        u_pattern = True
    if vol[-3] > vol[-4] and vol[-2] > vol[-3] and vol[-1] < vol[-2]:
        p_pattern = True
        
    return v_pattern, u_pattern, p_pattern

@app.route('/health', methods=['GET'])
def health():
    session = get_angel_session()
    return jsonify({
        "status": "online",
        "api_connected": session is not None,
        "mode": "REAL_TIME" if session else "DEMO_FALLBACK"
    })

@app.route('/scan', methods=['POST'])
def scan():
    timeframe = request.json.get('timeframe', 'ONE_DAY')
    obj = get_angel_session()
    
    # List of top stocks to scan
    stocks = [
        {"symbol": "RELIANCE-EQ", "token": "3045"},
        {"symbol": "SBIN-EQ", "token": "3045"},
        {"symbol": "TCS-EQ", "token": "11536"},
        {"symbol": "HDFCBANK-EQ", "token": "1333"}
    ]
    
    final_results = []
    
    if not obj:
        return jsonify({"status": "error", "message": "Auth Failed", "data": []})

    for s in stocks:
        try:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": s['token'],
                "interval": timeframe,
                "fromdate": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M'),
                "todate": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            data = obj.getCandleData(historicParam)
            if data['status']:
                df = pd.DataFrame(data['data'], columns=['date','open','high','low','close','volume'])
                v, u, p = detect_patterns(df)
                
                if v or u or p:
                    final_results.append({
                        "ticker": s['symbol'],
                        "price": df['close'].iloc[-1],
                        "change": round(((df['close'].iloc[-1] - df['close'].iloc[-2])/df['close'].iloc[-2])*100, 2),
                        "v_pat": v, "u_pat": u, "p_pat": p,
                        "vma_status": "Bullish" if df['volume'].iloc[-1] > df['volume'].mean() else "Neutral"
                    })
        except:
            continue

    return jsonify({"status": "success", "data": final_results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
