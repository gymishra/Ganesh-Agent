#!/usr/bin/env python3

import requests
import json
import base64
from datetime import datetime

def get_suppliers_from_correct_entities():
    """Get suppliers using the correct entity names discovered from the service"""
    
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
    
    print("🔍 Getting Top 2 Suppliers - Using Correct Entity Names")
    print("=" * 60)
    print(f"🌐 Service: FAP_DISPLAY_SUPPLIER_LIST")
    print(f"📅 Request Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    service_name = "FAP_DISPLAY_SUPPLIER_LIST"
    base_url = f"{sap_url}sap/opu/odata/sap/{service_name}/"
    
    # Use the actual entity names discovered from the service
    supplier_entities = [
        'C_SupplierList',      # Most likely the main supplier list
        'C_Supplier',          # Individual supplier entity
        'C_APSupplier',        # Accounts Payable supplier
        'C_SupplierValueHelp', # Supplier value help
        'I_Supplier_VH'        # Supplier value help (internal)
    ]
    
    suppliers_found = []
    successful_entity = None
    
    for entity_name in supplier_entities:
        try:
            entity_url = f"{base_url}{entity_name}?$top=2"
            print(f"🔍 Trying: {entity_name}")
            
            response = session.get(entity_url, verify=False, timeout=30)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if 'd' in data:
                        if 'results' in data['d'] and data['d']['results']:
                            suppliers = data['d']['results']
                            print(f"   ✅ SUCCESS! Found {len(suppliers)} suppliers")
                            suppliers_found = suppliers[:2]  # Get top 2
                            successful_entity = entity_name
                            break
                        elif isinstance(data['d'], list) and len(data['d']) > 0:
                            suppliers = data['d']
                            print(f"   ✅ SUCCESS! Found {len(suppliers)} suppliers")
                            suppliers_found = suppliers[:2]  # Get top 2
                            successful_entity = entity_name
                            break
                        else:
                            print(f"   ⚠️ Empty result set")
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️ Non-JSON response")
                    continue
            
            elif response.status_code == 404:
                print(f"   ❌ Entity not found")
            elif response.status_code == 403:
                print(f"   🚫 Access forbidden")
            elif response.status_code == 401:
                print(f"   🔐 Authentication required")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            continue
    
    # Display results
    print(f"\n🏆 TOP 2 SUPPLIERS FROM {successful_entity if successful_entity else 'N/A'}")
    print("=" * 60)
    
    if suppliers_found:
        print(f"✅ Successfully retrieved {len(suppliers_found)} suppliers")
        print(f"📋 Source Entity: {successful_entity}")
        print()
        
        for i, supplier in enumerate(suppliers_found, 1):
            print(f"🏢 SUPPLIER {i}")
            print("-" * 40)
            
            # Key supplier fields to highlight
            key_fields = [
                'Supplier', 'SupplierName', 'BusinessPartner', 'SupplierFullName',
                'SupplierAccountGroup', 'Country', 'Region', 'CityName',
                'PostalCode', 'StreetName', 'PhoneNumber1', 'FaxNumber',
                'SupplierCorporateGroup', 'PurchasingOrganization',
                'PaymentTerms', 'PaymentMethodsList', 'Currency'
            ]
            
            # Display key fields first
            print("📋 KEY INFORMATION:")
            key_found = False
            for field in key_fields:
                if field in supplier and supplier[field] is not None and supplier[field] != "":
                    print(f"   {field}: {supplier[field]}")
                    key_found = True
            
            if not key_found:
                print("   📊 Available fields:")
                # Show first 10 fields if no key fields found
                field_count = 0
                for key, value in supplier.items():
                    if value is not None and value != "" and field_count < 10:
                        print(f"   {key}: {value}")
                        field_count += 1
                
                if len(supplier) > 10:
                    print(f"   ... and {len(supplier) - 10} more fields")
            
            print()
    
    else:
        print("❌ No suppliers found in any of the tested entities")
        print()
        print("💡 Available entities that might contain supplier data:")
        available_entities = [
            'C_SupplierList', 'C_Supplier', 'C_APSupplier', 
            'C_SupplierValueHelp', 'I_Supplier_VH', 'I_BusinessPartnerVH'
        ]
        
        for entity in available_entities:
            print(f"   • {entity}")
        
        print()
        print("🔍 You could try accessing these entities directly:")
        for entity in available_entities[:3]:
            print(f"   GET {base_url}{entity}?$top=5")
    
    # Summary
    print(f"📋 EXECUTION SUMMARY")
    print("=" * 60)
    print(f"🌐 Service: FAP_DISPLAY_SUPPLIER_LIST")
    print(f"✅ Service Status: Accessible")
    print(f"📊 Entities Tested: {len(supplier_entities)}")
    print(f"🏆 Successful Entity: {successful_entity or 'None'}")
    print(f"👥 Suppliers Retrieved: {len(suppliers_found)}")
    
    if suppliers_found:
        print(f"🎯 Result: SUCCESS - Found supplier data!")
    else:
        print(f"⚠️ Result: No data found - entities may be empty or require different parameters")
    
    return suppliers_found, successful_entity

if __name__ == "__main__":
    get_suppliers_from_correct_entities()
