#!/usr/bin/env python3
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys

def quip_to_pdf(url, output_file="quip_document.pdf", api_token=None):
    """Convert Quip URL to PDF"""
    
    # Chrome options for headless PDF generation
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--print-to-pdf")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Add API token as header if provided
        if api_token:
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": driver.execute_script("return navigator.userAgent") + f" QuipToken/{api_token}"
            })
        
        # Navigate to URL
        driver.get(url)
        time.sleep(3)  # Wait for content to load
        
        # Generate PDF
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
        import base64
        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        print(f"PDF saved as: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    url = "https://quip-amazon.com/8UhjA0uQupLl/Amazon-Q-Business-for-internal-AWS-SAP-community"
    api_token = None  # Replace with your API token if needed
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        api_token = sys.argv[2]
    
    quip_to_pdf(url, "quip_sap_community.pdf", api_token)
