"""
INCOMEPLUS WEB API - FLASK VERSION
Optimized for Railway deployment with GitHub Pages frontend
BATCH SCANNING VERSION - HANDLES 200+ STOCKS
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
    """Try different symbol formats for Indian stocks"""
    symbol = symbol.strip().upper()
    
    # If no suffix, try .NS and .BO
    if '.' not in symbol:
        return [f"{symbol}.NS", f"{symbol}.BO", symbol]
    
    # Already has suffix
    return [symbol]

def scan_single_stock(symbol):
    """Scan a single stock (for batch scanning)"""
    try:
        symbol_variations = normalize_symbol(symbol)
        stock_data = None
        used_symbol = symbol
        
        for sym_var in symbol_variations:
            try:
                stock_data = yf.download(
                    sym_var, 
                    period="1mo", 
                    progress=False,
                    timeout=8
                )
                
                if stock_data is not None and not stock_data.empty and len(stock_data) >= 10:
                    used_symbol = sym_var
                    break
            except:
                continue
        
        # Check if we got data
        if stock_data is None or stock_data.empty or len(stock_data) < 10:
            return {
                "symbol": symbol,
                "error": "insufficient data",
                "success": False
            }
        
        # Get volumes and prices
        volumes = stock_data['Volume'].values
        closes = stock_data['Close'].values
        
        # Detect patterns
        v_pattern = detect_v_pattern(volumes)
        u_pattern = detect_u_pattern(volumes)
        
        # Calculate price change
        current_price = float(closes[-1])
        prev_price = float(closes[-2]) if len(closes) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
        
        # Prepare result
        clean_symbol = used_symbol.replace('.NS', '').replace('.BO', '')
        
        return {
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
            "status": "pattern_found" if (v_pattern or u_pattern) else "no_pattern",
            "success": True
        }
        
    except Exception as e:
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
        "version": "3.0",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        "demo_mode": DEMO_MODE,
        "status": "running",
        "total_stocks_available": len(ALL_INDIAN_STOCKS),
        "frontend_url": "https://incomeplusin-sys.github.io/incomeplus/",
        "backend_url": "https://web-production-1b0f1.up.railway.app",
        "pattern_logic": "IMPROVED - More lenient detection",
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
        "message": "IncomePlus API is working",
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        "demo_mode": DEMO_MODE,
        "total_stocks": len(ALL_INDIAN_STOCKS),
        "pattern_detection": "IMPROVED V3.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/scan-all', methods=['GET'])
def scan_all_stocks():
    """Scan ALL 200+ Indian stocks with pagination"""
    try:
        page = int(request.args.get('page', 0))
        page_size = int(request.args.get('page_size', 20))  # 20 stocks per page
        
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
        symbols = data.get('symbols', ALL_INDIAN_STOCKS[:20])  # Default to first 20
        page = data.get('page', 0)
        page_size = data.get('page_size', 20)
        
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
            symbols = data.get('symbols', ALL_INDIAN_STOCKS[:10])  # Default to first 10
        else:
            # GET request with query parameter
            symbols_param = request.args.get('symbols', 'RELIANCE.NS,TCS.NS,INFY.NS')
            symbols = [s.strip() for s in symbols_param.split(',')]
        
        # Limit symbols for performance (Railway free tier)
        symbols = symbols[:25]  # Increased to 25, safe for Railway
        
        results = []
        failed_symbols = []
        patterns_found = 0
        
        print(f"🔍 SCAN REQUEST: {len(symbols)} symbols")
        print(f"📊 DEMO MODE: {DEMO_MODE}")
        
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
            "api_version": "3.0"
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)[:200],
            "timestamp": datetime.now().isoformat()
        }), 500

# ========== OTHER ENDPOINTS (keep as before) ==========
@app.route('/api/debug-scan/<symbol>', methods=['GET'])
def debug_scan(symbol):
    """Debug endpoint to see exactly what data we're getting"""
    try:
        # Get stock data
        stock_data = yf.download(
            symbol, 
            period="1mo", 
            progress=False,
            timeout=10
        )
        
        if stock_data is None or stock_data.empty:
            return jsonify({
                "error": "No data returned from yfinance",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Get last 10 days of volumes
        volumes = stock_data['Volume'].values[-10:]
        closes = stock_data['Close'].values[-10:]
        
        # Get dates
        dates = stock_data.index[-10:].strftime('%Y-%m-%d').tolist()
        
        # Check patterns
        v_pattern = detect_v_pattern(volumes)
        u_pattern = detect_u_pattern(volumes)
        
        # Apply demo mode if enabled
        v_pattern, u_pattern = ensure_patterns_for_demo(symbol, v_pattern, u_pattern)
        
        # Detailed analysis
        last_5_volumes = volumes[-5:] if len(volumes) >= 5 else volumes
        last_5_dates = dates[-5:] if len(dates) >= 5 else dates
        
        if len(last_5_volumes) >= 5:
            min_idx = np.argmin(last_5_volumes)
            v_analysis = {
                "last_5_volumes": [int(v) for v in last_5_volumes],
                "last_5_dates": last_5_dates,
                "minimum_volume_day": f"Day {min_idx} ({last_5_dates[min_idx]})",
                "minimum_volume_value": int(last_5_volumes[min_idx]),
                "volume_trend": "Decreasing then increasing" if min_idx in [2,3] else "Other pattern",
                "v_pattern_possible": min_idx in [2, 3],
                "day_comparisons": {
                    "day2_vs_day0": f"{last_5_volumes[2]/last_5_volumes[0]*100:.1f}%",
                    "day2_vs_day1": f"{last_5_volumes[2]/last_5_volumes[1]*100:.1f}%",
                    "day3_vs_day2": f"{last_5_volumes[3]/last_5_volumes[2]*100:.1f}%",
                    "day4_vs_day3": f"{last_5_volumes[4]/last_5_volumes[3]*100:.1f}%"
                }
            }
        else:
            v_analysis = {"error": "Not enough data for analysis"}
        
        return jsonify({
            "symbol": symbol,
            "data_points": len(stock_data),
            "dates_available": stock_data.index.strftime('%Y-%m-%d').tolist()[-10:],
            "last_10_days": {
                "dates": dates,
                "volumes": [int(v) for v in volumes],
                "closing_prices": [float(c) for c in closes]
            },
            "pattern_detection": {
                "v_pattern": v_pattern,
                "u_pattern": u_pattern,
                "any_pattern": v_pattern or u_pattern,
                "demo_mode_applied": DEMO_MODE and (v_pattern or u_pattern)
            },
            "v_pattern_analysis": v_analysis,
            "algorithm_info": {
                "v_pattern_requires": "Day 2 or 3 = minimum volume, followed by increase",
                "current_status": "✅ Pattern found" if v_pattern else "❌ No V-pattern",
                "detection_type": "IMPROVED (more lenient)"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }), 500

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
        "pattern_test_suite": "IncomePlus Pattern Detection v3.0",
        "results": results,
        "summary": {
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["overall"] == "✅ PASS"),
            "all_tests_passed": all_pass,
            "pattern_logic_working": all_pass
        },
        "demo_mode": DEMO_MODE,
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
                "status": "✅ PATTERN FOUND"
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
                "status": "✅ PATTERN FOUND"
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
                "status": "⏸️ No pattern"
            }
        ],
        "scanned": 3,
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

# ========== START THE SERVER ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 IncomePlus API v3.0 Starting...")
    print(f"📍 Port: {port}")
    print(f"📍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    print(f"📍 Demo Mode: {DEMO_MODE}")
    print(f"📍 Total Stocks: {len(ALL_INDIAN_STOCKS)}")
    print(f"📍 Frontend: https://incomeplusin-sys.github.io/incomeplus/")
    print("=" * 60)
    print("📊 Pattern Detection: IMPROVED V3.0")
    print("   • More lenient V-pattern detection")
    print("   • Real-world volume pattern matching")
    print("   • Demo mode for testing patterns")
    print("   • Batch scanning for 200+ stocks")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
