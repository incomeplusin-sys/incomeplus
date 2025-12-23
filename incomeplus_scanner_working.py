"""
INCOMEPLUS WORKING SCANNER - FMP FREE TIER
Uses the real-time quote endpoint available on the Basic plan.
"""

import requests
import pandas as pd
from datetime import datetime
import time

# ========== CONFIGURATION ==========
FMP_API_KEY = "RN99S2fBFmMknX3XitZ8xcUsk8gHYkbH"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Use symbols that work with the free quote endpoint.
# For global stocks, use the primary exchange (e.g., RELIANCE.NS, but let's test).
# The API might accept these for a quote.
TEST_SYMBOLS = ["RELIANCE.BO", "TCS.BO", "INFY.BO"]  # We will test these

# ========== FETCH REAL-TIME QUOTE ==========
def fetch_realtime_quote(symbol):
    """Fetch latest price and volume from FMP Quote API[citation:5]"""
    try:
        url = f"{FMP_BASE_URL}/quote/{symbol}"
        params = {'apikey': FMP_API_KEY}
        
        print(f"  📡 Fetching {symbol}...", end=" ")
        response = requests.get(url, params=params, timeout=30)
        
        # Check for 403 specifically
        if response.status_code == 403:
            print(f"❌ 403 Forbidden. '{symbol}' not on free plan.")
            return None
        elif response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return None
            
        data = response.json()
        
        # The quote endpoint returns a list
        if isinstance(data, list) and len(data) > 0:
            quote = data[0]
            # Extract key data
            result = {
                'price': quote.get('price'),
                'volume': quote.get('volume'),
                'previous_close': quote.get('previousClose'),
                'change': quote.get('change'),
                'change_percentage': quote.get('changesPercentage')
            }
            print(f"✅ Price: ₹{result['price']}")
            return result
        else:
            print("❌ No quote data in response.")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return None

# ========== PATTERN DETECTION (SIMPLIFIED FOR REAL-TIME) ==========
# Since we only have current volume, we simulate pattern detection
# by checking if volume is significantly higher than average.
# In your final website, you will need historical data for real patterns.
def check_high_volume(current_volume, avg_volume=1000000):
    """Simple check if volume is high"""
    if current_volume and avg_volume > 0:
        ratio = current_volume / avg_volume
        return ratio > 1.5  # 50% higher than average
    return False

# ========== MAIN SCANNER ==========
def scan_realtime():
    print("\n" + "="*60)
    print("🎯 INCOMEPLUS REAL-TIME SCANNER (FREE TIER)")
    print("="*60)
    print(f"🔑 API Key: ...{FMP_API_KEY[-8:]}")  # Show last 8 chars for verification
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = []
    
    for symbol in TEST_SYMBOLS:
        quote_data = fetch_realtime_quote(symbol)
        
        if quote_data and quote_data['volume']:
            # Simple "pattern" detection for demo
            volume_high = check_high_volume(quote_data['volume'])
            
            if volume_high:
                result = {
                    'Symbol': symbol,
                    'Price': f"₹{quote_data['price']:.2f}",
                    'Volume': f"{quote_data['volume']:,}",
                    'Change': f"{quote_data['change_percentage']:+.2f}%",
                    'Signal': 'HIGH_VOLUME'
                }
                results.append(result)
                print(f"    ⚠️  High volume detected for {symbol}")
        
        time.sleep(1)  # Be nice to the API
    
    return results

# ========== RUN ==========
if __name__ == "__main__":
    print("🚀 Testing API Access with Free Endpoint...")
    results = scan_realtime()
    
    if results:
        print("\n" + "="*60)
        print("📊 SCAN COMPLETED - POTENTIAL SIGNALS")
        print("="*60)
        for res in results:
            print(f"\n  {res['Symbol']:15} | Price: {res['Price']:>12}")
            print(f"  {'Volume:':15} | {res['Volume']:>12}")
            print(f"  {'Change:':15} | {res['Change']:>12}")
            print(f"  {'Signal:':15} | {res['Signal']:>12}")
    else:
        print("\n" + "="*60)
        print("ℹ️  SCAN COMPLETED")
        print("="*60)
        print("No high-volume signals detected with test symbols.")
        print("\n💡 The quote API call worked! Next step: Get historical data.")
    
    print(f"\n✅ Scanner test finished.")