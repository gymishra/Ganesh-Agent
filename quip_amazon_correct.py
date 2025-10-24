#!/usr/bin/env python3
import requests
import json

def try_quip_amazon_endpoints(api_token, document_id):
    """Try different Quip Amazon API endpoints"""
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Different possible endpoints
    endpoints = [
        f'https://quip-amazon.com/api/1/threads/{document_id}',
        f'https://quip-amazon.com/1/threads/{document_id}',
        f'https://quip-amazon.com/api/threads/{document_id}',
        f'https://quip-amazon.com/dev/api/1/threads/{document_id}',
        f'https://platform.quip-amazon.com/1/threads/{document_id}',
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔄 Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                return response.json()
            elif response.status_code == 401:
                print("   401 - Check token permissions")
            elif response.status_code == 403:
                print("   403 - Access forbidden")
            elif response.status_code == 404:
                print("   404 - Endpoint not found")
            else:
                print(f"   Response preview: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    return None

def main():
    document_id = "8UhjA0uQupLl"
    api_token = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
    
    print("🔍 Testing Quip Amazon API endpoints...")
    data = try_quip_amazon_endpoints(api_token, document_id)
    
    if data:
        with open("quip_amazon_success.json", 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Data saved!")
    else:
        print("❌ All endpoints failed")
        print("\n💡 Alternative: The token might be for web authentication only")
        print("   Consider using the browser-based approach instead")

if __name__ == "__main__":
    main()
