"""
INCOMEPLUS YFINANCE SCANNER - ROBUST VERSION
Uses yfinance for Indian stock data with proper error handling
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# ========== CONFIGURATION ==========
# Use .NS for NSE (National Stock Exchange) symbols
INDIAN_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ASIANPAINT.NS"
]

# ========== DATA FETCHING WITH ERROR HANDLING ==========
def fetch_stock_data_yf(symbol, days=60):
    """Fetch stock data with multiple retry attempts"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            print(f"  📡 {symbol}... (Attempt {attempt + 1}/{max_retries})", end=" ")
            
            # Download data
            stock = yf.download(
                symbol,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False,
                timeout=10
            )
            
            # Check if data is valid
            if stock.empty:
                print("❌ No data")
                time.sleep(2)  # Wait before retry
                continue
            
            # Ensure we have required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in stock.columns for col in required_cols):
                print("❌ Missing columns")
                continue
            
            # Check if we have enough data points
            if len(stock) < 20:
                print(f"❌ Only {len(stock)} days")
                continue
            
            print(f"✅ {len(stock)} days, Vol: {stock['Volume'].iloc[-1]:,}")
            return stock
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            time.sleep(3)  # Longer wait on error
    
    print(f"  ⚠️  Failed after {max_retries} attempts")
    return None

# ========== PATTERN DETECTION (YOUR ORIGINAL LOGIC) ==========
def detect_v_pattern(volumes):
    """Detect 5-candle V pattern"""
    if len(volumes) < 5:
        return False
    
    last_5 = volumes[-5:]
    
    conditions = [
        last_5[2] == min(last_5),  # Candle 3 is lowest
        last_5[3] > last_5[2],     # Candle 4 > Candle 3
        last_5[4] > last_5[3],     # Candle 5 > Candle 4
        last_5[2] < last_5[0],     # Candle 3 < Candle 1
        last_5[2] < last_5[1]      # Candle 3 < Candle 2
    ]
    
    return all(conditions)

def detect_u_pattern(volumes):
    """Detect 6-candle U pattern"""
    if len(volumes) < 6:
        return False
    
    last_6 = volumes[-6:]
    
    conditions = [
        last_6[2] < last_6[1],     # Candle 3 < Candle 2
        last_6[3] < last_6[2],     # Candle 4 < Candle 3
        last_6[4] > last_6[3],     # Candle 5 > Candle 4
        last_6[5] > last_6[4],     # Candle 6 > Candle 5
        last_6[3] < last_6[0],     # Lowest < First
        last_6[3] < last_6[1]      # Lowest < Second
    ]
    
    return all(conditions)

# ========== MAIN SCANNER FUNCTION ==========
def scan_with_yfinance():
    """Main scanning function using yfinance"""
    print("\n" + "="*70)
    print("🎯 INCOMEPLUS VOLUME PATTERN SCANNER (YFINANCE)")
    print("="*70)
    print(f"📊 Data Source: Yahoo Finance (yfinance)")
    print(f"📈 Scanning {len(INDIAN_STOCKS)} Indian stocks (.NS)")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    for symbol in INDIAN_STOCKS:
        try:
            # Fetch stock data
            stock_data = fetch_stock_data_yf(symbol)
            if stock_data is None:
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
                    'Symbol': symbol.replace('.NS', ''),
                    'Price': f"₹{current_price:.2f}",
                    'Change': f"{price_change:+.2f}%",
                    'V_Pattern': '✅' if v_pattern else '❌',
                    'U_Pattern': '✅' if u_pattern else '❌',
                    'Volume': f"{volumes[-1]:,}",
                    'Days': len(stock_data)
                }
                
                results.append(result)
                print(f"    🎯 PATTERN FOUND!")
            
            # Small delay between stocks
            time.sleep(1)
            
        except Exception as e:
            print(f"    ⚠️  Skipping {symbol}: {str(e)[:50]}")
            continue
    
    return results

# ========== REPORT GENERATION ==========
def generate_csv_report(results):
    """Generate CSV report file"""
    if not results:
        print("\n❌ No patterns found in this scan.")
        print("💡 This is normal - patterns are rare. Try different stocks or timeframes.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    filename = f"IncomePlus_Scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    
    # Display results
    print("\n" + "="*70)
    print("📊 SCAN RESULTS SUMMARY")
    print("="*70)
    print(f"🎯 Total patterns found: {len(results)}")
    print(f"💾 Report saved as: {filename}")
    
    print("\n📈 DETAILED RESULTS:")
    for idx, result in enumerate(results, 1):
        print(f"\n  {idx}. {result['Symbol']:15}")
        print(f"     Price:  {result['Price']}")
        print(f"     Change: {result['Change']}")
        print(f"     V Pattern: {result['V_Pattern']}  |  U Pattern: {result['U_Pattern']}")
        print(f"     Volume: {result['Volume']}")
    
    return filename

# ========== TEST YFINANCE CONNECTION ==========
        if test_data.empty:
            print("❌ Connection failed: No data returned")
            print("💡 Possible solutions:")
            print("   1. Check your internet connection")
            print("   2. Try again in 5 minutes (Yahoo might be blocking)")
            print("   3. Use VPN if in India (sometimes helps)")
            return False
        else:
            print(f"✅ Connection SUCCESSFUL!")
            print(f"   Symbol: {test_symbol}")
            # FIXED LINE: Extract the last single price value correctly
            last_price = test_data['Close'].iloc[-1] 
            print(f"   Price: ₹{last_price:.2f}")
            # FIXED LINE: Extract the last single volume value correctly
            last_volume = test_data['Volume'].iloc[-1] 
            print(f"   Volume: {last_volume:,.0f}")
            print(f"   Date: {test_data.index[-1].date()}")
            return True

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    print("🚀 Starting IncomePlus Scanner with yfinance...")
    
    # First, test connection
    connection_ok = test_yfinance_connection()
    
    if not connection_ok:
        print("\n⚠️  Cannot proceed without yfinance connection.")
        print("💡 Try these fixes:")
        print("   1. Restart your computer")
        print("   2. Disable antivirus/firewall temporarily")
        print("   3. Use different network")
        print("   4. Wait 30 minutes and try again")
        exit(1)
    
    # Run the scanner
    print("\n" + "="*70)
    print("🔄 STARTING MAIN SCAN...")
    
    results = scan_with_yfinance()
    report_file = generate_csv_report(results)
    
    # Final message
    print("\n" + "="*70)
    if report_file:
        print(f"✅ Scan completed successfully!")
        print(f"📁 CSV file: {report_file}")
        print("\n💡 NEXT STEP: Convert this scanner to a web API!")
    else:
        print(f"⚠️  Scan completed with no patterns found.")
        print("\n💡 This is OK for testing! Your scanner logic is working.")
        print("   Next: We'll turn this into a web API anyway.")
    
    print("="*70)