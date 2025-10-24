#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin
from datetime import datetime

class SAPAuthTester:
    """Test different authentication methods for SAP system"""
    
    def __init__(self):
        self.sap_url = "https://vhcals4hci.awspoc.club/"
        self.username = "bpinst"
        self.passwords = ["Welcome1", "welcome1", "WELCOME1"]  # Try different cases
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()
    
    def test_basic_auth_variations(self):
        """Test different basic auth variations"""
        
        print("🔐 Testing Basic Authentication Variations")
        print("=" * 60)
        
        for password in self.passwords:
            print(f"\n🔑 Testing: {self.username} / {password}")
            print("-" * 40)
            
            session = requests.Session()
            
            # Setup authentication
            auth_string = f"{self.username}:{password}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            session.headers.update({
                'Authorization': f'Basic {auth_b64}',
                'Accept': 'application/json, application/xml, text/html',
                'User-Agent': 'SAP-Auth-Tester/1.0'
            })
            
            # Test different endpoints
            test_endpoints = [
                '/sap/opu/odata/',
                '/sap/bc/webdynpro/',
                '/sap/bc/gui/sap/its/webgui',
                '/sap/public/ping'
            ]
            
            auth_success = False
            
            for endpoint in test_endpoints:
                try:
                    url = urljoin(self.sap_url, endpoint)
                    response = session.get(url, verify=False, timeout=30)
                    
                    print(f"   {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        auth_success = True
                        print(f"      ✅ Success!")
                        
                        # Check for SAP-specific content
                        if 'sap' in response.text.lower():
                            print(f"      📋 SAP content detected")
                        
                        # Check headers
                        sap_headers = {k: v for k, v in response.headers.items() 
                                     if 'sap' in k.lower()}
                        if sap_headers:
                            print(f"      📊 SAP headers: {list(sap_headers.keys())}")
                    
                    elif response.status_code == 401:
                        print(f"      🔐 Auth required")
                    elif response.status_code == 403:
                        print(f"      🚫 Forbidden")
                    
                except Exception as e:
                    print(f"   {endpoint}: Error - {str(e)}")
            
            if auth_success:
                print(f"✅ Authentication SUCCESSFUL with {password}")
                return session, password
            else:
                print(f"❌ Authentication FAILED with {password}")
        
        return None, None
    
    def test_odata_with_working_auth(self, session, password):
        """Test OData access with working authentication"""
        
        print(f"\n🔍 Testing OData Access with Working Auth")
        print("=" * 60)
        print(f"🔑 Using: {self.username} / {password}")
        
        # Test OData service catalog
        catalog_urls = [
            '/sap/opu/odata/',
            '/sap/opu/odata/sap/',
            '/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/',
            '/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection'
        ]
        
        for catalog_url in catalog_urls:
            try:
                url = urljoin(self.sap_url, catalog_url)
                print(f"\n🔍 Testing: {catalog_url}")
                
                response = session.get(url, verify=False, timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ OData catalog accessible!")
                    
                    # Try to parse content
                    content_type = response.headers.get('content-type', '').lower()
                    print(f"   📋 Content-Type: {content_type}")
                    
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   📊 JSON data structure: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                        except:
                            print(f"   ⚠️ JSON parsing failed")
                    
                    elif 'xml' in content_type:
                        print(f"   📊 XML content ({len(response.content)} bytes)")
                    
                    # Show content preview
                    preview = response.text[:300].replace('\n', ' ')
                    print(f"   📝 Preview: {preview}...")
                    
                elif response.status_code == 401:
                    print(f"   🔐 Still requires auth")
                elif response.status_code == 403:
                    print(f"   🚫 Access forbidden")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    def test_specific_invoice_services(self, session, password):
        """Test specific invoice-related services"""
        
        print(f"\n🎯 Testing Invoice Services")
        print("=" * 60)
        
        invoice_services = [
            'API_BILLING_DOCUMENT_SRV',
            'API_SALES_ORDER_SRV',
            'API_BUSINESS_PARTNER'
        ]
        
        for service in invoice_services:
            try:
                service_url = f"{self.sap_url}sap/opu/odata/sap/{service}/"
                print(f"\n🔍 Testing: {service}")
                
                response = session.get(service_url, verify=False, timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Service accessible!")
                    
                    # Try to get metadata
                    metadata_url = f"{service_url}$metadata"
                    metadata_response = session.get(metadata_url, verify=False, timeout=30)
                    
                    if metadata_response.status_code == 200:
                        print(f"   ✅ Metadata accessible!")
                        
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
                            
                            print(f"   📋 Entities found: {entity_sets[:5]}")  # Show first 5
                            
                            # Try to access an entity
                            if entity_sets:
                                entity_url = f"{service_url}{entity_sets[0]}?$top=1"
                                entity_response = session.get(entity_url, verify=False, timeout=30)
                                print(f"   📊 Sample data access: {entity_response.status_code}")
                                
                                if entity_response.status_code == 200:
                                    print(f"   ✅ Can access entity data!")
                        
                        except Exception as e:
                            print(f"   ⚠️ Metadata parsing error: {str(e)}")
                    
                elif response.status_code == 401:
                    print(f"   🔐 Auth required")
                elif response.status_code == 403:
                    print(f"   🚫 Access forbidden")
                elif response.status_code == 404:
                    print(f"   ❌ Service not found")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    def search_invoice_with_working_auth(self, session, password, invoice_number):
        """Search for invoice with working authentication"""
        
        print(f"\n🔍 Searching for Invoice: {invoice_number}")
        print("=" * 60)
        
        # Services to try
        services_to_try = [
            ('API_SALES_ORDER_SRV', 'A_SalesOrder', 'SalesOrder'),
            ('API_BILLING_DOCUMENT_SRV', 'A_BillingDocument', 'BillingDocument'),
            ('API_BUSINESS_PARTNER', 'A_Customer', 'Customer')
        ]
        
        for service_name, entity_name, key_field in services_to_try:
            try:
                print(f"\n🔍 Searching in {service_name}")
                
                # Try different search approaches
                search_urls = [
                    f"{self.sap_url}sap/opu/odata/sap/{service_name}/{entity_name}('{invoice_number}')",
                    f"{self.sap_url}sap/opu/odata/sap/{service_name}/{entity_name}?$filter={key_field} eq '{invoice_number}'",
                    f"{self.sap_url}sap/opu/odata/sap/{service_name}/{entity_name}?$top=5"
                ]
                
                for search_url in search_urls:
                    try:
                        response = session.get(search_url, verify=False, timeout=30)
                        print(f"   Query: {search_url.split('/')[-1]}")
                        print(f"   Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if 'd' in data:
                                    if 'results' in data['d'] and data['d']['results']:
                                        results = data['d']['results']
                                        print(f"   ✅ Found {len(results)} records!")
                                        
                                        # Check if any match our invoice number
                                        for record in results:
                                            if str(record.get(key_field, '')) == str(invoice_number):
                                                print(f"   🎯 MATCH FOUND!")
                                                return record
                                    
                                    elif isinstance(data['d'], dict) and len(data['d']) > 1:
                                        print(f"   ✅ Found single record!")
                                        return data['d']
                                
                            except json.JSONDecodeError:
                                print(f"   ⚠️ Non-JSON response")
                        
                        elif response.status_code == 404:
                            print(f"   ❌ Not found")
                        
                    except Exception as e:
                        print(f"   ❌ Query error: {str(e)}")
                        
            except Exception as e:
                print(f"❌ Service error: {str(e)}")
        
        return None

def main():
    """Main function"""
    
    print("🔐 SAP Authentication & Invoice Search Tester")
    print("=" * 70)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target Invoice: 1023456")
    
    tester = SAPAuthTester()
    
    # Test authentication
    working_session, working_password = tester.test_basic_auth_variations()
    
    if working_session and working_password:
        print(f"\n🎉 AUTHENTICATION SUCCESS!")
        print(f"✅ Working credentials: bpinst / {working_password}")
        
        # Test OData access
        tester.test_odata_with_working_auth(working_session, working_password)
        
        # Test specific services
        tester.test_specific_invoice_services(working_session, working_password)
        
        # Search for the invoice
        invoice_result = tester.search_invoice_with_working_auth(working_session, working_password, "1023456")
        
        if invoice_result:
            print(f"\n🎯 INVOICE FOUND!")
            print("=" * 40)
            for key, value in invoice_result.items():
                print(f"{key}: {value}")
        else:
            print(f"\n❌ Invoice 1023456 not found in accessible services")
    
    else:
        print(f"\n❌ AUTHENTICATION FAILED")
        print("💡 Possible issues:")
        print("   • Password might be different")
        print("   • User might be locked")
        print("   • System might require different auth method")
        print("   • Client/system configuration issue")

if __name__ == "__main__":
    main()
