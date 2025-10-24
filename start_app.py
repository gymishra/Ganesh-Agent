#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.insert(0, '/home/gyanmis')

# Set environment variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['FLASK_ENV'] = 'development'

# Import and run the app
from quip_uploader_app import app

if __name__ == '__main__':
    print("🚀 Starting Quip Document Uploader Web Application")
    print("📍 Access at: http://localhost:5000")
    print("🔐 Identity Center: https://d-9767435275.awsapps.com/start")
    print("📦 S3 Bucket: sap-qbiz-kbnew")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
