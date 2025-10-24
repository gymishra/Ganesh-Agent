#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
import sys

def quip_sso_pdf(url, output_file="quip_document.pdf"):
    """Convert Quip URL to PDF with SSO authentication support"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"Opening: {url}")
        driver.get(url)
        
        # Handle various authentication scenarios
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check for different auth patterns
        if any(keyword in current_url.lower() for keyword in ['login', 'signin', 'auth', 'sso']):
            print("Authentication detected. Please complete login in the browser.")
            print("This script will wait for you to:")
            print("1. Complete SSO authentication")
            print("2. Navigate to the document")
            print("3. Wait for content to load")
            
            # Wait for user to complete authentication
            input("\nPress Enter after you've successfully logged in and can see the document content...")
            
            # Additional wait for content
            time.sleep(3)
        
        # Check if we're on the right page
        if "quip" not in driver.current_url:
            print("Warning: Not on Quip domain. Current URL:", driver.current_url)
        
        # Wait for document content to load
        print("Waiting for document content...")
        try:
            # Wait for typical Quip content indicators
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(5)  # Additional wait for dynamic content
        except:
            print("Timeout waiting for content, proceeding anyway...")
        
        # Generate PDF
        print("Generating PDF...")
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,
            "paperHeight": 11.7,
            "marginTop": 0.3,
            "marginBottom": 0.3,
            "marginLeft": 0.3,
            "marginRight": 0.3,
            "preferCSSPageSize": True,
            "displayHeaderFooter": False
        })
        
        # Save PDF
        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        print(f"✅ PDF saved successfully: {output_file}")
        
        # Get file size
        import os
        size = os.path.getsize(output_file)
        print(f"File size: {size/1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://quip-amazon.com/8UhjA0uQupLl/Amazon-Q-Business-for-internal-AWS-SAP-community"
    output = sys.argv[2] if len(sys.argv) > 2 else "quip_document.pdf"
    
    quip_sso_pdf(url, output)
