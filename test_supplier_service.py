#!/usr/bin/env python3

import requests
import base64

def test_supplier_service():
    """Test if FAP_DISPLAY_SUPPLIER_LIST service exists in SAP system"""
    
    # SAP credentials
    sap_url = "https://vhcals4hci.awspoc.club/"
    username = "bpinst"
    password = "Welcome1"
    
    # Setup session
    session = requests.Session()
    auth_b64 = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    session.headers.update({
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json'
    })
    
    requests.packages.urllib3.disable_warnings()
    
    print("🔍 Testing FAP_DISPLAY_SUPPLIER_LIST Service")
    print("=" * 60)
    print(f"🌐 SAP System: {sap_url}")
    print(f"👤 User: {username}")
    print()
    
    # Test the specific service
    service_name = "FAP_DISPLAY_SUPPLIER_LIST"
    service_url = f"{sap_url}sap/opu/odata/sap/{service_name}/"
    
    try:
        print(f"🔍 Testing: {service_name}")
        response = session.get(service_url, verify=False, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SERVICE EXISTS and is accessible!")
            
            # Try to get metadata
            metadata_url = f"{service_url}$metadata"
            metadata_response = session.get(metadata_url, verify=False, timeout=30)
            
            if metadata_response.status_code == 200:
                print("✅ Metadata accessible")
                
                # Parse metadata to find entities
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(metadata_response.content)
                    
                    # Find EntitySet elements
                    entity_sets = []
                    for elem in root.iter():
                        if 'EntitySet' in elem.tag:
                            name = elem.get('Name')
                            if name:
                                entity_sets.append(name)
                    
                    print(f"📋 Available Entities: {entity_sets}")
                    
                    # Try to get sample data
                    if entity_sets:
                        sample_entity = entity_sets[0]
                        sample_url = f"{service_url}{sample_entity}?$top=3"
                        sample_response = session.get(sample_url, verify=False, timeout=30)
                        
                        if sample_response.status_code == 200:
                            print(f"✅ Sample data accessible from {sample_entity}")
                            
                            try:
                                data = sample_response.json()
                                if 'd' in data and 'results' in data['d']:
                                    results = data['d']['results']
                                    print(f"📊 Found {len(results)} supplier records")
                                    
                                    if results:
                                        print("📋 Sample supplier data:")
                                        for i, supplier in enumerate(results, 1):
                                            print(f"   {i}. {supplier}")
                                            
                            except:
                                print("⚠️ Could not parse sample data")
                        else:
                            print(f"⚠️ Sample data not accessible: {sample_response.status_code}")
                
                except Exception as e:
                    print(f"⚠️ Metadata parsing error: {str(e)}")
            else:
                print(f"⚠️ Metadata not accessible: {metadata_response.status_code}")
        
        elif response.status_code == 404:
            print("❌ SERVICE NOT FOUND")
            print("💡 This service may not be available in this SAP system")
            
        elif response.status_code == 403:
            print("🚫 ACCESS FORBIDDEN")
            print("💡 Service exists but user lacks authorization")
            
        elif response.status_code == 401:
            print("🔐 AUTHENTICATION REQUIRED")
            print("💡 Credentials may be insufficient")
        
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"📝 Response: {response.text[:200]}...")
    
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
    
    # Also test related supplier services
    print(f"\n🔍 Testing Related Supplier Services:")
    print("-" * 40)
    
    related_services = [
        "API_BUSINESS_PARTNER",
        "API_SUPPLIER_SRV", 
        "SUPPLIER_SRV",
        "API_PURCHASING_SUPPLIER_SRV"
    ]
    
    for service in related_services:
        try:
            test_url = f"{sap_url}sap/opu/odata/sap/{service}/"
            response = session.get(test_url, verify=False, timeout=15)
            
            status_icon = "✅" if response.status_code == 200 else "❌" if response.status_code == 404 else "🚫" if response.status_code == 403 else "⚠️"
            print(f"   {status_icon} {service}: {response.status_code}")
            
        except:
            print(f"   ❌ {service}: Connection error")

if __name__ == "__main__":
    test_supplier_service()
