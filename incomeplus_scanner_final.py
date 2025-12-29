"""
INCOMEPLUS YFINANCE SCANNER - FINAL WORKING VERSION
No indentation errors, proper error handling
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
"360ONE.NS","ABB.NS","APLAPOLLO.NS","AUBANK.NS","ADANIENSOL.NS","ADANIENT.NS","ADANIGREEN.NS","ADANIPORTS.NS","ABCAPITAL.NS","ALKEM.NS","AMBER.NS","AMBUJACEM.NS","ANGELONE.NS","APOLLOHOSP.NS","ASHOKLEY.NS","ASIANPAINT.NS","ASTRAL.NS","AUROPHARMA.NS","DMART.NS","AXISBANK.NS","BSE.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BANDHANBNK.NS","BANKBARODA.NS","BANKINDIA.NS","BDL.NS","BEL.NS","BHARATFORG.NS","BHEL.NS","BPCL.NS","BHARTIARTL.NS","BIOCON.NS","BLUESTARCO.NS","BOSCHLTD.NS","BRITANNIA.NS","CGPOWER.NS","CANBK.NS","CDSL.NS","CHOLAFIN.NS","CIPLA.NS","COALINDIA.NS","COFORGE.NS","COLPAL.NS","CAMS.NS","CONCOR.NS","CROMPTON.NS","CUMMINSIND.NS","CYIENT.NS","DLF.NS","DABUR.NS","DALBHARAT.NS","DELHIVERY.NS","DIVISLAB.NS","DIXON.NS","DRREDDY.NS","ETERNAL.NS","EICHERMOT.NS","EXIDEIND.NS","NYKAA.NS","FORTIS.NS","GAIL.NS","GMRAIRPORT.NS","GLENMARK.NS","GODREJCP.NS","GODREJPROP.NS","GRASIM.NS","HCLTECH.NS","HDFCAMC.NS","HDFCBANK.NS","HDFCLIFE.NS","HFCL.NS","HAVELLS.NS","HEROMOTOCO.NS","HINDALCO.NS","HAL.NS","HINDPETRO.NS","HINDUNILVR.NS","HINDZINC.NS","POWERINDIA.NS","HUDCO.NS","ICICIBANK.NS","ICICIGI.NS","ICICIPRULI.NS","IDFCFIRSTB.NS","IIFL.NS","ITC.NS","INDIANB.NS","IEX.NS","IOC.NS","IRCTC.NS","IRFC.NS","IREDA.NS","IGL.NS","INDUSTOWER.NS","INDUSINDBK.NS","NAUKRI.NS","INFY.NS","INOXWIND.NS","INDIGO.NS","JINDALSTEL.NS","JSWENERGY.NS","JSWSTEEL.NS","JIOFIN.NS","JUBLFOOD.NS","KEI.NS","KPITTECH.NS","KALYANKJIL.NS","KAYNES.NS","KFINTECH.NS","KOTAKBANK.NS","LTF.NS","LICHSGFIN.NS","LTIM.NS","LT.NS","LAURUSLABS.NS","LICI.NS","LODHA.NS","LUPIN.NS","M&M.NS","MANAPPURAM.NS","MANKIND.NS","MARICO.NS","MARUTI.NS","MFSL.NS","MAXHEALTH.NS","MAZDOCK.NS","MPHASIS.NS","MCX.NS","MUTHOOTFIN.NS","NBCC.NS","NCC.NS","NHPC.NS","NMDC.NS","NTPC.NS","NATIONALUM.NS","NESTLEIND.NS","NUVAMA.NS","OBEROIRLTY.NS","ONGC.NS","OIL.NS","PAYTM.NS","OFSS.NS","POLICYBZR.NS","PGEL.NS","PIIND.NS","PNBHOUSING.NS","PAGEIND.NS","PATANJALI.NS","PERSISTENT.NS","PETRONET.NS","PIDILITIND.NS","PPLPHARMA.NS","POLYCAB.NS","PFC.NS","POWERGRID.NS","PRESTIGE.NS","PNB.NS","RBLBANK.NS","RECLTD.NS","RVNL.NS","RELIANCE.NS","SBICARD.NS","SBILIFE.NS","SHREECEM.NS","SRF.NS","SAMMAANCAP.NS","MOTHERSON.NS","SHRIRAMFIN.NS","SIEMENS.NS","SOLARINDS.NS","SONACOMS.NS","SBIN.NS","SAIL.NS","SUNPHARMA.NS","SUPREMEIND.NS","SUZLON.NS","SYNGENE.NS","TATACONSUM.NS","TITAGARH.NS","TVSMOTOR.NS","TCS.NS","TATAELXSI.NS","TMPV.NS","TATAPOWER.NS","TATASTEEL.NS","TATATECH.NS","TECHM.NS","FEDERALBNK.NS","INDHOTEL.NS","PHOENIXLTD.NS","TITAN.NS","TORNTPHARM.NS","TORNTPOWER.NS","TRENT.NS","TIINDIA.NS","UNOMINDA.NS","UPL.NS","ULTRACEMCO.NS","UNIONBANK.NS","UNITDSPR.NS","VBL.NS","VEDL.NS","IDEA.NS","VOLTAS.NS","WIPRO.NS","YESBANK.NS","ZYDUSLIFE.NS"]

# ========== DATA FETCHING WITH ERROR HANDLING ==========
def fetch_stock_data_yf(symbol, days=60):
    """Fetch stock data with multiple retry attempts"""
    max_retries = 2  # Reduced for faster testing
    for attempt in range(max_retries):
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            print(f"  📡 {symbol}... (Attempt {attempt + 1}/{max_retries})", end=" ")
            
            # Download data - SIMPLER METHOD
            stock = yf.download(
                symbol,
                period=f"{days}d",  # Simpler method
                progress=False,
                timeout=15
            )
            
            # Check if data is valid
            if stock.empty:
                print("❌ No data")
                time.sleep(1)  # Wait before retry
                continue
            
            # Ensure we have required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in stock.columns for col in required_cols):
                print("❌ Missing columns")
                continue
            
            # Check if we have enough data points
            if len(stock) < 15:
                print(f"❌ Only {len(stock)} days")
                continue
            
            # Fix: Extract single value from Series
            last_volume = stock['Volume'].iloc[-1]
            if hasattr(last_volume, '__len__'):
                last_volume = last_volume.iloc[0] if hasattr(last_volume, 'iloc') else last_volume[0]
            
            print(f"✅ {len(stock)} days, Vol: {last_volume:,.0f}")
            return stock
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            time.sleep(2)  # Longer wait on error
    
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

# ========== TEST YFINANCE CONNECTION ==========
def test_yfinance_connection():
    """Test if yfinance can fetch data - FIXED VERSION"""
    print("\n🔧 TESTING YFINANCE CONNECTION...")
    print("-" * 50)
    
    test_symbol = "RELIANCE.NS"
    try:
        # Quick test with 1 day
        test_data = yf.download(test_symbol, period="1d", progress=False)
        
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
            
            # FIXED: Extract single values properly
            last_price = test_data['Close'].iloc[-1]
            if hasattr(last_price, '__len__'):
                last_price = last_price.iloc[0] if hasattr(last_price, 'iloc') else last_price[0]
            
            last_volume = test_data['Volume'].iloc[-1]
            if hasattr(last_volume, '__len__'):
                last_volume = last_volume.iloc[0] if hasattr(last_volume, 'iloc') else last_volume[0]
            
            print(f"   Price: ₹{float(last_price):.2f}")
            print(f"   Volume: {int(last_volume):,}")
            print(f"   Date: {test_data.index[-1].date()}")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed with error: {e}")
        return False

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
            stock_data = fetch_stock_data_yf(symbol, days=30)  # 30 days for faster testing
            if stock_data is None:
                continue
            
            # Get volumes
            volumes = stock_data['Volume'].values
            
            # Detect patterns
            v_pattern = detect_v_pattern(volumes)
            u_pattern = detect_u_pattern(volumes)
            
            if v_pattern or u_pattern:
                # FIXED: Extract single price values
                current_price = stock_data['Close'].iloc[-1]
                prev_price = stock_data['Close'].iloc[-2]
                
                if hasattr(current_price, '__len__'):
                    current_price = current_price.iloc[0] if hasattr(current_price, 'iloc') else current_price[0]
                if hasattr(prev_price, '__len__'):
                    prev_price = prev_price.iloc[0] if hasattr(prev_price, 'iloc') else prev_price[0]
                
                price_change = ((float(current_price) - float(prev_price)) / float(prev_price)) * 100
                
                result = {
                    'Symbol': symbol.replace('.NS', ''),
                    'Price': f"₹{float(current_price):.2f}",
                    'Change': f"{price_change:+.2f}%",
                    'V_Pattern': '✅' if v_pattern else '❌',
                    'U_Pattern': '✅' if u_pattern else '❌',
                    'Volume': f"{int(stock_data['Volume'].iloc[-1]):,}",
                    'Days': len(stock_data)
                }
                
                results.append(result)
                print(f"    🎯 PATTERN FOUND in {symbol}!")
            
            # Small delay between stocks
            time.sleep(1.5)
            
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

# ========== MAIN EXECUTION ==========
def main():
    """Main function with proper structure"""
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
        return  # Don't exit, just return
    
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

# ========== ENTRY POINT ==========
if __name__ == "__main__":

    main()
