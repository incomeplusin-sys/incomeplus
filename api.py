import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# FIX: This allows your GitHub website to talk to your Railway backend without errors
CORS(app, resources={r"/*": {"origins": "*"}})

# Your working API Key
ALPHA_VANTAGE_API_KEY = "JMY6SM927NKIJIXI" 

@app.route('/health', methods=['GET'])
def health():
    """Check if server is alive"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "message": "IncomePlus API is Online"
    })

@app.route('/scan', methods=['POST', 'GET'])
def scan_stocks():
    """Simple scan logic to test connection"""
    # For now, returning sample data to ensure your frontend works first
    results = [
        {"ticker": "RELIANCE.NS", "price": 2500.50, "change_percent": 1.2, "v_pattern": True, "u_pattern": False, "volume": 1200000},
        {"ticker": "TCS.NS", "price": 3400.10, "change_percent": -0.4, "v_pattern": False, "u_pattern": True, "volume": 850000}
    ]
    return jsonify({
        "status": "success",
        "data": results,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Railway sets the PORT automatically
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
