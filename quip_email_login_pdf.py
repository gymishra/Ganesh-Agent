#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
import sys

def quip_email_login_pdf(url, email, password, output_file="quip_document.pdf"):
    """Convert Quip URL to PDF with email login"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    service = Service("/usr/bin/chromedriver")
    
    try:
        print("Starting Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        print(f"Opening: {url}")
        driver.get(url)
        
        # Wait for email input field
        print("Looking for email input...")
        email_field = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, 'input[type="email"], input[name="email"], input[placeholder*="email" i]'
        )))
        
        print(f"Entering email: {email}")
        email_field.clear()
        email_field.send_keys(email)
        
        # Look for continue/next button
        try:
            continue_btn = driver.find_element(By.CSS_SELECTOR, 
                'button[type="submit"], input[type="submit"], button:contains("Continue"), button:contains("Next")')
            continue_btn.click()
            time.sleep(2)
        except:
            print("No continue button found, proceeding...")
        
        # Wait for password field (might appear after email)
        try:
            print("Looking for password field...")
            password_field = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 'input[type="password"], input[name="password"]'
            )))
            
            print("Entering password...")
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login
            login_btn = driver.find_element(By.CSS_SELECTOR,
                'button[type="submit"], input[type="submit"], button:contains("Sign"), button:contains("Login")')
            login_btn.click()
            
        except Exception as e:
            print(f"Password field not found or error: {e}")
        
        # Wait for redirect and content load
        print("Waiting for content to load...")
        time.sleep(10)
        
        # Generate PDF
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
    email = sys.argv[1] if len(sys.argv) > 1 else input("Enter your email: ")
    password = sys.argv[2] if len(sys.argv) > 2 else input("Enter your password: ")
    output = sys.argv[3] if len(sys.argv) > 3 else "quip_sap_community_authenticated.pdf"
    
    quip_email_login_pdf(url, email, password, output)
