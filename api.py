import os
import requests
import pandas as pd
import pyotp
from flask import Flask, jsonify, request
from flask_cors import CORS
from SmartApi import SmartConnect
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# --- GLOBAL DATA STORE ---
SCRIP_MASTER = None

def fetch_scrip_master():
    """Downloads the latest Angel One Token List automatically"""
    global SCRIP_MASTER
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        SCRIP_MASTER = pd.DataFrame(response.json())
        print("✅ NSE & F&O Tokens Loaded Successfully")
    except Exception as e:
        print(f"❌ Failed to download scrip master: {e}")

def get_token_info(symbol, segment="NSE"):
    """Finds the correct token and trading symbol dynamically"""
    if SCRIP_MASTER is None: return None
    try:
        res = SCRIP_MASTER[(SCRIP_MASTER['symbol'] == symbol) & (SCRIP_MASTER['exch_seg'] == segment)]
        if not res.empty:
            return {"token": res.iloc[0]['token'], "tradingsymbol": res.iloc[0]['symbol']}
    except: return None

def get_session():
    try:
        # CLEANING: .strip() removes accidental spaces, .upper() ensures correct case
        api_key = os.getenv('AOUtmyst').strip()
        client_code = os.getenv('AABZ050479').strip().upper()
        password = os.getenv('0204').strip() # Your 4-digit MPIN
        totp_secret = os.getenv('GWO7RQCDT7VAAOQZOLE4AL7HGY').strip().replace(" ", "")

        smartApi = SmartConnect(api_key=api_key)
        # Generate the 6-digit code from the secret
        totp_code = pyotp.TOTP(totp_secret).now()
        
        data = smartApi.generateSession(client_code, password, totp_code)
        
        if data.get('status'):
            print(f"✅ Login Successful for {client_code}")
            return smartApi
        else:
            print(f"❌ Login Failed: {data.get('message')}")
            return None
    except Exception as e:
        print(f"⚠️ Session Error: {str(e)}")
        return None

def detect_patterns(df):
    if len(df) < 20: return False, False, False
    vols = df['volume'].astype(float).tolist()
    avg_vol = sum(vols[-20:]) / 20
    curr_vol = vols[-1]
    is_valid = curr_vol > avg_vol
    v_pat = is_valid and (vols[-3] > vols[-2] and vols[-1] > vols[-2])
    u_pat = is_valid and (vols[-4] > vols[-3] and vols[-3] > vols[-2] and vols[-1] > vols[-2])
    p_pat = is_valid and (vols[-2] > vols[-3] and vols[-2] > vols[-1])
    return v_pat, u_pat, p_pat

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "message": "Scanner is active and connected to NSE"
    })

@app.route('/scan', methods=['POST'])
def scan():
    sector = request.json.get('sector', 'EQUITY')
    timeframe = request.json.get('timeframe', 'ONE_DAY')
    obj = get_session()
    if not obj: return jsonify({"status": "error", "message": "Auth Failed"})
    
    if sector == "INDEX_FUT":
        targets = [{"s": "NIFTY29JAN26FUT", "ex": "NFO"}, {"s": "BANKNIFTY29JAN26FUT", "ex": "NFO"}]
    elif sector == "STOCK_FUT":
        targets = [{"s": "RELIANCE29JAN26FUT", "ex": "NFO"}]
    else:
        targets = [{"s": "RELIANCE-EQ", "ex": "NSE"}, {"s": "SBIN-EQ", "ex": "NSE"}, {"s": "TCS-EQ", "ex": "NSE"}]

    final_results = []
    for t in targets:
        info = get_token_info(t['s'], t['ex'])
        if not info: continue
        try:
            params = {
                "exchange": t['ex'], "symboltoken": info['token'], "interval": timeframe,
                "fromdate": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M'),
                "todate": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            data = obj.getCandleData(params)
            if data['status'] and data['data']:
                df = pd.DataFrame(data['data'], columns=['date','open','high','low','close','volume'])
                v, u, p = detect_patterns(df)
                if v or u or p:
                    final_results.append({
                        "ticker": t['s'], "price": df['close'].iloc[-1],
                        "change": round(((df['close'].iloc[-1] - df['close'].iloc[-2])/df['close'].iloc[-2])*100, 2),
                        "v_pat": v, "u_pat": u, "p_pat": p,
                        "vma_status": "Bullish" if df['volume'].iloc[-1] > (df['volume'].astype(float).tail(20).mean()) else "Neutral"
                    })
        except: continue
    return jsonify({"status": "success", "data": final_results})

if __name__ == '__main__':
    fetch_scrip_master()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
