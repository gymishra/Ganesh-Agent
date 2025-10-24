#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import base64
import sys

def quip_to_pdf_simple(url, output_file="quip_document.pdf"):
    """Simple Quip URL to PDF converter"""
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    # Service with explicit driver path
    service = Service("/usr/bin/chromedriver")
    
    try:
        print("Starting Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Opening: {url}")
        driver.get(url)
        
        print("Waiting for page to load...")
        time.sleep(10)  # Wait for content
        
        print("Generating PDF...")
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
        
        # Save PDF
        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        print(f"✅ PDF saved: {output_file}")
        
        # Check file size
        import os
        size = os.path.getsize(output_file)
        print(f"File size: {size/1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    url = "https://quip-amazon.com/8UhjA0uQupLl/Amazon-Q-Business-for-internal-AWS-SAP-community"
    output = "quip_sap_community.pdf"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        output = sys.argv[2]
    
    quip_to_pdf_simple(url, output)
