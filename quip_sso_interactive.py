#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import base64
import sys

def quip_sso_interactive(url, output_file="quip_sso_authenticated.pdf"):
    """Convert Quip URL to PDF with interactive SSO login"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    service = Service("/usr/bin/chromedriver")
    
    try:
        print("🚀 Starting Chrome browser...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"📄 Opening Quip URL: {url}")
        driver.get(url)
        
        print("\n" + "="*60)
        print("🔐 AMAZON SSO LOGIN REQUIRED")
        print("="*60)
        print("1. Complete your Amazon SSO login in the browser window")
        print("2. Navigate through any authentication steps")
        print("3. Wait until you can see the Quip document content")
        print("4. Then come back here and press Enter")
        print("="*60)
        
        input("\n⏳ Press Enter after you've completed SSO login and can see the document...")
        
        print("⏱️  Waiting for content to fully load...")
        time.sleep(5)
        
        print("📄 Generating PDF...")
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,
            "paperHeight": 11.7,
            "marginTop": 0.4,
            "marginBottom": 0.4,
            "marginLeft": 0.4,
            "marginRight": 0.4
        })
        
        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        import os
        size = os.path.getsize(output_file)
        print(f"✅ PDF saved: {output_file}")
        print(f"📊 File size: {size/1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    url = "https://quip-amazon.com/8UhjA0uQupLl/Amazon-Q-Business-for-internal-AWS-SAP-community"
    output = sys.argv[1] if len(sys.argv) > 1 else "quip_sso_authenticated.pdf"
    
    quip_sso_interactive(url, output)
