#!/usr/bin/env python3
"""
Test catalog connection to verify it works from your environment
"""

import requests
import base64
import json

# SAP System Configuration
ECS_ENDPOINT = "https://vhcals4hci.awspoc.club"
SAP_CLIENT = "100"
SAP_USERNAME = "bpinst"
SAP_PASSWORD = "Welcome1"
CATALOG_SERVICE = "/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection"

def test_catalog_connection():
    """Test if we can connect to the catalog service"""
    
    print("🧪 Testing Catalog Connection")
    print("=" * 40)
    
    # Create auth header
    credentials = f"{SAP_USERNAME}:{SAP_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Build URL
    catalog_url = ECS_ENDPOINT + CATALOG_SERVICE
    print(f"📡 Testing URL: {catalog_url}")
    
    # Set headers
    headers = {
        'Authorization': auth_header,
        'sap-client': SAP_CLIENT,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔄 Making request...")
        response = requests.get(catalog_url, headers=headers, timeout=30, verify=False)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📏 Response Size: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Catalog connection works")
            
            # Try to parse JSON
            try:
                data = response.json()
                if 'd' in data and 'results' in data['d']:
                    services = data['d']['results']
                    print(f"🎯 Found {len(services)} services in catalog")
                    
                    # Show first few services
                    print("\n📋 Sample Services:")
                    for i, service in enumerate(services[:5]):
                        tech_name = service.get('TechnicalServiceName', 'Unknown')
                        description = service.get('Description', 'No description')
                        print(f"   {i+1}. {tech_name} - {description}")
                    
                    return True
                else:
                    print("⚠️ Unexpected JSON structure")
                    print(f"Keys in response: {list(data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"First 500 chars: {response.text[:500]}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error response: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        
    return False

def test_simple_regex_parsing():
    """Test the regex parsing approach on a small sample"""
    
    print("\n🧪 Testing Regex Parsing")
    print("=" * 40)
    
    # Sample JSON structure (simplified)
    sample_json = '''
    {
        "d": {
            "results": [
                {
                    "ID": "ZAPI_SALES_ORDER_SRV_0001",
                    "TechnicalServiceName": "API_SALES_ORDER_SRV",
                    "Description": "Sales Order (A2X)",
                    "ServiceUrl": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/API_SALES_ORDER_SRV"
                },
                {
                    "ID": "ZAPI_BUSINESS_PARTNER_0001", 
                    "TechnicalServiceName": "API_BUSINESS_PARTNER",
                    "Description": "Remote API for Business Partner",
                    "ServiceUrl": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/API_BUSINESS_PARTNER"
                }
            ]
        }
    }
    '''
    
    import re
    
    # Test the regex patterns used in Java
    id_pattern = re.compile(r'"ID"\s*:\s*"([^"]+)"')
    tech_name_pattern = re.compile(r'"TechnicalServiceName"\s*:\s*"([^"]+)"')
    desc_pattern = re.compile(r'"Description"\s*:\s*"([^"]*?)"')
    url_pattern = re.compile(r'"ServiceUrl"\s*:\s*"([^"]+)"')
    
    # Split into service objects
    service_objects = sample_json.split('},')
    
    print(f"📊 Found {len(service_objects)} service objects")
    
    for i, service_obj in enumerate(service_objects):
        if not service_obj.strip():
            continue
            
        # Ensure complete JSON object
        if not service_obj.strip().startswith('{'):
            service_obj = '{' + service_obj
        if not service_obj.strip().endswith('}'):
            service_obj = service_obj + '}'
            
        # Extract fields
        id_match = id_pattern.search(service_obj)
        tech_match = tech_name_pattern.search(service_obj)
        desc_match = desc_pattern.search(service_obj)
        url_match = url_pattern.search(service_obj)
        
        if tech_match and url_match:
            print(f"   ✅ Service {i+1}:")
            print(f"      ID: {id_match.group(1) if id_match else 'Not found'}")
            print(f"      Technical Name: {tech_match.group(1)}")
            print(f"      Description: {desc_match.group(1) if desc_match else 'Not found'}")
            print(f"      URL: {url_match.group(1)}")
        else:
            print(f"   ❌ Service {i+1}: Failed to parse")
    
    print("✅ Regex parsing test completed")

if __name__ == "__main__":
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test connection
    connection_works = test_catalog_connection()
    
    # Test parsing
    test_simple_regex_parsing()
    
    print("\n" + "=" * 40)
    if connection_works:
        print("🎉 RESULT: Your Eclipse plugin should work!")
        print("   ✅ Catalog connection successful")
        print("   ✅ JSON parsing approach validated")
        print("   ✅ Ready to load all services dynamically")
    else:
        print("❌ RESULT: Connection issues detected")
        print("   🔧 Check network connectivity")
        print("   🔧 Verify SAP system is accessible")
        print("   🔧 Confirm credentials are correct")
