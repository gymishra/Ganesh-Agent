#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import re

class EnhancedSAPConnector:
    """Enhanced SAP system connector with better error handling"""
    
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
            'Accept': 'application/json, application/xml, text/html, */*',
            'Content-Type': 'application/json',
            'User-Agent': 'SAP-OData-Discovery-Tool/1.0',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()
        
    def comprehensive_connection_test(self):
        """Comprehensive connection testing with multiple approaches"""
        
        print(f"🔗 Comprehensive Connection Test")
        print(f"🌐 Target: {self.base_url}")
        print(f"👤 User: {self.username}")
        print("-" * 60)
        
        # Test different endpoints
        test_endpoints = [
            '',  # Root
            '/',
            '/sap/',
            '/sap/bc/',
            '/sap/bc/gui/sap/its/webgui',
            '/sap/bc/webdynpro/',
            '/sap/opu/',
            '/sap/opu/odata/',
            '/irj/portal',
            '/webdynpro/',
            '/sap/public/ping'
        ]
        
        successful_endpoints = []
        
        for endpoint in test_endpoints:
            try:
                url = urljoin(self.base_url, endpoint) if endpoint else self.base_url
                print(f"🔍 Testing: {url}")
                
                response = self.session.get(
                    url, 
                    verify=False, 
                    timeout=30,
                    allow_redirects=True
                )
                
                print(f"   📊 Status: {response.status_code}")
                print(f"   📏 Size: {len(response.content)} bytes")
                
                # Check for SAP-specific content
                content_lower = response.text.lower()
                sap_indicators = ['sap', 'netweaver', 'webdynpro', 'odata', 'fiori']
                found_indicators = [ind for ind in sap_indicators if ind in content_lower]
                
                if found_indicators:
                    print(f"   ✅ SAP indicators found: {found_indicators}")
                
                # Check response headers for SAP info
                sap_headers = {k: v for k, v in response.headers.items() 
                             if 'sap' in k.lower() or 'server' in k.lower()}
                if sap_headers:
                    print(f"   📋 Relevant headers: {sap_headers}")
                
                # Store successful responses
                if response.status_code in [200, 302, 401]:  # 401 means auth required but endpoint exists
                    successful_endpoints.append({
                        'endpoint': endpoint,
                        'url': url,
                        'status': response.status_code,
                        'size': len(response.content),
                        'content_type': response.headers.get('content-type', ''),
                        'sap_indicators': found_indicators,
                        'headers': dict(response.headers)
                    })
                
                # Show snippet of response for analysis
                if response.status_code == 200 and len(response.text) > 0:
                    snippet = response.text[:200].replace('\\n', ' ').replace('\\r', '')
                    print(f"   📝 Content snippet: {snippet}...")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                print()
        
        return successful_endpoints
    
    def discover_odata_endpoints(self):
        """Discover OData service endpoints"""
        
        print(f"🔍 OData Service Discovery")
        print("-" * 60)
        
        # Common OData paths in SAP systems
        odata_paths = [
            '/sap/opu/odata/',
            '/sap/opu/odata/sap/',
            '/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/',
            '/sap/opu/odata/iwfnd/catalogservice;v=2/',
            '/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection',
            '/sap/bc/rest/slc/odata/',
            '/gateway/odata/',
            '/odata/',
            '/services/'
        ]
        
        odata_services = []
        
        for path in odata_paths:
            try:
                url = urljoin(self.base_url, path)
                print(f"🔍 Checking OData path: {path}")
                
                response = self.session.get(
                    url, 
                    verify=False, 
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ OData endpoint found!")
                    
                    # Analyze content
                    content_type = response.headers.get('content-type', '').lower()
                    print(f"   📋 Content-Type: {content_type}")
                    
                    # Try to extract service information
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   📊 JSON response with {len(str(data))} characters")
                            odata_services.append({
                                'path': path,
                                'type': 'json',
                                'data': data,
                                'url': url
                            })
                        except Exception as e:
                            print(f"   ⚠️ JSON parse error: {str(e)}")
                    
                    elif 'xml' in content_type:
                        try:
                            root = ET.fromstring(response.content)
                            print(f"   📊 XML response parsed successfully")
                            odata_services.append({
                                'path': path,
                                'type': 'xml',
                                'data': root,
                                'url': url
                            })
                        except Exception as e:
                            print(f"   ⚠️ XML parse error: {str(e)}")
                    
                    # Look for service links in HTML
                    if 'html' in content_type:
                        service_links = re.findall(r'href=["\']([^"\']*(?:odata|service)[^"\']*)["\']', 
                                                 response.text, re.IGNORECASE)
                        if service_links:
                            print(f"   🔗 Found {len(service_links)} service links")
                            for link in service_links[:5]:  # Show first 5
                                print(f"      • {link}")
                
                elif response.status_code == 401:
                    print(f"   🔐 Authentication required (endpoint exists)")
                elif response.status_code == 404:
                    print(f"   ❌ Not found")
                else:
                    print(f"   ⚠️ Unexpected status: {response.status_code}")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                print()
        
        return odata_services
    
    def search_specific_services(self):
        """Search for specific SAP services"""
        
        print(f"🎯 Searching for Specific SAP Services")
        print("-" * 60)
        
        # Known SAP OData services
        known_services = [
            'API_SALES_ORDER_SRV',
            'API_BUSINESS_PARTNER',
            'API_CUSTOMER_MASTER_SRV',
            'API_PRODUCT_SRV',
            'API_MATERIAL_DOCUMENT_SRV',
            'SALESORDER_SRV',
            'CUSTOMER_SRV',
            'PRODUCT_SRV',
            'ZSD_SALES_ORDER_SRV',  # Custom service example
            'ZGWSAMPLE_BASIC'  # Gateway sample service
        ]
        
        found_services = []
        
        for service in known_services:
            service_paths = [
                f'/sap/opu/odata/sap/{service}/',
                f'/sap/opu/odata/sap/{service}/$metadata',
                f'/sap/opu/odata/{service}/',
                f'/gateway/odata/{service}/'
            ]
            
            print(f"🔍 Searching for: {service}")
            
            for path in service_paths:
                try:
                    url = urljoin(self.base_url, path)
                    
                    response = self.session.get(
                        url, 
                        verify=False, 
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Found at: {path}")
                        found_services.append({
                            'service': service,
                            'path': path,
                            'url': url,
                            'status': response.status_code,
                            'content_type': response.headers.get('content-type', ''),
                            'size': len(response.content)
                        })
                        break
                    elif response.status_code == 401:
                        print(f"   🔐 Auth required at: {path}")
                        found_services.append({
                            'service': service,
                            'path': path,
                            'url': url,
                            'status': response.status_code,
                            'auth_required': True
                        })
                        break
                        
                except Exception as e:
                    continue  # Try next path
            
            if not any(s['service'] == service for s in found_services):
                print(f"   ❌ Not found: {service}")
            
            print()
        
        return found_services
    
    def analyze_response_content(self, response):
        """Analyze response content for useful information"""
        
        content = response.text
        
        # Look for common SAP patterns
        patterns = {
            'sap_system': r'SAP\s+(\w+)',
            'version': r'version[:\s]+([0-9\.]+)',
            'services': r'service[s]?["\s]*:["\s]*([^"\'<>\s]+)',
            'odata_links': r'href=["\']([^"\']*odata[^"\']*)["\']',
            'metadata_links': r'href=["\']([^"\']*metadata[^"\']*)["\']'
        }
        
        findings = {}
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                findings[pattern_name] = matches[:10]  # Limit to first 10 matches
        
        return findings

def main():
    """Main function"""
    
    # SAP system details
    sap_url = "https://vhcals4hci.awspoc.club/"
    username = "bpinst"
    password = "welcome1"
    
    print("🚀 Enhanced SAP System Analysis Tool")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 SAP System: {sap_url}")
    print(f"👤 User: {username}")
    print()
    
    # Initialize connector
    connector = EnhancedSAPConnector(sap_url, username, password)
    
    # Comprehensive connection test
    successful_endpoints = connector.comprehensive_connection_test()
    
    # Discover OData services
    odata_services = connector.discover_odata_endpoints()
    
    # Search for specific services
    specific_services = connector.search_specific_services()
    
    # Final summary
    print(f"📊 ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"✅ Accessible endpoints: {len(successful_endpoints)}")
    print(f"🔍 OData endpoints found: {len(odata_services)}")
    print(f"🎯 Specific services found: {len(specific_services)}")
    
    if successful_endpoints:
        print(f"\n🌐 ACCESSIBLE ENDPOINTS:")
        for endpoint in successful_endpoints[:5]:  # Show top 5
            print(f"   • {endpoint['endpoint']} (Status: {endpoint['status']})")
            if endpoint['sap_indicators']:
                print(f"     SAP indicators: {endpoint['sap_indicators']}")
    
    if odata_services:
        print(f"\n🔍 ODATA SERVICES:")
        for service in odata_services:
            print(f"   • {service['path']} ({service['type']})")
    
    if specific_services:
        print(f"\n🎯 SPECIFIC SERVICES FOUND:")
        for service in specific_services:
            status_text = f"Status: {service['status']}"
            if service.get('auth_required'):
                status_text += " (Auth Required)"
            print(f"   • {service['service']} - {service['path']}")
            print(f"     {status_text}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if successful_endpoints:
        print(f"   ✅ System is accessible - try different authentication methods")
        print(f"   ✅ Look for Fiori Launchpad or WebGUI access")
    
    if not odata_services and not specific_services:
        print(f"   🔍 Try accessing the system through a web browser first")
        print(f"   🔍 Check if OData services need to be activated")
        print(f"   🔍 Verify user permissions for OData access")
    
    return {
        'accessible_endpoints': successful_endpoints,
        'odata_services': odata_services,
        'specific_services': specific_services
    }

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n✅ Analysis completed!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
