#!/usr/bin/env python3

import requests
import json
import base64
from datetime import datetime

def get_top_suppliers():
    """Get top 2 suppliers from FAP_DISPLAY_SUPPLIER_LIST service"""
    
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
    
    print("🔍 Retrieving Top 2 Suppliers")
    print("=" * 50)
    print(f"🌐 Service: FAP_DISPLAY_SUPPLIER_LIST")
    print(f"📅 Request Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # First, let's explore the service structure
    service_name = "FAP_DISPLAY_SUPPLIER_LIST"
    base_url = f"{sap_url}sap/opu/odata/sap/{service_name}/"
    
    try:
        # Get service document to see available entity sets
        print("🔍 Step 1: Exploring service structure...")
        response = session.get(base_url, verify=False, timeout=30)
        
        if response.status_code == 200:
            print("✅ Service accessible")
            
            # Try to parse service document
            try:
                data = response.json()
                if 'd' in data and 'EntitySets' in data['d']:
                    entity_sets = data['d']['EntitySets']
                    print(f"📋 Available EntitySets: {entity_sets}")
                else:
                    print("📋 Service document structure:")
                    print(json.dumps(data, indent=2)[:500] + "...")
            except:
                print("📋 Service document (XML format)")
                print(response.text[:300] + "...")
        
        # Try common entity names for suppliers
        print(f"\n🔍 Step 2: Trying to find supplier entities...")
        
        common_entity_names = [
            'SupplierSet',
            'Suppliers', 
            'SupplierList',
            'Supplier',
            'BusinessPartner',
            'Vendors',
            'VendorSet'
        ]
        
        suppliers_found = []
        
        for entity_name in common_entity_names:
            try:
                entity_url = f"{base_url}{entity_name}?$top=2"
                print(f"   🔗 Trying: {entity_name}")
                
                response = session.get(entity_url, verify=False, timeout=30)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if 'd' in data:
                            if 'results' in data['d'] and data['d']['results']:
                                suppliers = data['d']['results']
                                print(f"      ✅ Found {len(suppliers)} suppliers!")
                                suppliers_found = suppliers
                                break
                            elif isinstance(data['d'], list):
                                suppliers = data['d']
                                print(f"      ✅ Found {len(suppliers)} suppliers!")
                                suppliers_found = suppliers
                                break
                            elif isinstance(data['d'], dict) and len(data['d']) > 1:
                                print(f"      ✅ Found single supplier record!")
                                suppliers_found = [data['d']]
                                break
                        
                    except json.JSONDecodeError:
                        print(f"      ⚠️ Non-JSON response")
                        continue
                
                elif response.status_code == 404:
                    print(f"      ❌ Entity not found")
                elif response.status_code == 403:
                    print(f"      🚫 Access forbidden")
                
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
                continue
        
        # Display results
        print(f"\n📊 TOP 2 SUPPLIERS RESULTS")
        print("=" * 50)
        
        if suppliers_found:
            print(f"✅ Successfully retrieved {len(suppliers_found)} suppliers")
            print()
            
            for i, supplier in enumerate(suppliers_found[:2], 1):
                print(f"🏢 SUPPLIER {i}")
                print("-" * 30)
                
                # Display all available fields
                for key, value in supplier.items():
                    if value is not None and value != "":
                        # Format key for better readability
                        display_key = key.replace('_', ' ').title()
                        print(f"   {display_key}: {value}")
                
                print()
        
        else:
            print("❌ No suppliers found")
            print()
            print("💡 Possible reasons:")
            print("   • Entity names might be different")
            print("   • Service might use different structure")
            print("   • Data might be empty")
            print()
            
            # Try to get service metadata for better understanding
            print("🔍 Attempting to get service metadata...")
            metadata_url = f"{base_url}$metadata"
            
            try:
                metadata_response = session.get(metadata_url, verify=False, timeout=30)
                
                if metadata_response.status_code == 200:
                    print("✅ Metadata retrieved")
                    
                    # Try to parse XML metadata
                    try:
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(metadata_response.content)
                        
                        # Find EntitySet elements
                        entity_sets = []
                        for elem in root.iter():
                            if 'EntitySet' in elem.tag:
                                name = elem.get('Name')
                                entity_type = elem.get('EntityType')
                                if name:
                                    entity_sets.append({'name': name, 'type': entity_type})
                        
                        if entity_sets:
                            print("📋 Available EntitySets from metadata:")
                            for entity_set in entity_sets:
                                print(f"   • {entity_set['name']} ({entity_set['type']})")
                        
                    except Exception as e:
                        print(f"⚠️ Metadata parsing error: {str(e)}")
                        print("📝 Raw metadata preview:")
                        print(metadata_response.text[:500] + "...")
                
                else:
                    print(f"❌ Metadata not accessible: {metadata_response.status_code}")
            
            except Exception as e:
                print(f"❌ Metadata retrieval error: {str(e)}")
    
    except Exception as e:
        print(f"❌ Service connection error: {str(e)}")
    
    print(f"\n📋 SUMMARY")
    print("=" * 50)
    print(f"🌐 Service: FAP_DISPLAY_SUPPLIER_LIST")
    print(f"📊 Status: {'✅ Success' if suppliers_found else '❌ No data found'}")
    print(f"👥 Suppliers Retrieved: {len(suppliers_found) if suppliers_found else 0}")
    
    return suppliers_found

if __name__ == "__main__":
    get_top_suppliers()
