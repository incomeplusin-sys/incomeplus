"""
INCOMEPLUS WEB API - FLASK VERSION
Optimized for Railway deployment with GitHub Pages frontend
UPDATED VERSION: Now uses Alpha Vantage API instead of yfinance
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# ========== ENHANCED CORS SETTINGS FOR GITHUB PAGES ==========
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://incomeplusin-sys.github.io",  # Your GitHub Pages
            "http://localhost:8000",              # Local testing
            "http://127.0.0.1:8000",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ========== ALPHA VANTAGE CONFIGURATION ==========
ALPHA_VANTAGE_API_KEY = "JMY6SM927NKIJIXI"  # YOUR API KEY
ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE = 5
ALPHA_VANTAGE_DAILY_LIMIT = 25

# Global session tracker to prevent excessive logins
session_data = {"token": None, "last_login": None}

# ========== ALL YOUR STOCKS LIST ==========
ALL_INDIAN_STOCKS = [
    "360ONE.NS", "ABB.NS", "APLAPOLLO.NS", "AUBANK.NS", "ADANIENSOL.NS",
    "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ABCAPITAL.NS", "ALKEM.NS",
    "AMBER.NS", "AMBUJACEM.NS", "ANGELONE.NS", "APOLLOHOSP.NS", "ASHOKLEY.NS",
    "ASIANPAINT.NS", "ASTRAL.NS", "AUROPHARMA.NS", "DMART.NS", "AXISBANK.NS",
    "BSE.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BANDHANBNK.NS",
    "BANKBARODA.NS", "BANKINDIA.NS", "BDL.NS", "BEL.NS", "BHARATFORG.NS",
    "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BLUESTARCO.NS",
    "BOSCHLTD.NS", "BRITANNIA.NS", "CGPOWER.NS", "CANBK.NS", "CDSL.NS",
    "CHOLAFIN.NS", "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS",
    "CAMS.NS", "CONCOR.NS", "CROMPTON.NS", "CUMMINSIND.NS", "CYIENT.NS",
    "DLF.NS", "DABUR.NS", "DALBHARAT.NS", "DELHIVERY.NS", "DIVISLAB.NS",
    "DIXON.NS", "DRREDDY.NS", "ETERNAL.NS", "EICHERMOT.NS", "EXIDEIND.NS",
    "NYKAA.NS", "FORTIS.NS", "GAIL.NS", "GMRAIRPORT.NS", "GLENMARK.NS",
    "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCAMC.NS",
    "HDFCBANK.NS", "HDFCLIFE.NS", "HFCL.NS", "HAVELLS.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HAL.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS",
    "POWERINDIA.NS", "HUDCO.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS",
    "IDFCFIRSTB.NS", "IIFL.NS", "ITC.NS", "INDIANB.NS", "IEX.NS", "IOC.NS",
    "IRCTC.NS", "IRFC.NS", "IREDA.NS", "IGL.NS", "INDUSTOWER.NS", "INDUSINDBK.NS",
    "NAUKRI.NS", "INFY.NS", "INOXWIND.NS", "INDIGO.NS", "JINDALSTEL.NS",
    "JSWENERGY.NS", "JSWSTEEL.NS", "JIOFIN.NS", "JUBLFOOD.NS", "KEI.NS",
    "KPITTECH.NS", "KALYANKJIL.NS", "KAYNES.NS", "KFINTECH.NS", "KOTAKBANK.NS",
    "LTF.NS", "LICHSGFIN.NS", "LTIM.NS", "LT.NS", "LAURUSLABS.NS", "LICI.NS",
    "LODHA.NS", "LUPIN.NS", "M&M.NS", "MANAPPURAM.NS", "MANKIND.NS", "MARICO.NS",
    "MARUTI.NS", "MFSL.NS", "MAXHEALTH.NS", "MAZDOCK.NS", "MPHASIS.NS", "MCX.NS",
    "MUTHOOTFIN.NS", "NBCC.NS", "NCC.NS", "NHPC.NS", "NMDC.NS", "NTPC.NS",
    "NATIONALUM.NS", "NESTLEIND.NS", "NUVAMA.NS", "OBEROIRLTY.NS", "ONGC.NS",
    "OIL.NS", "PAYTM.NS", "OFSS.NS", "POLICYBZR.NS", "PGEL.NS", "PIIND.NS",
    "PNBHOUSING.NS", "PAGEIND.NS", "PATANJALI.NS", "PERSISTENT.NS", "PETRONET.NS",
    "PIDILITIND.NS", "PPLPHARMA.NS", "POLYCAB.NS", "PFC.NS", "POWERGRID.NS",
    "PRESTIGE.NS", "PNB.NS", "RBLBANK.NS", "RECLTD.NS", "RVNL.NS", "RELIANCE.NS",
    "SBICARD.NS", "SBILIFE.NS", "SHREECEM.NS", "SRF.NS", "SAMMAANCAP.NS",
    "MOTHERSON.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", "SOLARINDS.NS", "SONACOMS.NS",
    "SBIN.NS", "SAIL.NS", "SUNPHARMA.NS", "SUPREMEIND.NS", "SUZLON.NS", "SYNGENE.NS",
    "TATACONSUM.NS", "TITAGARH.NS", "TVSMOTOR.NS", "TCS.NS", "TATAELXSI.NS",
    "TMPV.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS", "TECHM.NS",
    "FEDERALBNK.NS", "INDHOTEL.NS", "PHOENIXLTD.NS", "TITAN.NS", "TORNTPHARM.NS",
    "TORNTPOWER.NS", "TRENT.NS", "TIINDIA.NS", "UNOMINDA.NS", "UPL.NS",
    "ULTRACEMCO.NS", "UNIONBANK.NS", "UNITDSPR.NS", "VBL.NS", "VEDL.NS",
    "IDEA.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZYDUSLIFE.NS"
]

# ========== ALPHA VANTAGE DATA FETCHER ==========
def fetch_stock_data_alpha_vantage(ticker):
    """Fetch real stock data from Alpha Vantage"""
    try:
        symbol = ticker.replace(".NS", ".BSE")
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        
        r = requests.get(url)
        data = r.json()
        
        if "Time Series (Daily)" not in data:
            return None
            
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# ========== PATTERN DETECTION LOGIC ==========
def detect_u_pattern(volumes):
    if len(volumes) < 6: return False
    last_6 = volumes[-6:]
    midpoint = len(last_6) // 2
    left = last_6[:midpoint]
    right = last_6[midpoint:]
    is_descending = all(left[i] > left[i+1] for i in range(len(left)-1))
    is_ascending = all(right[i] < right[i+1] for i in range(len(right)-1))
    return is_descending and is_ascending

def detect_v_pattern(volumes):
    if len(volumes) < 5: return False
    last_5 = volumes[-5:]
    return last_5[2] == min(last_5) and last_5[3] > last_5[2] and last_5[4] > last_5[3]

# ========== API ENDPOINTS ==========
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/scan', methods=['POST'])
def scan_stocks():
    results = []
    # Limit for demo/free tier
    stocks_to_scan = ALL_INDIAN_STOCKS[:5]
    
    for ticker in stocks_to_scan:
        df = fetch_stock_data_alpha_vantage(ticker)
        if df is not None and len(df) >= 10:
            volumes = df['Volume'].values
            closes = df['Close'].values
            
            u_pat = detect_u_pattern(volumes)
            v_pat = detect_v_pattern(volumes)
            
            change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
            
            results.append({
                "ticker": ticker,
                "price": round(closes[-1], 2),
                "change_percent": round(change, 2),
                "volume": int(volumes[-1]),
                "u_pattern": u_pat,
                "v_pattern": v_pat
            })
            
    return jsonify({
        "status": "success",
        "count": len(results),
        "data": results,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)