"""
INCOMEPLUS MASTER SCANNER - LATEST INTEGRATED VERSION
---------------------------------------------------
- DATA SOURCE: Angel One SmartApi (Integrated)
- SCANNERS: U-Pattern, V-Pattern, Pyramid Pattern
- FEATURES: VMA (Volume Moving Average) Validation & Price Trend Analysis
"""

import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from SmartApi import SmartConnect
import pyotp
import warnings

warnings.filterwarnings('ignore')

# ========== 1. CONFIGURATION & AUTHENTICATION ==========
API_KEY = "YOUR_ANGEL_API_KEY"
CLIENT_CODE = "YOUR_CLIENT_CODE"
PASSWORD = "YOUR_PASSWORD"
TOTP_SECRET = "YOUR_TOTP_SECRET"

class AngelOneClient:
    def __init__(self):
        self.obj = SmartConnect(api_key=API_KEY)
        self.token_data = self.obj.generateSession(CLIENT_CODE, PASSWORD, pyotp.TOTP(TOTP_SECRET).now())
        self.feed_token = self.obj.getfeedToken()
        
    def fetch_historical_data(self, symbol_token, symbol_name, interval="ONE_DAY", days=60):
        """Fetch data using Angel One SmartApi"""
        try:
            to_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
            
            data = self.obj.getCandleData({
                "exchange": "NSE",
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            })
            
            if data['status'] and data['data']:
                df = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df['volume'] = pd.to_numeric(df['volume'])
                df['close'] = pd.to_numeric(df['close'])
                return df
            return None
        except Exception as e:
            print(f"Error fetching {symbol_name}: {e}")
            return None

# ========== 2. THE THREE CORE SCANNERS ==========

def detect_u_pattern(volumes, min_len=6):
    """Detect U-Pattern: Strictly Descending then Strictly Ascending"""
    if len(volumes) < min_len: return False
    mid = len(volumes) // 2
    left = volumes[:mid]
    right = volumes[mid:]
    # Check if left is descending and right is ascending
    is_desc = all(x > y for x, y in zip(left, left[1:]))
    is_asc = all(x < y for x, y in zip(right, right[1:]))
    return is_desc and is_asc

def detect_v_pattern(volumes):
    """Detect 5-Candle V-Pattern: High -> Low -> Lowest -> Low -> High"""
    if len(volumes) < 5: return False
    v = volumes[-5:]
    cond = (v[2] == min(v) and v[3] > v[2] and v[4] > v[3] and v[2] < v[0] and v[2] < v[1])
    return cond

def detect_pyramid_pattern(volumes):
    """Detect Pyramid: Increasing then Decreasing volume"""
    if len(volumes) < 5: return False
    mid = len(volumes) // 2
    left = volumes[:mid+1]
    right = volumes[mid:]
    is_pyramid_asc = all(x < y for x, y in zip(left, left[1:]))
    is_pyramid_desc = all(x > y for x, y in zip(right, right[1:]))
    return is_pyramid_asc and is_pyramid_desc

# ========== 3. MAIN SCANNING ENGINE ==========

def run_integrated_scan(stock_list):
    client = AngelOneClient()
    results = []
    
    print(f"🚀 Starting Master Scan on {len(stock_list)} stocks...")
    
    for stock in stock_list:
        # Note: In real use, you'd map 'RELIANCE' to its token '3045'
        df = client.fetch_historical_data(stock['token'], stock['symbol'])
        
        if df is not None:
            volumes = df['volume'].values
            prices = df['close'].values
            vma = df['volume'].rolling(window=20).mean().iloc[-1]
            
            # Run all pattern checks
            found_u = detect_u_pattern(volumes[-6:])
            found_v = detect_v_pattern(volumes[-5:])
            found_p = detect_pyramid_pattern(volumes[-5:])
            
            if found_u or found_v or found_p:
                pattern_type = "U-Pattern" if found_u else ("V-Pattern" if found_v else "Pyramid")
                
                results.append({
                    "Symbol": stock['symbol'],
                    "Pattern": pattern_type,
                    "Price": prices[-1],
                    "Volume": volumes[-1],
                    "VMA_Status": "Above VMA" if volumes[-1] > vma else "Below VMA",
                    "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                print(f"🎯 Pattern Found: {stock['symbol']} ({pattern_type})")
        
        time.sleep(0.5) # Respect Angel One rate limits
    
    return results

# ========== 4. ENTRY POINT ==========
if __name__ == "__main__":
    # Example stock list with Angel Tokens
    sample_stocks = [
        {'symbol': 'RELIANCE', 'token': '3045'},
        {'symbol': 'SBIN', 'token': '3045'}, # Replace with actual tokens
    ]
    
    final_report = run_integrated_scan(sample_stocks)
    pd.DataFrame(final_report).to_csv("IncomePlus_Master_Scan.csv", index=False)
    print("✅ Scan Complete. Results saved to CSV.")
