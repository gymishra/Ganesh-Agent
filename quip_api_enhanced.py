#!/usr/bin/env python3
import requests
import json
import sys
import base64

def try_quip_api_methods(api_token, document_id):
    """Try different Quip API authentication methods"""
    
    methods = [
        # Method 1: Bearer token
        {'Authorization': f'Bearer {api_token}'},
        # Method 2: Basic auth with token as password
        {'Authorization': f'Basic {base64.b64encode(f":{api_token}".encode()).decode()}'},
        # Method 3: Custom header
        {'X-Quip-Token': api_token},
        # Method 4: Query parameter
        {}
    ]
    
    urls = [
        f'https://platform.quip.com/1/threads/{document_id}',
        f'https://platform.quip.com/1/threads/{document_id}?token={api_token}',
        f'https://quip-amazon.com/api/1/threads/{document_id}',
    ]
    
    for i, headers in enumerate(methods):
        for j, url in enumerate(urls):
            if i == 3 and j != 1:  # Skip query param method for non-query URLs
                continue
                
            try:
                print(f"🔄 Trying method {i+1}, URL {j+1}...")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Success with method {i+1}, URL {j+1}!")
                    return response.json()
                else:
                    print(f"   Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   Error: {e}")
    
    return None

def download_quip_enhanced(api_token, document_id):
    """Enhanced Quip download with multiple methods"""
    
    print(f"📡 Trying to fetch document: {document_id}")
    print(f"🔑 Using token: {api_token[:20]}...")
    
    data = try_quip_api_methods(api_token, document_id)
    
    if data:
        # Save the data
        with open("quip_api_success.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        print("✅ Data saved to quip_api_success.json")
        return True
    else:
        print("❌ All methods failed")
        return False

if __name__ == "__main__":
    document_id = "8UhjA0uQupLl"
    api_token = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
    
    download_quip_enhanced(api_token, document_id)
