import os, requests, pyotp, time, pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from SmartApi import SmartConnect
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# --- GLOBAL DATA STORE ---
SCRIP_MASTER = None
ACTIVE_SESSION = None
IST = pytz.timezone('Asia/Kolkata')

def fetch_scrip_master():
    """FIX: Pre-filters NSE/NFO for Railway memory efficiency"""
    global SCRIP_MASTER
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        df = pd.DataFrame(response.json())
        SCRIP_MASTER = df[df['exch_seg'].isin(['NSE', 'NFO'])].copy()
        print("✅ NSE & F&O Tokens Loaded Successfully")
    except Exception as e:
        print(f"❌ Scrip Master Error: {e}")

def get_session():
    """FIX: Direct Login with your verified credentials"""
    global ACTIVE_SESSION
    if ACTIVE_SESSION:
        try:
            ACTIVE_SESSION.getProfile()
            return ACTIVE_SESSION
        except:
            print("🔄 Session expired. Re-connecting...")

    try:
        api_key = "AOUtmyst"
        client_code = "AABZ050479"
        password = "0204"
        totp_secret = "GWO7RQCDT7VAAOQZOLE4AL7HGY"
        
        smartApi = SmartConnect(api_key=api_key)
        for attempt in range(3):
            totp_code = pyotp.TOTP(totp_secret).now()
            data = smartApi.generateSession(client_code, password, totp_code)
            if data.get('status'):
                print(f"✅ API LIVE: Connected as {client_code}")
                ACTIVE_SESSION = smartApi
                return ACTIVE_SESSION
            time.sleep(2)
        return None
    except Exception as e:
        print(f"❌ Login Failure: {str(e)}")
        return None

def get_futures_for_symbol(base_name):
    """Dynamic Current Month Future Lookup"""
    try:
        df = SCRIP_MASTER[(SCRIP_MASTER['name'] == base_name) & 
                          (SCRIP_MASTER['instrumenttype'].isin(['FUTSTK', 'FUTIDX']))].copy()
        df['expiry'] = pd.to_datetime(df['expiry'])
        df = df.sort_values(by='expiry').head(1) # Get Current Month
        
        return [{"s": row['symbol'], "ex": "NFO", "token": row['token'], "label": "FUT"}]
    except: return []

def detect_patterns(df):
    """SCANNER LOGIC: V, U, and Pyramid patterns with VMA Validation"""
    if len(df) < 20: return False, False, False
    vols = df['volume'].astype(float).tolist()
    avg_vol = sum(vols[-20:]) / 20
    curr_vol = vols[-1]
    
    is_valid = curr_vol > avg_vol
    v_pat = is_valid and (vols[-3] > vols[-2] and vols[-1] > vols[-2])
    u_pat = is_valid and (vols[-4] > vols[-3] and vols[-3] > vols[-2] and vols[-1] > vols[-2])
    p_pat = is_valid and (vols[-2] > vols[-3] and vols[-2] > vols[-1])
    return v_pat, u_pat, p_pat

@app.route('/scan', methods=['POST'])
def scan():
    sector = request.json.get('sector', 'EQUITY')
    timeframe = request.json.get('timeframe', 'ONE_DAY')
    obj = get_session()
    
    # --- INDENTATION FIXED HERE ---
    if not obj: 
        return jsonify({"status": "error", "message": "API Login Failed. Check MPIN/TOTP."})

    targets = []
    
    # --- TARGET LOGIC (ALL 200+ F&O STOCKS ENABLED) ---
    if sector == "STOCK_FUT":
        fo_symbols = SCRIP_MASTER[SCRIP_MASTER['instrumenttype'] == 'FUTSTK']['name'].unique().tolist()
        for s in fo_symbols:
            targets += get_futures_for_symbol(s)
            
    elif sector == "INDEX_FUT":
        for s in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
            targets += get_futures_for_symbol(s)
            
    else: # EQUITY (Cash)
        equity_list = ["RELIANCE-EQ", "SBIN-EQ", "TCS-EQ", "INFY-EQ", "HDFCBANK-EQ"]
        for s in equity_list:
            try:
                res = SCRIP_MASTER[SCRIP_MASTER['symbol'] == s].iloc[0]
                targets.append({"s": s, "ex": "NSE", "token": res['token'], "label": "Cash"})
            except: continue

    # --- ANYTIME/OFFLINE LOGIC ---
    now_ist = datetime.now(IST)
    from_date = (now_ist - timedelta(days=45)).strftime('%Y-%m-%d %H:%M')
    to_date = now_ist.strftime('%Y-%m-%d %H:%M')

    final_results = []
    for t in targets:
        try:
            data = obj.getCandleData({"exchange": t['ex'], "symboltoken": t['token'], "interval": timeframe, "fromdate": from_date, "todate": to_date})
            if data['status'] and data['data']:
                df = pd.DataFrame(data['data'], columns=['date','open','high','low','close','volume'])
                v, u, p = detect_patterns(df)
                if v or u or p:
                    final_results.append({
                        "ticker": f"{t['s']} ({t.get('label', '')})",
                        "date": df['date'].iloc[-1],
                        "price": df['close'].iloc[-1],
                        "change": round(((df['close'].iloc[-1] - df['close'].iloc[-2])/df['close'].iloc[-2])*100, 2),
                        "v_pat": v, "u_pat": u, "p_pat": p, "vma_status": "Bullish"
                    })
        except: continue
        
    return jsonify({"status": "success", "data": final_results})

@app.route('/health')
def health(): 
    return jsonify({"status": "online", "api_connected": ACTIVE_SESSION is not None})

if __name__ == '__main__':
    fetch_scrip_master()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
