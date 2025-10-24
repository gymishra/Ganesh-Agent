#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import base64
import sys

def quip_sso_robust(url, output_file="quip_sso_final.pdf"):
    """Robust Quip SSO login with session preservation"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    service = Service("/usr/bin/chromedriver")
    driver = None
    
    try:
        print("🚀 Starting Chrome with debugging...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"📄 Opening: {url}")
        driver.get(url)
        
        print("\n" + "🔐 AMAZON SSO LOGIN INSTRUCTIONS" + "\n" + "="*50)
        print("1. ✅ Complete Amazon SSO in the browser")
        print("2. ✅ Wait for Quip document to load completely")
        print("3. ✅ Keep the browser window open")
        print("4. ✅ Come back here and type 'done' + Enter")
        print("="*50)
        
        while True:
            user_input = input("\n⏳ Type 'done' when ready, or 'check' to verify: ").strip().lower()
            
            if user_input == 'done':
                break
            elif user_input == 'check':
                try:
                    current_url = driver.current_url
                    title = driver.title
                    print(f"📍 Current URL: {current_url}")
                    print(f"📋 Page Title: {title}")
                except:
                    print("❌ Browser session lost")
                    return False
            else:
                print("Please type 'done' or 'check'")
        
        print("📄 Generating PDF...")
        
        # Check if browser is still alive
        try:
            driver.current_url
        except:
            print("❌ Browser session lost. Please restart.")
            return False
        
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,
            "paperHeight": 11.7,
            "marginTop": 0.3,
            "marginBottom": 0.3,
            "marginLeft": 0.3,
            "marginRight": 0.3,
            "displayHeaderFooter": False
        })
        
        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
        
        import os
        size = os.path.getsize(output_file)
        print(f"✅ SUCCESS! PDF saved: {output_file}")
        print(f"📊 File size: {size/1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    url = "https://quip-amazon.com/8UhjA0uQupLl/Amazon-Q-Business-for-internal-AWS-SAP-community"
    output = sys.argv[1] if len(sys.argv) > 1 else "quip_sso_final.pdf"
    
    success = quip_sso_robust(url, output)
    
    if success:
        print("\n🎉 Ready to upload to S3!")
        upload = input("Upload to S3 now? (y/n): ").strip().lower()
        if upload == 'y':
            import subprocess
            subprocess.run(["aws", "s3", "cp", output, "s3://quip-documents-for-q-business/"])
            print("✅ Uploaded to S3!")
