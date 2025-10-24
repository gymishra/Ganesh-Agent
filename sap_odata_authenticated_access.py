#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

class SAPODataAuthenticatedAccess:
    """Access SAP OData services with proper authentication"""
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        
        # Setup authentication
        auth_string = f"{username}:{password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json, application/xml',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': 'Fetch'  # Important for SAP systems
        })
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()
        
        # Get CSRF token
        self.csrf_token = self.get_csrf_token()
    
    def get_csrf_token(self):
        """Get CSRF token for SAP system"""
        
        try:
            print("🔐 Getting CSRF token...")
            
            # Try to get CSRF token from OData service
            response = self.session.get(
                f"{self.base_url}/sap/opu/odata/",
                verify=False,
                timeout=30
            )
            
            csrf_token = response.headers.get('x-csrf-token')
            if csrf_token:
                print(f"✅ CSRF token obtained: {csrf_token[:20]}...")
                self.session.headers['X-CSRF-Token'] = csrf_token
                return csrf_token
            else:
                print("⚠️ No CSRF token in response")
                return None
                
        except Exception as e:
            print(f"⚠️ Could not get CSRF token: {str(e)}")
            return None
    
    def get_service_catalog(self):
        """Get the OData service catalog"""
        
        print("📋 Fetching OData Service Catalog...")
        print("-" * 50)
        
        catalog_urls = [
            '/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection',
            '/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection',
            '/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/',
            '/sap/opu/odata/'
        ]
        
        for catalog_url in catalog_urls:
            try:
                url = urljoin(self.base_url, catalog_url)
                print(f"🔍 Trying catalog: {catalog_url}")
                
                response = self.session.get(
                    url,
                    verify=False,
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Catalog accessed successfully!")
                    
                    # Try to parse as JSON first
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            return self.parse_json_catalog(data)
                        except:
                            pass
                    
                    # Try to parse as XML
                    if 'xml' in content_type or 'atom' in content_type:
                        try:
                            return self.parse_xml_catalog(response.content)
                        except Exception as e:
                            print(f"   ⚠️ XML parsing error: {str(e)}")
                    
                    # If neither, return raw content for analysis
                    return {
                        'type': 'raw',
                        'content': response.text[:2000],  # First 2000 chars
                        'url': url
                    }
                
                elif response.status_code == 401:
                    print("   🔐 Authentication failed")
                elif response.status_code == 403:
                    print("   🚫 Access forbidden")
                else:
                    print(f"   ⚠️ Unexpected status: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return None
    
    def parse_json_catalog(self, data):
        """Parse JSON service catalog"""
        
        print("📊 Parsing JSON catalog...")
        
        services = []
        
        # Handle different JSON structures
        if isinstance(data, dict):
            if 'd' in data and 'results' in data['d']:
                # Standard OData JSON format
                for service in data['d']['results']:
                    services.append({
                        'id': service.get('ID', ''),
                        'title': service.get('Title', ''),
                        'description': service.get('Description', ''),
                        'url': service.get('TechnicalServiceName', '')
                    })
            elif 'value' in data:
                # OData v4 format
                for service in data['value']:
                    services.append({
                        'id': service.get('ID', ''),
                        'title': service.get('Title', ''),
                        'description': service.get('Description', ''),
                        'url': service.get('name', '')
                    })
        
        return {
            'type': 'json',
            'services': services,
            'total': len(services)
        }
    
    def parse_xml_catalog(self, xml_content):
        """Parse XML service catalog"""
        
        print("📊 Parsing XML catalog...")
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
                'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
            }
            
            services = []
            
            # Look for entry elements
            entries = root.findall('.//atom:entry', namespaces)
            
            for entry in entries:
                service_info = {}
                
                # Get title
                title_elem = entry.find('atom:title', namespaces)
                if title_elem is not None:
                    service_info['title'] = title_elem.text
                
                # Get content/properties
                content = entry.find('.//atom:content', namespaces)
                if content is not None:
                    props = content.find('.//m:properties', namespaces)
                    if props is not None:
                        for prop in props:
                            tag_name = prop.tag.split('}')[-1]  # Remove namespace
                            service_info[tag_name.lower()] = prop.text
                
                if service_info:
                    services.append(service_info)
            
            return {
                'type': 'xml',
                'services': services,
                'total': len(services)
            }
            
        except Exception as e:
            print(f"❌ XML parsing error: {str(e)}")
            return None
    
    def get_specific_service_metadata(self, service_name):
        """Get metadata for a specific service"""
        
        print(f"📋 Getting metadata for: {service_name}")
        
        try:
            metadata_url = f"{self.base_url}/sap/opu/odata/sap/{service_name}/$metadata"
            
            response = self.session.get(
                metadata_url,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Metadata retrieved successfully!")
                
                # Parse XML metadata
                try:
                    root = ET.fromstring(response.content)
                    
                    # Extract entity sets
                    entity_sets = []
                    for elem in root.iter():
                        if 'EntitySet' in elem.tag:
                            name = elem.get('Name')
                            entity_type = elem.get('EntityType')
                            if name:
                                entity_sets.append({
                                    'name': name,
                                    'entity_type': entity_type
                                })
                    
                    return {
                        'service': service_name,
                        'entity_sets': entity_sets,
                        'metadata_url': metadata_url,
                        'raw_metadata': response.text[:1000]  # First 1000 chars
                    }
                    
                except Exception as e:
                    print(f"⚠️ Metadata parsing error: {str(e)}")
                    return {
                        'service': service_name,
                        'raw_metadata': response.text[:1000]
                    }
            
            else:
                print(f"❌ Failed to get metadata: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting metadata: {str(e)}")
            return None
    
    def test_sales_order_services(self):
        """Test specific sales order services"""
        
        print("🎯 Testing Sales Order Services")
        print("-" * 50)
        
        sales_services = [
            'API_SALES_ORDER_SRV',
            'SALESORDER_SRV',
            'ZSD_SALES_ORDER_SRV',
            'API_BUSINESS_PARTNER',
            'API_CUSTOMER_MASTER_SRV',
            'API_PRODUCT_SRV'
        ]
        
        working_services = []
        
        for service in sales_services:
            print(f"\n🔍 Testing: {service}")
            
            # Test service root
            service_url = f"{self.base_url}/sap/opu/odata/sap/{service}/"
            
            try:
                response = self.session.get(
                    service_url,
                    verify=False,
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Service accessible!")
                    
                    # Get metadata
                    metadata = self.get_specific_service_metadata(service)
                    
                    working_services.append({
                        'service': service,
                        'url': service_url,
                        'metadata': metadata
                    })
                
                elif response.status_code == 401:
                    print(f"   🔐 Authentication issue")
                elif response.status_code == 403:
                    print(f"   🚫 Access forbidden")
                else:
                    print(f"   ⚠️ Status: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return working_services

def main():
    """Main function"""
    
    # SAP system details
    sap_url = "https://vhcals4hci.awspoc.club/"
    username = "bpinst"
    password = "welcome1"
    
    print("🚀 SAP OData Authenticated Access Tool")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 SAP System: {sap_url}")
    print(f"👤 User: {username}")
    print()
    
    # Initialize authenticated access
    sap_access = SAPODataAuthenticatedAccess(sap_url, username, password)
    
    # Get service catalog
    catalog = sap_access.get_service_catalog()
    
    if catalog:
        print(f"\n📊 SERVICE CATALOG RESULTS:")
        print(f"   Type: {catalog['type']}")
        
        if 'services' in catalog:
            print(f"   Total services: {catalog['total']}")
            
            # Show first 10 services
            for i, service in enumerate(catalog['services'][:10], 1):
                title = service.get('title', 'No title')
                service_id = service.get('id', service.get('url', 'No ID'))
                print(f"   {i:2d}. {title} ({service_id})")
        
        elif 'content' in catalog:
            print(f"   Raw content preview:")
            print(f"   {catalog['content'][:200]}...")
    
    # Test sales order services
    working_services = sap_access.test_sales_order_services()
    
    # Summary
    print(f"\n📊 FINAL SUMMARY")
    print("=" * 60)
    
    if catalog:
        print(f"✅ Service catalog: Accessible")
    else:
        print(f"❌ Service catalog: Not accessible")
    
    print(f"🎯 Working sales services: {len(working_services)}")
    
    if working_services:
        print(f"\n🏆 WORKING SERVICES FOR SALES ORDERS:")
        for service in working_services:
            print(f"   • {service['service']}")
            if service['metadata'] and 'entity_sets' in service['metadata']:
                entity_count = len(service['metadata']['entity_sets'])
                print(f"     Entities: {entity_count}")
    
    # Provide practical guidance
    print(f"\n💡 FOR SALES ORDER CREATION:")
    print(f"   1. 🎯 Primary: API_SALES_ORDER_SRV")
    print(f"      URL: {sap_url}sap/opu/odata/sap/API_SALES_ORDER_SRV/")
    print(f"   2. 👤 Customer: API_BUSINESS_PARTNER")
    print(f"      URL: {sap_url}sap/opu/odata/sap/API_BUSINESS_PARTNER/")
    print(f"   3. 📦 Product: API_PRODUCT_SRV")
    print(f"      URL: {sap_url}sap/opu/odata/sap/API_PRODUCT_SRV/")
    
    return {
        'catalog': catalog,
        'working_services': working_services
    }

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
