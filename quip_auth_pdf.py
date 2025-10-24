#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
import sys

def quip_to_pdf_with_auth(url, output_file="quip_document.pdf", username=None, password=None):
    """Convert Quip URL to PDF with midway authentication"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Remove headless for authentication
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Check if redirected to login page
        if "login" in driver.current_url.lower() or "signin" in driver.current_url.lower():
            print("Login required - handling authentication...")
            
            # Wait for login form
            try:
                # Try common login field selectors
                username_field = wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    'input[type="email"], input[name="username"], input[name="email"], input[id="username"]'
                )))
                
                password_field = driver.find_element(By.CSS_SELECTOR, 
                    'input[type="password"], input[name="password"], input[id="password"]')
                
                if username and password:
                    print("Entering credentials...")
                    username_field.send_keys(username)
                    password_field.send_keys(password)
                    
                    # Find and click login button
                    login_button = driver.find_element(By.CSS_SELECTOR,
                        'button[type="submit"], input[type="submit"], button:contains("Sign"), button:contains("Login")')
                    login_button.click()
                    
                    # Wait for redirect after login
                    time.sleep(3)
                else:
                    print("Manual login required - please login in the browser window")
                    input("Press Enter after logging in...")
                    
            except Exception as e:
                print(f"Authentication handling: {e}")
                print("Manual intervention may be required")
                input("Press Enter when ready to continue...")
        
        # Wait for content to load
        print("Waiting for content to load...")
        time.sleep(5)
        
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
            "marginRight": 0.4,
            "preferCSSPageSize": True
        })
        
        # Save PDF
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
    username = None
    password = None
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        username = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]
    
    print("Starting Quip to PDF conversion with authentication handling...")
    quip_to_pdf_with_auth(url, "quip_sap_community.pdf", username, password)
