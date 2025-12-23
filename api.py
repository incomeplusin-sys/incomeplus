"""
INCOMEPLUS WEB API - FLASK VERSION
Turn your scanner into a web service
"""

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
CORS(app)  # Allow frontend to access this API

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

# ========== API ENDPOINTS ==========
@app.route('/')
def home():
    return jsonify({
        "service": "IncomePlus Stock Scanner API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/": "This information",
            "/api/health": "Health check",
            "/api/scan": "Scan stocks (POST with JSON or GET with ?symbols=)"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "IncomePlus API is working",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/scan', methods=['GET', 'POST'])
def scan_stocks():
    """Main scanning endpoint"""
    try:
        # Get symbols from request
        if request.method == 'POST':
            data = request.json
            if data and 'symbols' in data:
                symbols = data['symbols']
            else:
                symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
        else:
            # GET request with query parameter
            symbols_param = request.args.get('symbols', "RELIANCE.NS,TCS.NS,INFY.NS")
            symbols = symbols_param.split(',')
        
        # Limit to 5 symbols for performance
        symbols = symbols[:5]
        
        results = []
        
        for symbol in symbols:
            try:
                # Fetch stock data
                stock_data = yf.download(symbol, period="1mo", progress=False)
                
                if stock_data is None or stock_data.empty or len(stock_data) < 10:
                    continue
                
                # Get volumes
                volumes = stock_data['Volume'].values
                
                # Detect patterns
                v_pattern = detect_v_pattern(volumes)
                u_pattern = detect_u_pattern(volumes)
                
                if v_pattern or u_pattern:
                    # Get price data
                    current_price = float(stock_data['Close'].iloc[-1])
                    prev_price = float(stock_data['Close'].iloc[-2])
                    price_change = ((current_price - prev_price) / prev_price) * 100
                    
                    result = {
                        "symbol": symbol.replace('.NS', ''),
                        "price": current_price,
                        "change_percent": round(price_change, 2),
                        "v_pattern": v_pattern,
                        "u_pattern": u_pattern,
                        "volume": int(volumes[-1]),
                        "data_points": len(stock_data),
                        "last_updated": datetime.now().isoformat()
                    }
                    results.append(result)
                    
            except Exception as e:
                # Skip this stock if error
                continue
        
        return jsonify({
            "success": True,
            "count": len(results),
            "results": results,
            "scanned": len(symbols),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/test', methods=['GET'])
def test_scan():
    """Test endpoint with sample data"""
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
                "last_updated": datetime.now().isoformat()
            },
            {
                "symbol": "TCS",
                "price": 3850.25,
                "change_percent": -0.75,
                "v_pattern": False,
                "u_pattern": True,
                "volume": 2365227,
                "data_points": 30,
                "last_updated": datetime.now().isoformat()
            }
        ],
        "scanned": 3,
        "timestamp": datetime.now().isoformat()
    })

# ========== START THE SERVER ==========
if __name__ == '__main__':
    print("🚀 IncomePlus API Starting...")
    print("📍 Local URL: http://localhost:5000")
    print("📍 Health Check: http://localhost:5000/api/health")
    print("📍 Test Scan: http://localhost:5000/api/test")
    print("📍 Real Scan: http://localhost:5000/api/scan?symbols=RELIANCE.NS,TCS.NS")
    print("=" * 50)
    app.run(debug=True, port=5000)