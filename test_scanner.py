print("=" * 50)
print("INCOMEPLUS SCANNER TEST")
print("=" * 50)

print("\n1. Testing Python installation...")
import sys
print(f"✓ Python version: {sys.version}")

print("\n2. Testing required libraries...")
try:
    import yfinance
    print("✓ yfinance: INSTALLED")
except:
    print("✗ yfinance: NOT INSTALLED")

try:
    import pandas
    print("✓ pandas: INSTALLED")
except:
    print("✗ pandas: NOT INSTALLED")

try:
    import numpy
    print("✓ numpy: INSTALLED")
except:
    print("✗ numpy: NOT INSTALLED")

print("\n3. Testing Yahoo Finance connection...")
try:
    import yfinance as yf
    # Test with Reliance
    data = yf.download("RELIANCE.NS", period="1d", progress=False)
    
    if not data.empty:
        print("✓ Yahoo Finance: WORKING")
        print(f"  Stock: RELIANCE.NS")
        print(f"  Price: ₹{data['Close'].iloc[-1]:.2f}")
        print(f"  Date: {data.index[-1].date()}")
    else:
        print("✗ Yahoo Finance: NO DATA")
except Exception as e:
    print(f"✗ Yahoo Finance error: {e}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
input("\nPress Enter to close...")