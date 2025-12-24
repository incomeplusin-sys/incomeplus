"""
INCOMEPLUS WEB API - COMPLETE SCANNER VERSION
Optimized for Railway deployment with GitHub Pages frontend
With Historical Pattern Scanner and Fixed yfinance Period Issues
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# ========== ENHANCED CORS SETTINGS ==========
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://incomeplusin-sys.github.io",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ========== ALL INDIAN STOCKS LIST ==========
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

# ========== FIXED YFINANCE DATA FETCHING ==========
def fetch_stock_data(symbol, days=30):
    """Fetch stock data using start/end dates instead of period parameter"""
    try:
        print(f"🔍 [DEBUG] Fetching data for {symbol}, days={days}")
        
        # Calculate dates (FIX for Indian stocks)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Use start/end format instead of period
        stock_data = yf.download(
            symbol,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False,
            timeout=15
        )
        
        if stock_data.empty:
            print(f"⚠️ [DEBUG] No data returned for {symbol}")
            return None
        
        print(f"📊 [DEBUG] Success! Data shape: {stock_data.shape}")
        return stock_data
        
    except Exception as e:
        print(f"❌ [DEBUG] Error fetching {symbol}: {str(e)[:100]}")
        return None

# ========== HISTORICAL PATTERN SCANNER (FIXED) ==========
def scan_historical_patterns(symbol, months=6):
    """Scan historical data with FIXED date fetching"""
    try:
        print(f"🔍 [DEBUG] Starting historical scan for {symbol}, months={months}")
        
        # Calculate dates for the requested months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)  # Approximate 30 days per month
        
        print(f"📅 [DEBUG] Date range: {start_date.date()} to {end_date.date()}")
        
        # Fetch data with start/end dates
        stock_data = yf.download(
            symbol,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False,
            timeout=20
        )
        
        if stock_data.empty:
            print(f"⚠️ [DEBUG] No data returned for {symbol}")
            return []
        
        print(f"📊 [DEBUG] Data fetched: {len(stock_data)} rows")
        
        # Reset index for date handling
        df = stock_data.reset_index()
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        volumes = df['Volume'].values
        closes = df['Close'].values
        dates = df['Date'].values
        
        all_patterns = []
        
        # Scan through ALL data (sliding window)
        for start_idx in range(len(volumes) - 15):
            for window_size in [5, 6, 7, 8, 9, 10, 12, 15]:
                end_idx = start_idx + window_size
                
                if end_idx >= len(volumes):
                    continue
                
                window_volumes = volumes[start_idx:end_idx]
                window_dates = dates[start_idx:end_idx]
                window_prices = closes[start_idx:end_idx]
                
                # ========== V-PATTERN DETECTION ==========
                if window_size >= 5:
                    bottom_idx = np.argmin(window_volumes)
                    
                    if bottom_idx == 0 or bottom_idx == window_size - 1:
                        continue
                    
                    left_strict = all(window_volumes[i] > window_volumes[i+1] 
                                    for i in range(bottom_idx))
                    right_strict = all(window_volumes[bottom_idx+i] < window_volumes[bottom_idx+i+1] 
                                     for i in range(window_size - bottom_idx - 1))
                    
                    start_vol = window_volumes[0]
                    bottom_vol = window_volumes[bottom_idx]
                    end_vol = window_volumes[-1]
                    
                    drop_pct = ((start_vol - bottom_vol) / start_vol) * 100
                    recovery_pct = ((end_vol - bottom_vol) / bottom_vol) * 100
                    
                    if (left_strict and right_strict and drop_pct > 30 and recovery_pct > 30):
                        days_after = 5
                        after_end = min(end_idx + days_after, len(closes) - 1)
                        
                        if after_end > end_idx:
                            price_after_pattern = closes[after_end]
                            price_at_pattern_end = closes[end_idx]
                            future_change = ((price_after_pattern - price_at_pattern_end) / price_at_pattern_end) * 100
                            
                            try:
                                pattern_end_date = datetime.strptime(window_dates[-1], '%Y-%m-%d')
                                current_date = datetime.now()
                                days_since_pattern = (current_date - pattern_end_date).days
                            except:
                                days_since_pattern = len(dates) - end_idx
                            
                            pattern_info = {
                                'symbol': symbol.replace('.NS', ''),
                                'pattern_type': 'V_PATTERN',
                                'pattern_length': window_size,
                                'start_date': window_dates[0],
                                'end_date': window_dates[-1],
                                'days_ago': days_since_pattern,
                                'is_current_week': days_since_pattern <= 7,
                                'is_current_month': days_since_pattern <= 30,
                                'volume_details': {
                                    'start_volume': int(start_vol),
                                    'bottom_volume': int(bottom_vol),
                                    'end_volume': int(end_vol),
                                    'drop_percent': round(drop_pct, 1),
                                    'recovery_percent': round(recovery_pct, 1)
                                },
                                'price_details': {
                                    'start_price': round(float(window_prices[0]), 2),
                                    'end_price': round(float(window_prices[-1]), 2),
                                    'price_change_percent': round(((window_prices[-1] - window_prices[0]) / window_prices[0]) * 100, 2),
                                    'future_price_change': round(future_change, 2),
                                    'days_analyzed_after': days_after
                                },
                                'strictness_score': 1.0,
                                'pattern_quality': 'HIGH'
                            }
                            all_patterns.append(pattern_info)
                
                # ========== U-PATTERN DETECTION ==========
                if window_size >= 8:
                    min_volume = np.min(window_volumes)
                    bottom_indices = [i for i, vol in enumerate(window_volumes) 
                                     if vol <= min_volume * 1.15]
                    
                    if len(bottom_indices) < 3:
                        continue
                    
                    bottom_sorted = sorted(bottom_indices)
                    is_consecutive = all(bottom_sorted[i+1] - bottom_sorted[i] <= 2 
                                       for i in range(len(bottom_sorted)-1))
                    
                    if not is_consecutive:
                        continue
                    
                    bottom_start = bottom_sorted[0]
                    bottom_end = bottom_sorted[-1]
                    
                    left_decreasing = True
                    if bottom_start > 2:
                        for i in range(1, bottom_start + 1):
                            if window_volumes[i] > window_volumes[i-1] * 1.1:
                                left_decreasing = False
                                break
                    
                    right_increasing = True
                    if bottom_end < window_size - 2:
                        for i in range(bottom_end + 1, window_size):
                            if window_volumes[i] < window_volumes[i-1] * 0.9:
                                right_increasing = False
                                break
                    
                    start_vol = window_volumes[0]
                    end_vol = window_volumes[-1]
                    bottom_avg = np.mean([window_volumes[i] for i in bottom_indices])
                    
                    left_drop = ((start_vol - bottom_avg) / start_vol) * 100
                    right_rise = ((end_vol - bottom_avg) / bottom_avg) * 100
                    
                    if (left_decreasing and right_increasing and left_drop > 25 and right_rise > 35):
                        days_after = 5
                        after_end = min(end_idx + days_after, len(closes) - 1)
                        
                        if after_end > end_idx:
                            price_after = closes[after_end]
                            price_at_end = closes[end_idx]
                            future_change = ((price_after - price_at_end) / price_at_end) * 100
                            
                            try:
                                pattern_end_date = datetime.strptime(window_dates[-1], '%Y-%m-%d')
                                current_date = datetime.now()
                                days_since = (current_date - pattern_end_date).days
                            except:
                                days_since = len(dates) - end_idx
                            
                            pattern_info = {
                                'symbol': symbol.replace('.NS', ''),
                                'pattern_type': 'U_PATTERN',
                                'pattern_length': window_size,
                                'start_date': window_dates[0],
                                'end_date': window_dates[-1],
                                'days_ago': days_since,
                                'is_current_week': days_since <= 7,
                                'is_current_month': days_since <= 30,
                                'volume_details': {
                                    'start_volume': int(start_vol),
                                    'bottom_avg_volume': int(bottom_avg),
                                    'end_volume': int(end_vol),
                                    'bottom_days': len(bottom_indices),
                                    'drop_percent': round(left_drop, 1),
                                    'recovery_percent': round(right_rise, 1)
                                },
                                'price_details': {
                                    'start_price': round(float(window_prices[0]), 2),
                                    'end_price': round(float(window_prices[-1]), 2),
                                    'price_change_percent': round(((window_prices[-1] - window_prices[0]) / window_prices[0]) * 100, 2),
                                    'future_price_change': round(future_change, 2)
                                },
                                'strictness_score': 0.9,
                                'pattern_quality': 'HIGH'
                            }
                            all_patterns.append(pattern_info)
        
        print(f"✅ [DEBUG] Found {len(all_patterns)} patterns for {symbol}")
        return all_patterns
        
    except Exception as e:
        print(f"❌ [DEBUG] Error in historical scan for {symbol}: {str(e)[:200]}")
        return []

# ========== BASIC PATTERN DETECTION ==========
def detect_v_pattern(volumes):
    if len(volumes) < 5:
        return False
    
    last_5 = volumes[-5:]
    min_idx = np.argmin(last_5)
    
    return (min_idx in [2, 3] and 
            last_5[3] > last_5[2] * 1.05 and 
            last_5[4] > last_5[3] * 1.02)

def detect_u_pattern(volumes):
    if len(volumes) < 6:
        return False
    
    last_6 = volumes[-6:]
    min_idx = np.argmin(last_6)
    
    return (min_idx in [2, 3] and 
            last_6[3] < last_6[2] * 0.95 and 
            last_6[4] > last_6[3] * 1.05 and 
            last_6[5] > last_6[4] * 1.05)

def scan_single_stock(symbol):
    """Basic stock scanning with FIXED date fetching"""
    try:
        print(f"🔍 [DEBUG] Basic scan for {symbol}")
        
        # Use the fixed fetch function
        stock_data = fetch_stock_data(symbol, days=30)
        
        if stock_data is None or stock_data.empty:
            return {
                "symbol": symbol,
                "error": "insufficient data",
                "success": False
            }
        
        volumes = stock_data['Volume'].values
        closes = stock_data['Close'].values
        
        current_price = float(closes[-1]) if len(closes) > 0 else 0
        prev_price = float(closes[-2]) if len(closes) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
        
        v_pattern = detect_v_pattern(volumes)
        u_pattern = detect_u_pattern(volumes)
        
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        return {
            "symbol": clean_symbol,
            "price": round(current_price, 2),
            "change_percent": round(price_change, 2),
            "v_pattern": v_pattern,
            "u_pattern": u_pattern,
            "volume": int(volumes[-1]) if len(volumes) > 0 else 0,
            "data_points": len(stock_data),
            "success": True
        }
        
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e)[:100],
            "success": False
        }

# ========== DEMO MODE ==========
DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

# ========== API ENDPOINTS ==========
@app.route('/')
def home():
    return jsonify({
        "service": "IncomePlus Complete Stock Scanner API",
        "version": "4.0",
        "status": "running",
        "features": [
            "Historical Pattern Scanner (6 months)",
            "Fixed yfinance data fetching",
            "Strict Pattern Detection Rules",
            "All Indian Stocks Coverage"
        ],
        "endpoints": {
            "/": "This information",
            "/api/health": "Health check",
            "/api/scan": "Basic V/U pattern scan",
            "/api/scan-all": "Scan all 200+ stocks",
            "/api/scanner/historical": "Historical pattern analysis (6 months)",
            "/api/debug-scan/<symbol>": "Debug data fetch for symbol"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "4.0",
        "features": "Historical Scanner + Fixed yfinance",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/debug-scan/<symbol>', methods=['GET'])
def debug_scan(symbol):
    """Debug endpoint with FIXED data fetching"""
    try:
        print(f"🔍 [DEBUG-SCAN] Starting debug scan for {symbol}")
        
        # Test different approaches
        test_results = []
        
        # Test 1: Try with .NS suffix
        print(f"🔍 [DEBUG-SCAN] Test 1: {symbol}")
        stock_data1 = fetch_stock_data(symbol, days=30)
        
        if stock_data1 is not None and not stock_data1.empty:
            test_results.append({
                "symbol": symbol,
                "status": "SUCCESS",
                "data_points": len(stock_data1),
                "columns": list(stock_data1.columns),
                "date_range": {
                    "start": stock_data1.index[0].strftime('%Y-%m-%d') if len(stock_data1) > 0 else None,
                    "end": stock_data1.index[-1].strftime('%Y-%m-%d') if len(stock_data1) > 0 else None
                }
            })
        else:
            test_results.append({
                "symbol": symbol,
                "status": "FAILED",
                "error": "No data returned"
            })
        
        # Test 2: Try .BO suffix (Bombay Stock Exchange)
        if symbol.endswith('.NS'):
            symbol_bo = symbol.replace('.NS', '.BO')
            print(f"🔍 [DEBUG-SCAN] Test 2: {symbol_bo}")
            stock_data2 = fetch_stock_data(symbol_bo, days=30)
            
            if stock_data2 is not None and not stock_data2.empty:
                test_results.append({
                    "symbol": symbol_bo,
                    "status": "SUCCESS",
                    "data_points": len(stock_data2),
                    "columns": list(stock_data2.columns),
                    "date_range": {
                        "start": stock_data2.index[0].strftime('%Y-%m-%d') if len(stock_data2) > 0 else None,
                        "end": stock_data2.index[-1].strftime('%Y-%m-%d') if len(stock_data2) > 0 else None
                    }
                })
            else:
                test_results.append({
                    "symbol": symbol_bo,
                    "status": "FAILED",
                    "error": "No data returned"
                })
        
        return jsonify({
            "debug_scan": True,
            "symbol": symbol,
            "tests": test_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [DEBUG-SCAN] Error: {str(e)}")
        return jsonify({
            "error": str(e),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/scanner/historical', methods=['GET'])
def historical_scanner():
    """Historical scanner endpoint"""
    try:
        symbols_param = request.args.get('symbols', 'RELIANCE.NS,TCS.NS,INFY.NS')
        symbols = [s.strip() for s in symbols_param.split(',')]
        months = int(request.args.get('months', 6))
        highlight_current_week = request.args.get('current_week', 'true').lower() == 'true'
        
        print(f"🔍 [HISTORICAL] Starting scan for {len(symbols)} symbols")
        
        all_patterns = []
        
        for symbol in symbols[:10]:
            print(f"🔍 [HISTORICAL] Processing {symbol}")
            patterns = scan_historical_patterns(symbol, months)
            
            if highlight_current_week:
                for pattern in patterns:
                    if pattern['is_current_week']:
                        pattern['highlight'] = 'CURRENT_WEEK'
                        pattern['priority'] = 1
                    elif pattern['is_current_month']:
                        pattern['priority'] = 2
                    else:
                        pattern['priority'] = 3
            else:
                for pattern in patterns:
                    pattern['priority'] = 3
            
            all_patterns.extend(patterns)
            time.sleep(0.5)  # Rate limiting
        
        # Sort patterns
        all_patterns.sort(key=lambda x: (x.get('priority', 3), -x.get('strictness_score', 0)))
        
        # Categorize patterns
        current_week_patterns = [p for p in all_patterns if p.get('highlight') == 'CURRENT_WEEK']
        current_month_patterns = [p for p in all_patterns if p.get('is_current_month', False) and not p.get('is_current_week', False)]
        historical_patterns = [p for p in all_patterns if not p.get('is_current_month', False)]
        
        v_patterns = [p for p in all_patterns if p['pattern_type'] == 'V_PATTERN']
        u_patterns = [p for p in all_patterns if p['pattern_type'] == 'U_PATTERN']
        
        # Analyze outcomes
        pattern_outcomes = []
        for pattern in all_patterns:
            if 'future_price_change' in pattern['price_details']:
                outcome = {
                    'pattern_type': pattern['pattern_type'],
                    'days_after': pattern['price_details'].get('days_analyzed_after', 5),
                    'price_change': pattern['price_details']['future_price_change'],
                    'volume_drop': pattern['volume_details']['drop_percent'],
                    'volume_recovery': pattern['volume_details']['recovery_percent']
                }
                pattern_outcomes.append(outcome)
        
        return jsonify({
            'success': True,
            'total_patterns_found': len(all_patterns),
            'pattern_distribution': {
                'v_patterns': len(v_patterns),
                'u_patterns': len(u_patterns),
                'current_week': len(current_week_patterns),
                'current_month': len(current_month_patterns),
                'historical': len(historical_patterns)
            },
            'current_week_patterns': current_week_patterns[:10],
            'current_month_patterns': current_month_patterns[:10],
            'all_patterns': all_patterns[:50],
            'pattern_outcomes_analysis': {
                'total_patterns_analyzed': len(pattern_outcomes),
                'avg_price_change_after_5_days': round(np.mean([p['price_change'] for p in pattern_outcomes]), 2) if pattern_outcomes else 0,
                'successful_patterns': len([p for p in pattern_outcomes if p['price_change'] > 0]),
                'failed_patterns': len([p for p in pattern_outcomes if p['price_change'] <= 0]),
                'success_rate': f"{(len([p for p in pattern_outcomes if p['price_change'] > 0])/len(pattern_outcomes)*100):.1f}%" if pattern_outcomes else "0%"
            },
            'strictness_note': 'Patterns detected with STRICT rules: Min 30% volume changes required',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [HISTORICAL] Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/scan', methods=['GET'])
def scan_stocks():
    """Basic scanning endpoint"""
    try:
        symbols_param = request.args.get('symbols', 'RELIANCE.NS,TCS.NS,INFY.NS')
        symbols = [s.strip() for s in symbols_param.split(',')][:25]
        
        results = []
        patterns_found = 0
        
        for symbol in symbols:
            result = scan_single_stock(symbol)
            if result.get("success", False):
                if result["v_pattern"] or result["u_pattern"]:
                    patterns_found += 1
                results.append(result)
        
        return jsonify({
            "success": True,
            "count": len(results),
            "patterns_found": patterns_found,
            "results": results,
            "scanned": len(symbols),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [SCAN] Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/scan-all', methods=['GET'])
def scan_all_stocks():
    """Scan all stocks with pagination"""
    try:
        page = int(request.args.get('page', 0))
        page_size = int(request.args.get('page_size', 20))
        
        start_idx = page * page_size
        end_idx = start_idx + page_size
        symbols_to_scan = ALL_INDIAN_STOCKS[start_idx:end_idx]
        
        if not symbols_to_scan:
            return jsonify({
                "success": True,
                "message": "No more stocks to scan",
                "has_next_page": False
            })
        
        results = []
        
        for symbol in symbols_to_scan:
            result = scan_single_stock(symbol)
            if result.get("success", False):
                results.append(result)
            time.sleep(0.2)
        
        return jsonify({
            "success": True,
            "page": page,
            "page_size": page_size,
            "total_stocks": len(ALL_INDIAN_STOCKS),
            "results": results,
            "has_next_page": end_idx < len(ALL_INDIAN_STOCKS),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ========== START THE SERVER ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 IncomePlus Complete Scanner v4.0 Starting...")
    print(f"📍 Port: {port}")
    print("=" * 60)
    print("📊 FEATURES:")
    print("   • Historical Pattern Scanner (6 months)")
    print("   • FIXED yfinance data fetching (start/end dates)")
    print("   • Strict Pattern Detection Rules")
    print("   • All Indian Stocks Coverage")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
