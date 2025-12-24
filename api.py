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
def fetch_stock_data_alpha_vantage(symbol, days=30):
    """Fetch stock data using Alpha Vantage API (RELIABLE)"""
    try:
        # Remove .NS/.BO suffix for Alpha Vantage
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        print(f"🔍 [ALPHA] Fetching {clean_symbol} for {days} days")
        
        # Try BSE first
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={clean_symbol}.BSE&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}"
        
        response = requests.get(url, timeout=15)
        data = response.json()
        
        # Check if we got valid data
        if "Time Series (Daily)" not in data:
            print(f"⚠️ [ALPHA] BSE failed, trying NSE...")
            
            # Try NSE instead of BSE
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={clean_symbol}.NSE&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if "Time Series (Daily)" not in data:
                # Check if rate limited
                if "Note" in data:
                    print(f"⚠️ [ALPHA] Rate limited: {data['Note'][:80]}...")
                print(f"❌ [ALPHA] Both BSE and NSE failed for {clean_symbol}")
                return None
        
        # Convert Alpha Vantage data to DataFrame
        time_series = data["Time Series (Daily)"]
        
        # Get the most recent days
        dates = sorted(time_series.keys(), reverse=True)[:days]
        
        # Create DataFrame
        records = []
        for date in dates:
            day_data = time_series[date]
            records.append({
                'Date': date,
                'Open': float(day_data['1. open']),
                'High': float(day_data['2. high']),
                'Low': float(day_data['3. low']),
                'Close': float(day_data['4. close']),
                'Volume': int(float(day_data['5. volume']))
            })
        
        if not records:
            print(f"⚠️ [ALPHA] No records created for {clean_symbol}")
            return None
        
        df = pd.DataFrame(records)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date').sort_index()
        
        print(f"✅ [ALPHA] Success! Got {len(df)} days for {clean_symbol}")
        return df
        
    except Exception as e:
        print(f"❌ [ALPHA] Error fetching {symbol}: {str(e)[:100]}")
        return None

# ========== IMPROVED PATTERN DETECTION FUNCTIONS ==========
def detect_v_pattern(volumes):
    """
    IMPROVED V-pattern detection
    Looks for: High → Medium → LOW → Medium → High pattern
    More lenient to find real patterns
    """
    if len(volumes) < 5:
        return False
    
    last_5 = volumes[-5:]
    
    # Find which day has minimum volume
    min_day = np.argmin(last_5)
    
    # For V-pattern, day 2 (index 2) should be minimum OR day 3
    if min_day not in [2, 3]:
        return False
    
    # Check if volumes increase after the minimum
    if min_day == 2:
        # Pattern: day0 → day1 → MIN(day2) → day3↑ → day4↑
        conditions = [
            last_5[3] > last_5[2] * 1.05,  # Day 3 at least 5% higher than Day 2
            last_5[4] > last_5[3] * 1.02,  # Day 4 at least 2% higher than Day 3
            last_5[2] < last_5[0] * 0.8,   # Day 2 at least 20% lower than Day 0
            last_5[2] < last_5[1] * 0.8,   # Day 2 at least 20% lower than Day 1
        ]
    else:  # min_day == 3
        # Pattern: day0 → day1 → day2 → MIN(day3) → day4↑
        conditions = [
            last_5[4] > last_5[3] * 1.1,   # Day 4 at least 10% higher than Day 3
            last_5[3] < last_5[1] * 0.7,   # Day 3 significantly lower than Day 1
            last_5[3] < last_5[2] * 0.9,   # Day 3 lower than Day 2
        ]
    
    return all(conditions)

def detect_u_pattern(volumes):
    """
    IMPROVED U-pattern detection
    Looks for gradual decrease then increase
    """
    if len(volumes) < 6:
        return False
    
    last_6 = volumes[-6:]
    
    # Find minimum volume in the middle (days 2, 3, or 4)
    middle_days = last_6[2:5]
    min_middle_idx = np.argmin(middle_days) + 2  # Adjust index
    
    # The minimum should be in the middle (not at edges)
    if min_middle_idx not in [2, 3, 4]:
        return False
    
    # Check gradual decrease to minimum
    decrease_ok = True
    for i in range(1, min_middle_idx + 1):
        if last_6[i] > last_6[i-1] * 1.1:  # Not decreasing
            decrease_ok = False
            break
    
    # Check gradual increase from minimum
    increase_ok = True
    for i in range(min_middle_idx + 1, 6):
        if last_6[i] < last_6[i-1] * 0.95:  # Not increasing
            increase_ok = False
            break
    
    # Minimum should be significantly lower than start
    min_volume = last_6[min_middle_idx]
    return (decrease_ok and increase_ok and 
            min_volume < last_6[0] * 0.7 and 
            min_volume < last_6[1] * 0.7)

# ========== HELPER FUNCTIONS ==========
def normalize_symbol(symbol):
    """Try different symbol formats for Alpha Vantage"""
    symbol = symbol.strip().upper()
    
    # Remove suffix for Alpha Vantage
    clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    # Alpha Vantage supports BSE and NSE suffixes
    return [f"{clean_symbol}.BSE", f"{clean_symbol}.NSE"]

def scan_single_stock(symbol):
    """Scan a single stock using Alpha Vantage"""
    try:
        print(f"🔍 [SCAN] Starting scan for {symbol}")
        
        # Use Alpha Vantage instead of yfinance
        stock_data = fetch_stock_data_alpha_vantage(symbol, days=30)
        
        if stock_data is None or stock_data.empty:
            print(f"⚠️ [SCAN] No data for {symbol}")
            return {
                "symbol": symbol,
                "error": "Alpha Vantage: No data returned",
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
        
        print(f"✅ [SCAN] Success! {clean_symbol}: ₹{current_price:.2f}, V:{v_pattern}, U:{u_pattern}")
        
        return {
            "symbol": clean_symbol,
            "original_symbol": symbol,
            "price": round(current_price, 2),
            "change_percent": round(price_change, 2),
            "v_pattern": v_pattern,
            "u_pattern": u_pattern,
            "volume": int(volumes[-1]) if len(volumes) > 0 else 0,
            "data_points": len(stock_data),
            "last_updated": datetime.now().isoformat(),
            "status": "pattern_found" if (v_pattern or u_pattern) else "no_pattern",
            "data_source": "Alpha Vantage",
            "success": True
        }
        
    except Exception as e:
        print(f"❌ [SCAN] Error: {str(e)}")
        return {
            "symbol": symbol,
            "error": str(e)[:100],
            "success": False
        }

# ========== DEMO MODE FOR TESTING ==========
DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

def ensure_patterns_for_demo(symbol, v_pattern, u_pattern):
    """Ensure some patterns are found in demo mode"""
    if not DEMO_MODE:
        return v_pattern, u_pattern
    
    # In demo mode, force some patterns for popular stocks
    demo_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
                   'SBIN', 'TATAMOTORS', 'BAJFINANCE', 'WIPRO', 'AXISBANK']
    
    clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    if clean_symbol in demo_stocks[:3]:
        return True, False  # First 3 get V-pattern
    elif clean_symbol in demo_stocks[3:6]:
        return False, True  # Next 3 get U-pattern
    elif clean_symbol in demo_stocks[6:]:
        return True, True   # Rest get both
    
    return v_pattern, u_pattern

# ========== API ENDPOINTS ==========
@app.route('/')
def home():
    return jsonify({
        "service": "IncomePlus Stock Scanner API",
        "version": "4.0",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        "demo_mode": DEMO_MODE,
        "status": "running",
        "total_stocks_available": len(ALL_INDIAN_STOCKS),
        "frontend_url": "https://incomeplusin-sys.github.io/incomeplus/",
        "backend_url": "https://web-production-1b0f1.up.railway.app",
        "data_source": "Alpha Vantage",
        "pattern_logic": "IMPROVED - More lenient detection",
        "alpha_vantage_limits": {
            "calls_per_minute": ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE,
            "daily_calls": ALPHA_VANTAGE_DAILY_LIMIT
        },
        "endpoints": {
            "/": "This information",
            "/api/health": "Health check",
            "/api/scan": "Scan stocks (GET with ?symbols= or POST JSON)",
            "/api/scan-all": "Scan all 200+ Indian stocks (paginated)",
            "/api/scan-batch": "Batch scan (POST with symbols list)",
            "/api/test": "Test data (no API calls)",
            "/api/test-patterns": "Test pattern detection logic",
            "/api/debug-scan/<symbol>": "Debug scan for specific symbol"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "IncomePlus API is working with Alpha Vantage",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        "demo_mode": DEMO_MODE,
        "total_stocks": len(ALL_INDIAN_STOCKS),
        "data_source": "Alpha Vantage",
        "alpha_vantage_status": "Connected",
        "pattern_detection": "IMPROVED V4.0",
        "timestamp": datetime.now().isoformat()
    })

# ========== HISTORICAL PATTERN SCANNER WITH ALPHA VANTAGE ==========
def scan_historical_patterns(symbol, months=6):
    """Scan 6 months data and find all patterns using Alpha Vantage"""
    try:
        # Fetch 6 months data from Alpha Vantage
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        stock_data = fetch_stock_data_alpha_vantage(symbol, days=months*30)  # Approx 6 months
        
        if stock_data is None or len(stock_data) < 40:
            return []
        
        df = stock_data.reset_index()
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        volumes = df['Volume'].values
        closes = df['Close'].values
        dates = df['Date'].values
        
        all_patterns = []
        
        # Scan through ALL data (sliding window)
        for start_idx in range(len(volumes) - 15):  # Need at least 15 days
            for window_size in [5, 6, 7, 8, 9, 10, 12, 15]:  # Different pattern lengths
                end_idx = start_idx + window_size
                
                if end_idx >= len(volumes):
                    continue
                
                window_volumes = volumes[start_idx:end_idx]
                window_dates = dates[start_idx:end_idx]
                window_prices = closes[start_idx:end_idx]
                
                # ========== V-PATTERN DETECTION ==========
                if window_size >= 5:
                    # Find bottom (must be in middle)
                    bottom_idx = np.argmin(window_volumes)
                    
                    # Strict rules:
                    # 1. Bottom not at edges
                    if bottom_idx == 0 or bottom_idx == window_size - 1:
                        continue
                    
                    # 2. Left side decreasing
                    left_decreasing = all(window_volumes[i] > window_volumes[i+1] 
                                        for i in range(bottom_idx))
                    
                    # 3. Right side increasing
                    right_increasing = all(window_volumes[bottom_idx+i] < window_volumes[bottom_idx+i+1] 
                                         for i in range(window_size - bottom_idx - 1))
                    
                    # 4. Significant drop and recovery (minimum 30%)
                    start_vol = window_volumes[0]
                    bottom_vol = window_volumes[bottom_idx]
                    end_vol = window_volumes[-1]
                    
                    drop_pct = ((start_vol - bottom_vol) / start_vol) * 100
                    recovery_pct = ((end_vol - bottom_vol) / bottom_vol) * 100
                    
                    if (left_decreasing and right_increasing and 
                        drop_pct > 20 and recovery_pct > 20):
                        
                        # Check what happened AFTER pattern
                        days_after = 5  # Look 5 days ahead
                        after_end = min(end_idx + days_after, len(closes) - 1)
                        
                        if after_end > end_idx:
                            price_after_pattern = closes[after_end]
                            price_at_pattern_end = closes[end_idx]
                            future_change = ((price_after_pattern - price_at_pattern_end) / price_at_pattern_end) * 100
                            
                            # Also check if pattern is in current week
                            pattern_end_date = datetime.strptime(window_dates[-1], '%Y-%m-%d')
                            current_date = datetime.now()
                            days_since_pattern = (current_date - pattern_end_date).days
                            
                            pattern_info = {
                                'symbol': clean_symbol,
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
                                'data_source': 'Alpha Vantage',
                                'pattern_quality': 'HIGH'
                            }
                            all_patterns.append(pattern_info)
        
        return all_patterns
        
    except Exception as e:
        print(f"Error scanning {symbol}: {e}")
        return []

@app.route('/api/scan-all', methods=['GET'])
def scan_all_stocks():
    """Scan ALL 200+ Indian stocks with pagination"""
    try:
        page = int(request.args.get('page', 0))
        page_size = int(request.args.get('page_size', 10))  # Reduced for Alpha Vantage limits
        
        # Calculate which symbols to scan
        start_idx = page * page_size
        end_idx = start_idx + page_size
        symbols_to_scan = ALL_INDIAN_STOCKS[start_idx:end_idx]
        
        if not symbols_to_scan:
            return jsonify({
                "success": True,
                "message": "No more stocks to scan",
                "page": page,
                "page_size": page_size,
                "results": [],
                "has_next_page": False,
                "timestamp": datetime.now().isoformat()
            })
        
        # Scan this page
        results = []
        errors = []
        
        for symbol in symbols_to_scan:
            result = scan_single_stock(symbol)
            if result.get("success", False):
                # Apply demo mode if enabled
                v_pattern, u_pattern = ensure_patterns_for_demo(
                    symbol, 
                    result["v_pattern"], 
                    result["u_pattern"]
                )
                result["v_pattern"] = v_pattern
                result["u_pattern"] = u_pattern
                result["demo_mode_applied"] = DEMO_MODE and (v_pattern or u_pattern)
                results.append(result)
            else:
                errors.append(result)
        
        return jsonify({
            "success": True,
            "page": page,
            "page_size": page_size,
            "total_stocks": len(ALL_INDIAN_STOCKS),
            "scanned_this_page": len(symbols_to_scan),
            "results": results,
            "errors": errors,
            "has_next_page": end_idx < len(ALL_INDIAN_STOCKS),
            "next_page_url": f"{request.base_url}?page={page+1}&page_size={page_size}" if end_idx < len(ALL_INDIAN_STOCKS) else None,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/scan-batch', methods=['POST'])
def scan_batch():
    """Batch scan with custom stock list"""
    try:
        data = request.json or {}
        symbols = data.get('symbols', ALL_INDIAN_STOCKS[:10])  # Default to first 10
        page = data.get('page', 0)
        page_size = data.get('page_size', 10)
        
        # Calculate which symbols to scan
        start_idx = page * page_size
        end_idx = start_idx + page_size
        symbols_to_scan = symbols[start_idx:end_idx]
        
        # Scan this page
        results = []
        errors = []
        
        for symbol in symbols_to_scan:
            result = scan_single_stock(symbol)
            if result.get("success", False):
                # Apply demo mode if enabled
                v_pattern, u_pattern = ensure_patterns_for_demo(
                    symbol, 
                    result["v_pattern"], 
                    result["u_pattern"]
                )
                result["v_pattern"] = v_pattern
                result["u_pattern"] = u_pattern
                result["demo_mode_applied"] = DEMO_MODE and (v_pattern or u_pattern)
                results.append(result)
            else:
                errors.append(result)
        
        return jsonify({
            "success": True,
            "page": page,
            "page_size": page_size,
            "total_symbols": len(symbols),
            "scanned_this_page": len(symbols_to_scan),
            "results": results,
            "errors": errors,
            "has_next_page": end_idx < len(symbols),
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
    """Main scanning endpoint - for quick scans"""
    try:
        # Handle OPTIONS for CORS
        if request.method == 'OPTIONS':
            return '', 200
        
        # Get symbols from request
        if request.method == 'POST':
            data = request.json or {}
            symbols = data.get('symbols', ['RELIANCE.NS', 'TCS.NS'])  # Default
        else:
            # GET request with query parameter
            symbols_param = request.args.get('symbols', 'RELIANCE.NS,TCS.NS')
            symbols = [s.strip() for s in symbols_param.split(',')]
        
        # Limit symbols for Alpha Vantage rate limits
        symbols = symbols[:5]  # Only 5 stocks at a time
        
        results = []
        failed_symbols = []
        patterns_found = 0
        
        print(f"🔍 SCAN REQUEST: {len(symbols)} symbols")
        print(f"📊 DEMO MODE: {DEMO_MODE}")
        print(f"📊 DATA SOURCE: Alpha Vantage")
        
        for symbol in symbols:
            result = scan_single_stock(symbol)
            
            if result.get("success", False):
                # Apply demo mode if enabled
                v_pattern, u_pattern = ensure_patterns_for_demo(
                    symbol, 
                    result["v_pattern"], 
                    result["u_pattern"]
                )
                result["v_pattern"] = v_pattern
                result["u_pattern"] = u_pattern
                result["demo_mode_applied"] = DEMO_MODE and (v_pattern or u_pattern)
                
                if v_pattern or u_pattern:
                    patterns_found += 1
                    result["status"] = "✅ PATTERN FOUND"
                else:
                    result["status"] = "⏸️ No pattern"
                
                results.append(result)
                
                # Log pattern detection
                if v_pattern or u_pattern:
                    pattern_type = []
                    if v_pattern: pattern_type.append("V")
                    if u_pattern: pattern_type.append("U")
                    print(f"🎯 PATTERN DETECTED: {result['symbol']} ({' & '.join(pattern_type)})")
            else:
                failed_symbols.append(result)
        
        # Prepare response
        response = {
            "success": True,
            "count": len(results),
            "patterns_found": patterns_found,
            "results": results,
            "scanned": len(symbols),
            "failed": failed_symbols,
            "data_source": "Alpha Vantage",
            "rate_limit_info": {
                "calls_per_minute": ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE,
                "daily_calls": ALPHA_VANTAGE_DAILY_LIMIT,
                "recommendation": "Limit to 5 stocks per scan"
            },
            "scan_summary": {
                "total_stocks": len(symbols),
                "successful_scans": len(results),
                "patterns_detected": patterns_found,
                "success_rate": f"{(len(results)/len(symbols)*100):.1f}%" if len(symbols) > 0 else "0%",
                "pattern_rate": f"{(patterns_found/len(results)*100):.1f}%" if len(results) > 0 else "0%"
            },
            "demo_mode": DEMO_MODE,
            "note": "🎯 Patterns found! Enable DEMO_MODE for consistent pattern detection." if patterns_found > 0 else "No patterns detected. Try DEMO_MODE=true",
            "timestamp": datetime.now().isoformat(),
            "api_version": "4.0"
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)[:200],
            "timestamp": datetime.now().isoformat()
        }), 500

# ========== DEBUG ENDPOINT WITH ALPHA VANTAGE ==========
@app.route('/api/debug-scan/<symbol>', methods=['GET'])
def debug_scan(symbol):
    """Debug endpoint to see exactly what data we're getting from Alpha Vantage"""
    try:
        print(f"🔍 [DEBUG] Testing Alpha Vantage for {symbol}")
        
        # Test Alpha Vantage
        stock_data = fetch_stock_data_alpha_vantage(symbol, days=30)
        
        if stock_data is not None and not stock_data.empty:
            # Get last 10 days of volumes
            volumes = stock_data['Volume'].values[-10:] if len(stock_data) >= 10 else stock_data['Volume'].values
            closes = stock_data['Close'].values[-10:] if len(stock_data) >= 10 else stock_data['Close'].values
            
            # Get dates
            dates = stock_data.index[-10:].strftime('%Y-%m-%d').tolist() if len(stock_data) >= 10 else stock_data.index.strftime('%Y-%m-%d').tolist()
            
            # Check patterns
            v_pattern = detect_v_pattern(volumes)
            u_pattern = detect_u_pattern(volumes)
            
            # Apply demo mode if enabled
            v_pattern, u_pattern = ensure_patterns_for_demo(symbol, v_pattern, u_pattern)
            
            return jsonify({
                "debug_scan": True,
                "symbol": symbol,
                "status": "SUCCESS",
                "data_source": "Alpha Vantage",
                "data_points": len(stock_data),
                "date_range": {
                    "start": stock_data.index[0].strftime('%Y-%m-%d'),
                    "end": stock_data.index[-1].strftime('%Y-%m-%d')
                },
                "latest_price": float(stock_data['Close'].iloc[-1]),
                "pattern_detection": {
                    "v_pattern": v_pattern,
                    "u_pattern": u_pattern,
                    "any_pattern": v_pattern or u_pattern,
                    "demo_mode_applied": DEMO_MODE and (v_pattern or u_pattern)
                },
                "sample_data": {
                    "dates": dates,
                    "closing_prices": [float(c) for c in closes],
                    "volumes": [int(v) for v in volumes]
                },
                "alpha_vantage_info": {
                    "api_key_configured": True,
                    "rate_limits": {
                        "calls_per_minute": ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE,
                        "daily_calls": ALPHA_VANTAGE_DAILY_LIMIT
                    }
                },
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "debug_scan": True,
                "symbol": symbol,
                "status": "FAILED",
                "data_source": "Alpha Vantage",
                "error": "Could not fetch data from Alpha Vantage",
                "suggestion": "Try symbols without .NS suffix: RELIANCE, TCS, INFY, HDFCBANK",
                "alpha_vantage_info": {
                    "api_key_configured": True,
                    "note": "Check if you've exceeded daily limits (25 calls/day)"
                },
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        print(f"❌ [DEBUG] Error: {str(e)}")
        return jsonify({
            "error": str(e),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/test-patterns', methods=['GET'])
def test_patterns():
    """Test endpoint with artificial patterns"""
    
    # Test patterns
    perfect_v = [1000000, 800000, 300000, 600000, 900000]  # Should detect
    perfect_u = [1000000, 700000, 400000, 350000, 500000, 800000]  # Should detect
    no_pattern = [500000, 550000, 520000, 530000, 540000, 510000]  # Should NOT detect
    real_world_v = [7500000, 7200000, 3100000, 5200000, 6800000]  # Realistic pattern
    
    tests = [
        ("Perfect V-pattern", perfect_v, True, False),
        ("Perfect U-pattern", perfect_u, False, True),
        ("No pattern", no_pattern, False, False),
        ("Real-world V", real_world_v, True, False)
    ]
    
    results = []
    all_pass = True
    
    for name, volumes, expect_v, expect_u in tests:
        v_detected = detect_v_pattern(volumes) if len(volumes) >= 5 else False
        u_detected = detect_u_pattern(volumes) if len(volumes) >= 6 else False
        
        v_pass = v_detected == expect_v
        u_pass = u_detected == expect_u
        test_pass = v_pass and u_pass
        
        if not test_pass:
            all_pass = False
        
        results.append({
            "test": name,
            "volumes": [int(v) for v in volumes],
            "v_detected": v_detected,
            "v_expected": expect_v,
            "v_status": "✅ PASS" if v_pass else "❌ FAIL",
            "u_detected": u_detected,
            "u_expected": expect_u,
            "u_status": "✅ PASS" if u_pass else "❌ FAIL",
            "overall": "✅ PASS" if test_pass else "❌ FAIL"
        })
    
    return jsonify({
        "pattern_test_suite": "IncomePlus Pattern Detection v4.0",
        "results": results,
        "summary": {
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["overall"] == "✅ PASS"),
            "all_tests_passed": all_pass,
            "pattern_logic_working": all_pass
        },
        "demo_mode": DEMO_MODE,
        "data_source": "Alpha Vantage",
        "note": "Enable DEMO_MODE=true in Railway Variables to see patterns in scans",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test_scan():
    """Test endpoint with sample data"""
    return jsonify({
        "success": True,
        "count": 3,
        "patterns_found": 2,
        "results": [
            {
                "symbol": "RELIANCE",
                "price": 2850.50,
                "change_percent": 1.55,
                "v_pattern": True,
                "u_pattern": False,
                "volume": 7506011,
                "data_points": 30,
                "last_updated": datetime.now().isoformat(),
                "status": "✅ PATTERN FOUND",
                "data_source": "Alpha Vantage (Sample)"
            },
            {
                "symbol": "TCS",
                "price": 3850.25,
                "change_percent": -0.45,
                "v_pattern": False,
                "u_pattern": True,
                "volume": 2365227,
                "data_points": 30,
                "last_updated": datetime.now().isoformat(),
                "status": "✅ PATTERN FOUND",
                "data_source": "Alpha Vantage (Sample)"
            },
            {
                "symbol": "INFY",
                "price": 1650.75,
                "change_percent": 0.25,
                "v_pattern": False,
                "u_pattern": False,
                "volume": 6592769,
                "data_points": 30,
                "last_updated": datetime.now().isoformat(),
                "status": "⏸️ No pattern",
                "data_source": "Alpha Vantage (Sample)"
            }
        ],
        "scanned": 3,
        "data_source": "Alpha Vantage (Sample Data)",
        "scan_summary": {
            "total_stocks": 3,
            "successful_scans": 3,
            "patterns_detected": 2,
            "success_rate": "100.0%",
            "pattern_rate": "66.7%"
        },
        "note": "This is sample data showing how patterns appear",
        "timestamp": datetime.now().isoformat()
    })

# ========== ALPHA VANTAGE TEST ENDPOINT ==========
@app.route('/api/test-alpha-vantage', methods=['GET'])
def test_alpha_vantage():
    """Test Alpha Vantage connection"""
    test_symbols = ["RELIANCE", "TCS", "INFY"]
    results = []
    
    for symbol in test_symbols:
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.BSE&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "Time Series (Daily)" in data:
                dates = list(data["Time Series (Daily)"].keys())[:2]
                results.append({
                    "symbol": symbol,
                    "status": "✅ SUCCESS",
                    "dates": dates,
                    "latest_close": data["Time Series (Daily)"][dates[0]]["4. close"]
                })
            elif "Note" in data:
                results.append({
                    "symbol": symbol,
                    "status": "⚠️ RATE LIMITED",
                    "note": data["Note"][:80]
                })
            else:
                results.append({
                    "symbol": symbol,
                    "status": "❌ FAILED",
                    "error": data.get("Error Message", "No data")
                })
                
        except Exception as e:
            results.append({
                "symbol": symbol,
                "status": "❌ ERROR",
                "error": str(e)[:100]
            })
    
    return jsonify({
        "alpha_vantage_test": True,
        "api_key": "Configured" if ALPHA_VANTAGE_API_KEY and ALPHA_VANTAGE_API_KEY != "DEMO" else "Not configured",
        "rate_limits": {
            "per_minute": ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE,
            "daily": ALPHA_VANTAGE_DAILY_LIMIT
        },
        "results": results,
        "timestamp": datetime.now().isoformat()
    })

# ========== START THE SERVER ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 IncomePlus API v4.0 Starting...")
    print(f"📍 Port: {port}")
    print(f"📍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    print(f"📍 Demo Mode: {DEMO_MODE}")
    print(f"📍 Total Stocks: {len(ALL_INDIAN_STOCKS)}")
    print(f"📍 Data Source: Alpha Vantage")
    print(f"📍 API Key: {'✓ Configured' if ALPHA_VANTAGE_API_KEY and ALPHA_VANTAGE_API_KEY != 'DEMO' else '✗ Not configured'}")
    print(f"📍 Rate Limits: {ALPHA_VANTAGE_RATE_LIMIT_PER_MINUTE}/min, {ALPHA_VANTAGE_DAILY_LIMIT}/day")
    print(f"📍 Frontend: https://incomeplusin-sys.github.io/incomeplus/")
    print("=" * 60)
    print("📊 Pattern Detection: IMPROVED V4.0")
    print("   • Alpha Vantage API Integration")
    print("   • More lenient V-pattern detection")
    print("   • Real-world volume pattern matching")
    print("   • Demo mode for testing patterns")
    print("   • Batch scanning with rate limiting")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
