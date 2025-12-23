"""
INCOMEPLUS SCANNER - FMP VERSION
Working scanner with Financial Modeling Prep API
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# ========== CONFIGURATION ==========
FMP_API_KEY = "RN99S2fBFmMknX3XitZ8xcUsk8gHYkbH"  # Your API key
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Indian stocks recognized by FMP (use .BO for BSE)
INDIAN_STOCKS = [
    "RELIANCE.BO", "TCS.BO", "INFY.BO", "HDFCBANK.BO", "ICICIBANK.BO",
    "ITC.BO", "SBIN.BO", "BHARTIARTL.BO", "KOTAKBANK.BO", "ASIANPAINT.BO",
    "WIPRO.BO", "HINDUNILVR.BO", "MARUTI.BO", "LT.BO", "BAJFINANCE.BO"
]

# ========== DATA FETCHING ==========
def fetch_stock_data(symbol, days=90):
    """Fetch historical data from FMP"""
    try:
        # Calculate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build API URL
        url = f"{FMP_BASE_URL}/historical-price-full/{symbol}"
        params = {
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'apikey': FMP_API_KEY
        }
        
        # Make request
        print(f"  📡 Fetching {symbol}...", end=" ")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'historical' in data and data['historical']:
                # Convert to DataFrame
                df = pd.DataFrame(data['historical'])
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
                
                # Rename columns
                df.rename(columns={
                    'open': 'Open', 'high': 'High', 'low': 'Low',
                    'close': 'Close', 'volume': 'Volume'
                }, inplace=True)
                
                # Set index and select columns
                df.set_index('date', inplace=True)
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                
                print(f"✅ {len(df)} days")
                return df
            else:
                print("❌ No data")
                return None
        else:
            print(f"❌ API Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return None

# ========== PATTERN DETECTION ==========
def detect_v_pattern(volumes):
    """Detect 5-candle V pattern"""
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
    """Detect 6-candle U pattern"""
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

# ========== MAIN SCANNER ==========
def scan_stocks():
    """Main scanning function"""
    print("\n" + "="*70)
    print("🎯 INCOMEPLUS VOLUME PATTERN SCANNER")
    print("="*70)
    print(f"📊 Data Source: Financial Modeling Prep")
    print(f"📈 Scanning {len(INDIAN_STOCKS)} Indian stocks")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    for symbol in INDIAN_STOCKS:
        try:
            # Get stock data
            stock_data = fetch_stock_data(symbol)
            if stock_data is None or len(stock_data) < 11:
                continue
            
            # Get volumes
            volumes = stock_data['Volume'].values
            
            # Detect patterns
            v_pattern = detect_v_pattern(volumes)
            u_pattern = detect_u_pattern(volumes)
            
            if v_pattern or u_pattern:
                current_price = stock_data['Close'].iloc[-1]
                prev_price = stock_data['Close'].iloc[-2]
                price_change = ((current_price - prev_price) / prev_price) * 100
                
                result = {
                    'Symbol': symbol.replace('.BO', ''),
                    'Price': f"₹{current_price:.2f}",
                    'Change': f"{price_change:+.2f}%",
                    'V_Pattern': '✅' if v_pattern else '❌',
                    'U_Pattern': '✅' if u_pattern else '❌',
                    'Volume': f"{volumes[-1]:,}",
                    'Days': len(stock_data)
                }
                
                results.append(result)
                print(f"    🎯 PATTERN FOUND: {symbol.replace('.BO', '')}")
            
            # Delay to respect API limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ⚠️  Error with {symbol}: {str(e)[:50]}")
            continue
    
    return results

# ========== REPORT GENERATION ==========
def generate_report(results):
    """Generate report file"""
    if not results:
        print("\n❌ No patterns found.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    filename = f"IncomePlus_Scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    
    # Display results
    print("\n" + "="*70)
    print("📊 SCAN RESULTS")
    print("="*70)
    print(f"Total patterns found: {len(results)}")
    
    for result in results:
        print(f"\n  {result['Symbol']:15} | Price: {result['Price']:>10}")
        print(f"  {'Change:':15} | {result['Change']:>10}")
        print(f"  {'V Pattern:':15} | {result['V_Pattern']:>10}")
        print(f"  {'U Pattern:':15} | {result['U_Pattern']:>10}")
        print(f"  {'Volume:':15} | {result['Volume']:>10}")
    
    print(f"\n💾 Report saved: {filename}")
    return filename

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    print("🚀 Starting IncomePlus Scanner...")
    results = scan_stocks()
    report_file = generate_report(results)
    
    if report_file:
        print(f"\n✅ Scan completed successfully!")
        print(f"📁 File: {report_file}")
    else:
        print(f"\n⚠️  Scan completed with no patterns found.")
    
    print("\n" + "="*70)