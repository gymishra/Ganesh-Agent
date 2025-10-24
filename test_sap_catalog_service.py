#!/usr/bin/env python3
"""
Test SAP OData Catalog Service
Fetches all available OData services from your SAP system
"""

import requests
import json
import base64
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# SAP System Configuration
ECS_ENDPOINT = "https://vhcals4hci.awspoc.club"
SAP_CLIENT = "100"
SAP_USERNAME = "bpinst"
SAP_PASSWORD = "Welcome1"

# Catalog Service Endpoints to try
CATALOG_ENDPOINTS = [
    "/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection",
    "/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection", 
    "/sap/bc/rest/iwfnd/catalogservice/ServiceCollection",
    "/sap/opu/odata/IWFND/CATALOGSERVICE/ServiceCollection",
    "/sap/opu/odata4/iwfnd/config/default/iwfnd/catalog/0002/Services"
]

def create_auth_header():
    """Create Basic Authentication header"""
    credentials = f"{SAP_USERNAME}:{SAP_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def test_catalog_endpoint(endpoint):
    """Test a specific catalog endpoint"""
    url = urljoin(ECS_ENDPOINT, endpoint)
    
    headers = {
        'Authorization': create_auth_header(),
        'sap-client': SAP_CLIENT,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 Testing catalog endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS!")
            
            # Try to parse as JSON first
            try:
                data = response.json()
                print(f"   📊 JSON Response with {len(str(data))} characters")
                
                # Look for service collections
                if 'd' in data and 'results' in data['d']:
                    services = data['d']['results']
                    print(f"   🎯 Found {len(services)} services in catalog")
                    
                    # Show first few services
                    for i, service in enumerate(services[:5]):
                        service_id = service.get('ID', service.get('TechnicalServiceName', 'Unknown'))
                        title = service.get('Title', service.get('Description', 'No title'))
                        print(f"      {i+1}. {service_id}: {title}")
                    
                    if len(services) > 5:
                        print(f"      ... and {len(services) - 5} more services")
                        
                    return services
                    
            except json.JSONDecodeError:
                # Try XML parsing
                try:
                    root = ET.fromstring(response.text)
                    print("   📄 XML Response received")
                    
                    # Look for entry elements (Atom feed format)
                    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                    if entries:
                        print(f"   🎯 Found {len(entries)} service entries")
                        return parse_xml_catalog(entries)
                        
                except ET.ParseError:
                    print("   📝 Plain text response")
                    print(f"   First 500 chars: {response.text[:500]}...")
                    
        elif response.status_code == 401:
            print("   🔐 Authentication failed")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found")
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        
    return None

def parse_xml_catalog(entries):
    """Parse XML catalog entries"""
    services = []
    
    for entry in entries:
        # Extract service information from XML
        title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
        content_elem = entry.find('.//{http://www.w3.org/2005/Atom}content')
        
        if title_elem is not None:
            service_info = {
                'ID': title_elem.text,
                'Title': title_elem.text
            }
            
            # Try to extract more details from content
            if content_elem is not None:
                properties = content_elem.find('.//{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
                if properties is not None:
                    for prop in properties:
                        tag_name = prop.tag.split('}')[-1]  # Remove namespace
                        service_info[tag_name] = prop.text
                        
            services.append(service_info)
            
    return services

def discover_odata_services():
    """Try all catalog endpoints to discover OData services"""
    print("🚀 Starting SAP OData Service Discovery")
    print(f"🌐 Target System: {ECS_ENDPOINT}")
    print(f"👤 Client: {SAP_CLIENT}")
    
    all_services = []
    
    for endpoint in CATALOG_ENDPOINTS:
        services = test_catalog_endpoint(endpoint)
        if services:
            all_services.extend(services)
            print(f"\n✅ Successfully discovered services from: {endpoint}")
            break
    
    if all_services:
        print(f"\n🎉 DISCOVERY COMPLETE!")
        print(f"📊 Total services found: {len(all_services)}")
        
        # Categorize services
        categories = {}
        for service in all_services:
            service_id = service.get('ID', service.get('TechnicalServiceName', 'Unknown'))
            category = categorize_service(service_id)
            
            if category not in categories:
                categories[category] = []
            categories[category].append(service)
        
        print(f"\n📋 Services by Category:")
        for category, services in categories.items():
            print(f"\n{category} ({len(services)} services):")
            for service in services[:3]:  # Show first 3 in each category
                service_id = service.get('ID', service.get('TechnicalServiceName', 'Unknown'))
                title = service.get('Title', service.get('Description', 'No title'))
                print(f"  • {service_id}: {title}")
            if len(services) > 3:
                print(f"  ... and {len(services) - 3} more")
                
        # Save results
        with open('/home/gyanmis/discovered_odata_services.json', 'w') as f:
            json.dump(all_services, f, indent=2)
        print(f"\n💾 Results saved to: /home/gyanmis/discovered_odata_services.json")
        
    else:
        print("\n❌ No services discovered from any catalog endpoint")
        print("🔧 Possible issues:")
        print("   • Catalog service not enabled")
        print("   • Different endpoint URLs needed")
        print("   • Authentication/authorization issues")
        print("   • Network connectivity problems")

def categorize_service(service_name):
    """Categorize service by name pattern"""
    service_name = service_name.upper()
    
    if any(keyword in service_name for keyword in ['SALES', 'ORDER', 'SO_']):
        return "📊 Sales & Distribution"
    elif any(keyword in service_name for keyword in ['MATERIAL', 'PRODUCT', 'ITEM']):
        return "📦 Material Management"
    elif any(keyword in service_name for keyword in ['PARTNER', 'CUSTOMER', 'SUPPLIER', 'VENDOR']):
        return "👥 Master Data"
    elif any(keyword in service_name for keyword in ['PURCHASE', 'PROCUREMENT', 'PO_']):
        return "🛒 Procurement"
    elif any(keyword in service_name for keyword in ['FINANCIAL', 'ACCOUNTING', 'JOURNAL', 'GL_']):
        return "💰 Finance & Accounting"
    elif any(keyword in service_name for keyword in ['WORKFLOW', 'APPROVAL', 'TASK']):
        return "🔄 Business Process"
    else:
        return "🔧 Other Services"

if __name__ == "__main__":
    # Disable SSL warnings for self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    discover_odata_services()
