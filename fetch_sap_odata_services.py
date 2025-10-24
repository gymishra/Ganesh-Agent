#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

class SAPODataFetcher:
    """Fetch OData services from SAP system"""
    
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
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Disable SSL warnings for demo
        requests.packages.urllib3.disable_warnings()
        
    def test_connection(self):
        """Test connection to SAP system"""
        
        print(f"🔗 Testing connection to: {self.base_url}")
        print(f"👤 Username: {self.username}")
        print("-" * 50)
        
        try:
            # Try to access the main page
            response = self.session.get(
                self.base_url, 
                verify=False, 
                timeout=30
            )
            
            print(f"✅ Connection Status: {response.status_code}")
            print(f"📊 Response Size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print("✅ Successfully connected to SAP system!")
                return True
            else:
                print(f"⚠️ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def discover_odata_services(self):
        """Discover available OData services"""
        
        print(f"\n🔍 Discovering OData Services...")
        print("-" * 50)
        
        # Common OData service discovery endpoints
        discovery_paths = [
            '/sap/opu/odata/',
            '/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/',
            '/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection',
            '/sap/bc/rest/slc/odata/',
            '/sap/opu/odata/sap/'
        ]
        
        services_found = []
        
        for path in discovery_paths:
            try:
                url = urljoin(self.base_url, path)
                print(f"🔍 Trying: {url}")
                
                response = self.session.get(
                    url, 
                    verify=False, 
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Found services at: {path}")
                    
                    # Try to parse the response
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            services_found.append({
                                'path': path,
                                'type': 'json',
                                'data': data,
                                'content': response.text[:500]
                            })
                        except:
                            pass
                    
                    elif 'xml' in content_type:
                        try:
                            # Parse XML response
                            root = ET.fromstring(response.content)
                            services_found.append({
                                'path': path,
                                'type': 'xml',
                                'data': root,
                                'content': response.text[:500]
                            })
                        except:
                            pass
                    
                    else:
                        # HTML or other content
                        services_found.append({
                            'path': path,
                            'type': 'html',
                            'data': None,
                            'content': response.text[:500]
                        })
                
                elif response.status_code == 401:
                    print(f"   🔐 Authentication required")
                elif response.status_code == 404:
                    print(f"   ❌ Not found")
                else:
                    print(f"   ⚠️ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return services_found
    
    def search_sales_order_services(self):
        """Search for sales order related services"""
        
        print(f"\n🎯 Searching for Sales Order Services...")
        print("-" * 50)
        
        # Common SAP sales order service patterns
        sales_service_patterns = [
            'API_SALES_ORDER_SRV',
            'SALESORDER',
            'SALES_ORDER',
            'SD_ORDER',
            'ORDER_SRV',
            'QUOTATION',
            'CUSTOMER',
            'BUSINESS_PARTNER'
        ]
        
        found_services = []
        
        for pattern in sales_service_patterns:
            try:
                # Try different URL patterns
                service_urls = [
                    f'/sap/opu/odata/sap/{pattern}/',
                    f'/sap/opu/odata/sap/{pattern}/$metadata',
                    f'/sap/opu/odata/{pattern}/',
                    f'/sap/bc/rest/sap/{pattern}/'
                ]
                
                for service_url in service_urls:
                    try:
                        url = urljoin(self.base_url, service_url)
                        print(f"🔍 Checking: {pattern} at {service_url}")
                        
                        response = self.session.get(
                            url, 
                            verify=False, 
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            print(f"   ✅ Found: {pattern}")
                            found_services.append({
                                'service': pattern,
                                'url': service_url,
                                'status': response.status_code,
                                'content_type': response.headers.get('content-type', ''),
                                'size': len(response.content)
                            })
                            break  # Found this service, move to next pattern
                        
                        elif response.status_code == 401:
                            print(f"   🔐 Authentication issue for {pattern}")
                        elif response.status_code == 404:
                            print(f"   ❌ Not found: {pattern}")
                        else:
                            print(f"   ⚠️ Status {response.status_code}: {pattern}")
                            
                    except Exception as e:
                        print(f"   ❌ Error checking {pattern}: {str(e)}")
                        
            except Exception as e:
                print(f"❌ Error with pattern {pattern}: {str(e)}")
        
        return found_services
    
    def get_service_metadata(self, service_path):
        """Get metadata for a specific service"""
        
        try:
            metadata_url = urljoin(self.base_url, f"{service_path}/$metadata")
            print(f"📋 Getting metadata: {metadata_url}")
            
            response = self.session.get(
                metadata_url, 
                verify=False, 
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'url': metadata_url,
                    'content': response.text,
                    'content_type': response.headers.get('content-type', '')
                }
            else:
                print(f"⚠️ Metadata request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting metadata: {str(e)}")
            return None
    
    def analyze_system_info(self):
        """Try to get system information"""
        
        print(f"\n📊 Analyzing SAP System Information...")
        print("-" * 50)
        
        info_endpoints = [
            '/sap/bc/ping',
            '/sap/public/ping',
            '/sap/bc/webdynpro/sap/wda_analyze_config_user',
            '/',
            '/sap/'
        ]
        
        system_info = {}
        
        for endpoint in info_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                print(f"🔍 Checking: {endpoint}")
                
                response = self.session.get(
                    url, 
                    verify=False, 
                    timeout=15
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    system_info[endpoint] = {
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'size': len(response.content),
                        'headers': dict(response.headers)
                    }
                    
                    # Look for SAP-specific headers
                    sap_headers = {k: v for k, v in response.headers.items() 
                                 if 'sap' in k.lower()}
                    if sap_headers:
                        print(f"   📋 SAP Headers: {sap_headers}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return system_info

def main():
    """Main function"""
    
    # SAP system details
    sap_url = "https://vhcals4hci.awspoc.club/"
    username = "bpinst"
    password = "welcome1"
    
    print("🚀 SAP OData Service Discovery Tool")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 SAP System: {sap_url}")
    print(f"👤 User: {username}")
    print()
    
    # Initialize fetcher
    fetcher = SAPODataFetcher(sap_url, username, password)
    
    # Test connection
    if not fetcher.test_connection():
        print("❌ Cannot proceed without connection. Please check:")
        print("   • URL is accessible")
        print("   • Credentials are correct")
        print("   • Network connectivity")
        sys.exit(1)
    
    # Analyze system
    system_info = fetcher.analyze_system_info()
    
    # Discover OData services
    discovered_services = fetcher.discover_odata_services()
    
    # Search for sales order services
    sales_services = fetcher.search_sales_order_services()
    
    # Summary
    print(f"\n📊 DISCOVERY SUMMARY")
    print("=" * 60)
    print(f"✅ Connection: Successful")
    print(f"📋 Discovery endpoints checked: {len(discovered_services)}")
    print(f"🎯 Sales-related services found: {len(sales_services)}")
    
    if sales_services:
        print(f"\n🏆 SALES ORDER SERVICES FOUND:")
        for service in sales_services:
            print(f"   • {service['service']} - {service['url']}")
            print(f"     Status: {service['status']}, Size: {service['size']} bytes")
    
    if discovered_services:
        print(f"\n🔍 GENERAL SERVICES DISCOVERED:")
        for service in discovered_services:
            print(f"   • {service['path']} ({service['type']})")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Use the found services for sales order creation")
    print(f"   2. Get detailed metadata for specific services")
    print(f"   3. Test actual OData operations")
    
    return {
        'connection': True,
        'system_info': system_info,
        'discovered_services': discovered_services,
        'sales_services': sales_services
    }

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n✅ Discovery completed successfully!")
    except Exception as e:
        print(f"\n❌ Discovery failed: {str(e)}")
        sys.exit(1)
