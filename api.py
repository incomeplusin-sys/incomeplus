import os, requests, pyotp, time, pandas as pd
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
    """Downloads and filters the latest Angel One Token List"""
    global SCRIP_MASTER
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        SCRIP_MASTER = pd.DataFrame(response.json())
        # Optimization: Pre-filter for NSE and NFO only
        SCRIP_MASTER = SCRIP_MASTER[SCRIP_MASTER['exch_seg'].isin(['NSE', 'NFO'])]
        print("✅ NSE & F&O Tokens Loaded Successfully")
    except Exception as e:
        print(f"❌ Failed to download scrip master: {e}")

def get_futures_for_symbol(base_name):
    """Automatically finds Current, Next, and Far month futures"""
    try:
        # Filter for Futures (FUTSTK for stocks, FUTIDX for Nifty/BankNifty)
        df = SCRIP_MASTER[(SCRIP_MASTER['name'] == base_name) & 
                          (SCRIP_MASTER['instrumenttype'].isin(['FUTSTK', 'FUTIDX']))].copy()
        
        # Sort by expiry date to identify Current, Next, and Far months
        df['expiry'] = pd.to_datetime(df['expiry'])
        df = df.sort_values(by='expiry').head(3)
        
        results = []
        labels = ["Current", "Next", "Far"]
        for i, (_, row) in enumerate(df.iterrows()):
            results.append({
                "s": row['symbol'], "ex": "NFO", "token": row['token'], "label": labels[i]
            })
        return results
    except:
        return []

def get_session():
    """STABLE LOGIN: Your working logic with retries"""
    try:
        api_key = os.getenv('API_KEY').strip()
        client_code = os.getenv('CLIENT_CODE').strip().upper()
        password = os.getenv('PASSWORD').strip() 
        totp_secret = os.getenv('TOTP_SECRET').strip().replace(" ", "")
        smartApi = SmartConnect(api_key=api_key)
        for attempt in range(3):
            totp_code = pyotp.TOTP(totp_secret).now()
            data = smartApi.generateSession(client_code, password, totp_code)
            if data.get('status'):
                return smartApi
            time.sleep(2)
        return None
    except:
        return None

def detect_patterns(df):
    """STABLE LOGIC: Your volume pattern math"""
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
    return jsonify({"status": "online", "api_connected": SCRIP_MASTER is not None})

@app.route('/scan', methods=['POST'])
def scan():
    sector = request.json.get('sector', 'EQUITY')
    timeframe = request.json.get('timeframe', 'ONE_DAY')
    obj = get_session()
    if not obj: return jsonify({"status": "error", "message": "Auth Failed"})

    # --- UPGRADED TARGET SELECTION ---
    targets = []
    if sector == "INDEX_FUT":
        # Automatically gets Current, Next, Far for Nifty and BankNifty
        targets += get_futures_for_symbol("NIFTY")
        targets += get_futures_for_symbol("BANKNIFTY")
    
    elif sector == "STOCK_FUT":
        # Automatically gets Current, Next, Far for top volume stocks
        for stock in ["RELIANCE", "HDFCBANK", "SBIN", "ICICIBANK", "INFY"]:
            targets += get_futures_for_symbol(stock)
            
    else: # EQUITY (CASH)
        # Your preferred Equity list
        equity_symbols = ["RELIANCE-EQ", "SBIN-EQ", "TCS-EQ", "INFY-EQ", "HDFCBANK-EQ"]
        for s in equity_symbols:
            try:
                res = SCRIP_MASTER[SCRIP_MASTER['symbol'] == s].iloc[0]
                targets.append({"s": s, "ex": "NSE", "token": res['token'], "label": "Cash"})
            except: continue

    final_results = []
    for t in targets:
        try:
            params = {
                "exchange": t['ex'], "symboltoken": t['token'], "interval": timeframe,
                "fromdate": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M'),
                "todate": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            data = obj.getCandleData(params)
            if data['status'] and data['data']:
                df = pd.DataFrame(data['data'], columns=['date','open','high','low','close','volume'])
                v, u, p = detect_patterns(df)
                if v or u or p:
                    final_results.append({
                        "ticker": f"{t['s']} ({t.get('label', '')})",
                        "price": df['close'].iloc[-1],
                        "change": round(((df['close'].iloc[-1] - df['close'].iloc[-2])/df['close'].iloc[-2])*100, 2),
                        "v_pat": v, "u_pat": u, "p_pat": p,
                        "vma_status": "Bullish"
                    })
        except: continue
    return jsonify({"status": "success", "data": final_results})

if __name__ == '__main__':
    fetch_scrip_master()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
