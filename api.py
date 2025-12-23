"""
INCOMEPLUS WEB API - FLASK VERSION
Optimized for Railway deployment with GitHub Pages frontend
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
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

# ========== YOUR SCANNER FUNCTIONS ==========
def detect_v_pattern(volumes):
    if len(volumes) < 5:
        return False
    last_5 = volumes[-5:]
    conditions = [
        last_5[2] == min(last_5),
        last_5[3] > last_5[2],
        last_5[4] > last_5[3],
        last_5[2] < last_5[0],
        last_5[2] < last_5[1]
    ]
    return all(conditions)

def detect_u_pattern(volumes):
    if len(volumes) < 6:
        return False
    last_6 = volumes[-6:]
    conditions = [
        last_6[2] < last_6[1],
        last_6[3] < last_6[2],
        last_6[4] > last_6[3],
        last_6[5] > last_6[4],
        last_6[3] < last_6[0],
        last_6[3] < last_6[1]
    ]
    return all(conditions)

# ========== HELPER FUNCTION FOR SYMBOL FORMATTING ==========
def normalize_symbol(symbol):
    """Try different symbol formats for Indian stocks"""
    symbol = symbol.strip().upper()
    
    # If no suffix, try .NS and .BO
    if '.' not in symbol:
        return [f"{symbol}.NS", f"{symbol}.BO", symbol]
    
    # Already has suffix
    return [symbol]

# ========== API ENDPOINTS ==========

@app.route('/api/test-patterns', methods=['GET'])
def test_patterns():
    """Test endpoint with artificial patterns"""
    
    # Artificial V-pattern volumes: High, Medium, LOW, Medium, High
    v_pattern_volumes = [1000000, 800000, 300000, 600000, 900000]
    
    # Artificial U-pattern volumes: High, Medium, LOW, LOW, Medium, High
    u_pattern_volumes = [1000000, 700000, 400000, 350000, 500000, 800000]
    
    # Non-pattern volumes (random)
    no_pattern_volumes = [500000, 600000, 550000, 580000, 620000]
    
    v_detected = detect_v_pattern(v_pattern_volumes)
    u_detected = detect_u_pattern(u_pattern_volumes)
    no_pattern_v = detect_v_pattern(no_pattern_volumes)
    no_pattern_u = detect_u_pattern(no_pattern_volumes)
    
    return jsonify({
        "test_results": {
            "v_pattern_test": {
                "volumes": v_pattern_volumes,
                "detected": v_detected,
                "should_be": True
            },
            "u_pattern_test": {
                "volumes": u_pattern_volumes,
                "detected": u_detected,
                "should_be": True
            },
            "no_pattern_test": {
                "volumes": no_pattern_volumes,
                "v_detected": no_pattern_v,
                "u_detected": no_pattern_u,
                "should_be": False
            }
        },
        "pattern_logic_working": v_detected and u_detected and (not no_pattern_v) and (not no_pattern_u),
        "timestamp": datetime.now().isoformat()
    })
    
@app.route('/')
def home():
    return jsonify({
        "service": "IncomePlus Stock Scanner API",
        "version": "1.2",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        "status": "running",
        "frontend_url": "https://incomeplusin-sys.github.io/incomeplus/",
        "backend_url": "https://web-production-1b0f1.up.railway.app",
        "endpoints": {
            "/": "This information",
            "/api/health": "Health check",
            "/api/scan": "Scan stocks (GET with ?symbols= or POST JSON)",
            "/api/test": "Test data (no API calls)",
            "/api/debug": "Debug symbol lookup"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "IncomePlus API is working",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        "backend": "Railway",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/debug/<symbol>', methods=['GET'])
def debug_symbol(symbol):
    """Debug endpoint to check yfinance data for a symbol"""
    try:
        symbol_variations = normalize_symbol(symbol)
        results = []
        
        for sym in symbol_variations:
            try:
                print(f"DEBUG: Trying symbol: {sym}")
                stock_data = yf.download(sym, period="5d", progress=False, timeout=5)
                
                result = {
                    "symbol": sym,
                    "success": stock_data is not None and not stock_data.empty,
                    "rows": len(stock_data) if stock_data is not None else 0,
                    "columns": list(stock_data.columns) if stock_data is not None and not stock_data.empty else [],
                    "sample_data": stock_data.head(2).to_dict('records') if stock_data is not None and not stock_data.empty and len(stock_data) > 0 else None
                }
                results.append(result)
                
            except Exception as e:
                results.append({
                    "symbol": sym,
                    "success": False,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "original_symbol": symbol,
            "tried_variations": results,
            "recommendation": "Use .NS for NSE, .BO for BSE, or no suffix for US stocks",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/scan', methods=['GET', 'POST', 'OPTIONS'])
def scan_stocks():
    """Main scanning endpoint with enhanced logging"""
    try:
        # Handle OPTIONS for CORS
        if request.method == 'OPTIONS':
            return '', 200
        
        # Get symbols from request
        if request.method == 'POST':
            data = request.json or {}
            symbols = data.get('symbols', ["360ONE.NS","ABB.NS","APLAPOLLO.NS","AUBANK.NS","ADANIENSOL.NS","ADANIENT.NS","ADANIGREEN.NS","ADANIPORTS.NS","ABCAPITAL.NS","ALKEM.NS","AMBER.NS","AMBUJACEM.NS","ANGELONE.NS","APOLLOHOSP.NS","ASHOKLEY.NS","ASIANPAINT.NS","ASTRAL.NS","AUROPHARMA.NS","DMART.NS","AXISBANK.NS","BSE.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BANDHANBNK.NS","BANKBARODA.NS","BANKINDIA.NS","BDL.NS","BEL.NS","BHARATFORG.NS","BHEL.NS","BPCL.NS","BHARTIARTL.NS","BIOCON.NS","BLUESTARCO.NS","BOSCHLTD.NS","BRITANNIA.NS","CGPOWER.NS","CANBK.NS","CDSL.NS","CHOLAFIN.NS","CIPLA.NS","COALINDIA.NS","COFORGE.NS","COLPAL.NS","CAMS.NS","CONCOR.NS","CROMPTON.NS","CUMMINSIND.NS","CYIENT.NS","DLF.NS","DABUR.NS","DALBHARAT.NS","DELHIVERY.NS","DIVISLAB.NS","DIXON.NS","DRREDDY.NS","ETERNAL.NS","EICHERMOT.NS","EXIDEIND.NS","NYKAA.NS","FORTIS.NS","GAIL.NS","GMRAIRPORT.NS","GLENMARK.NS","GODREJCP.NS","GODREJPROP.NS","GRASIM.NS","HCLTECH.NS","HDFCAMC.NS","HDFCBANK.NS","HDFCLIFE.NS","HFCL.NS","HAVELLS.NS","HEROMOTOCO.NS","HINDALCO.NS","HAL.NS","HINDPETRO.NS","HINDUNILVR.NS","HINDZINC.NS","POWERINDIA.NS","HUDCO.NS","ICICIBANK.NS","ICICIGI.NS","ICICIPRULI.NS","IDFCFIRSTB.NS","IIFL.NS","ITC.NS","INDIANB.NS","IEX.NS","IOC.NS","IRCTC.NS","IRFC.NS","IREDA.NS","IGL.NS","INDUSTOWER.NS","INDUSINDBK.NS","NAUKRI.NS","INFY.NS","INOXWIND.NS","INDIGO.NS","JINDALSTEL.NS","JSWENERGY.NS","JSWSTEEL.NS","JIOFIN.NS","JUBLFOOD.NS","KEI.NS","KPITTECH.NS","KALYANKJIL.NS","KAYNES.NS","KFINTECH.NS","KOTAKBANK.NS","LTF.NS","LICHSGFIN.NS","LTIM.NS","LT.NS","LAURUSLABS.NS","LICI.NS","LODHA.NS","LUPIN.NS","M&M.NS","MANAPPURAM.NS","MANKIND.NS","MARICO.NS","MARUTI.NS","MFSL.NS","MAXHEALTH.NS","MAZDOCK.NS","MPHASIS.NS","MCX.NS","MUTHOOTFIN.NS","NBCC.NS","NCC.NS","NHPC.NS","NMDC.NS","NTPC.NS","NATIONALUM.NS","NESTLEIND.NS","NUVAMA.NS","OBEROIRLTY.NS","ONGC.NS","OIL.NS","PAYTM.NS","OFSS.NS","POLICYBZR.NS","PGEL.NS","PIIND.NS","PNBHOUSING.NS","PAGEIND.NS","PATANJALI.NS","PERSISTENT.NS","PETRONET.NS","PIDILITIND.NS","PPLPHARMA.NS","POLYCAB.NS","PFC.NS","POWERGRID.NS","PRESTIGE.NS","PNB.NS","RBLBANK.NS","RECLTD.NS","RVNL.NS","RELIANCE.NS","SBICARD.NS","SBILIFE.NS","SHREECEM.NS","SRF.NS","SAMMAANCAP.NS","MOTHERSON.NS","SHRIRAMFIN.NS","SIEMENS.NS","SOLARINDS.NS","SONACOMS.NS","SBIN.NS","SAIL.NS","SUNPHARMA.NS","SUPREMEIND.NS","SUZLON.NS","SYNGENE.NS","TATACONSUM.NS","TITAGARH.NS","TVSMOTOR.NS","TCS.NS","TATAELXSI.NS","TMPV.NS","TATAPOWER.NS","TATASTEEL.NS","TATATECH.NS","TECHM.NS","FEDERALBNK.NS","INDHOTEL.NS","PHOENIXLTD.NS","TITAN.NS","TORNTPHARM.NS","TORNTPOWER.NS","TRENT.NS","TIINDIA.NS","UNOMINDA.NS","UPL.NS","ULTRACEMCO.NS","UNIONBANK.NS","UNITDSPR.NS","VBL.NS","VEDL.NS","IDEA.NS","VOLTAS.NS","WIPRO.NS","YESBANK.NS","ZYDUSLIFE.NS"])
        else:
            # GET request with query parameter
            symbols_param = request.args.get('symbols', "AAPL,GOOGL,MSFT")  # Default to US stocks
            symbols = [s.strip() for s in symbols_param.split(',')]
        
        # Limit symbols for performance
        symbols = symbols[:8]
        
        results = []
        failed_symbols = []
        
        print(f"SCAN REQUEST: {symbols}")
        
        for symbol in symbols:
            try:
                # Try different symbol formats
                symbol_variations = normalize_symbol(symbol)
                stock_data = None
                used_symbol = symbol
                
                for sym_var in symbol_variations:
                    try:
                        print(f"Downloading: {sym_var}")
                        stock_data = yf.download(
                            sym_var, 
                            period="1mo", 
                            progress=False,
                            timeout=8
                        )
                        
                        if stock_data is not None and not stock_data.empty and len(stock_data) >= 10:
                            used_symbol = sym_var
                            print(f"✓ Success: {sym_var} ({len(stock_data)} rows)")
                            break
                        else:
                            print(f"✗ No data: {sym_var}")
                            stock_data = None
                    except Exception as e:
                        print(f"✗ Error {sym_var}: {str(e)}")
                        continue
                
                # Check if we got data
                if stock_data is None or stock_data.empty:
                    failed_symbols.append({
                        "symbol": symbol, 
                        "error": "no data from yfinance",
                        "tried_variations": symbol_variations
                    })
                    continue
                
                if len(stock_data) < 10:
                    failed_symbols.append({
                        "symbol": symbol,
                        "error": f"only {len(stock_data)} data points (need at least 10)",
                        "rows": len(stock_data)
                    })
                    continue
                
                # Get volumes
                volumes = stock_data['Volume'].values
                
                # Detect patterns
                v_pattern = detect_v_pattern(volumes)
                u_pattern = detect_u_pattern(volumes)
                
                # Get price data
                current_price = float(stock_data['Close'].iloc[-1])
                prev_price = float(stock_data['Close'].iloc[-2])
                price_change = ((current_price - prev_price) / prev_price) * 100
                
                # Prepare result
                clean_symbol = used_symbol.replace('.NS', '').replace('.BO', '')
                
                result = {
                    "symbol": clean_symbol,
                    "original_symbol": symbol,
                    "used_symbol": used_symbol,
                    "price": round(current_price, 2),
                    "change_percent": round(price_change, 2),
                    "v_pattern": v_pattern,
                    "u_pattern": u_pattern,
                    "volume": int(volumes[-1]),
                    "data_points": len(stock_data),
                    "last_updated": datetime.now().isoformat(),
                    "status": "pattern_found" if (v_pattern or u_pattern) else "no_pattern"
                }
                results.append(result)
                    
            except Exception as e:
                print(f"ERROR processing {symbol}: {str(e)}")
                failed_symbols.append({
                    "symbol": symbol, 
                    "error": str(e),
                    "type": "processing_error"
                })
                continue
        
        response = {
            "success": True,
            "count": len(results),
            "results": results,
            "scanned": len(symbols),
            "failed": failed_symbols,
            "timestamp": datetime.now().isoformat(),
            "api_version": "1.2",
            "note": "Use .NS for NSE India, .BO for BSE India, or no suffix for US stocks"
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/test', methods=['GET'])
def test_scan():
    """Test endpoint with sample data (no API calls)"""
    return jsonify({
        "success": True,
        "count": 2,
        "results": [
            {
                "symbol": "RELIANCE",
                "price": 2850.50,
                "change_percent": 1.25,
                "v_pattern": True,
                "u_pattern": False,
                "volume": 7506011,
                "data_points": 30,
                "last_updated": datetime.now().isoformat(),
                "status": "pattern_found"
            },
            {
                "symbol": "TCS",
                "price": 3850.25,
                "change_percent": -0.75,
                "v_pattern": False,
                "u_pattern": True,
                "volume": 2365227,
                "data_points": 30,
                "last_updated": datetime.now().isoformat(),
                "status": "pattern_found"
            }
        ],
        "scanned": 3,
        "timestamp": datetime.now().isoformat(),
        "note": "This is test data - not from yfinance"
    })

# ========== START THE SERVER ==========
if __name__ == '__main__':
    # Get port from Railway environment or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 IncomePlus API Starting...")
    print(f"📍 Port: {port}")
    print(f"📍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    print(f"📍 Frontend: https://incomeplusin-sys.github.io/incomeplus/")
    print("=" * 50)
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
