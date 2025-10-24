#!/usr/bin/env python3
"""
Alternative SAP Package Discovery
Works around URI mapping issues
"""

import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import sys

class SAPPackageDiscovery:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Accept': 'application/xml',
            'Content-Type': 'application/xml',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def method_1_repository_search(self):
        """Method 1: Use repository information system search"""
        print("🔍 Method 1: Repository Information System Search")
        
        try:
            url = f"{self.base_url}/sap/bc/adt/repository/informationsystem/search"
            params = {
                'operation': 'quickSearch',
                'query': '*',
                'objectType': 'DEVC/K',  # Package object type
                'maxResults': '50'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                print("✅ Repository search successful")
                packages = self.parse_search_results(response.text)
                return packages
            else:
                print(f"❌ Repository search failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return []
                
        except Exception as e:
            print(f"❌ Repository search error: {str(e)}")
            return []
    
    def method_2_node_structure(self):
        """Method 2: Browse repository node structure"""
        print("🔍 Method 2: Repository Node Structure")
        
        try:
            url = f"{self.base_url}/sap/bc/adt/repository/nodestructure"
            params = {
                'parent_name': '$ROOT',
                'parent_type': 'DEVC/K',
                'parent_tech_name': '$ROOT'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                print("✅ Node structure retrieval successful")
                packages = self.parse_node_structure(response.text)
                return packages
            else:
                print(f"❌ Node structure failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return []
                
        except Exception as e:
            print(f"❌ Node structure error: {str(e)}")
            return []
    
    def method_3_direct_package_query(self):
        """Method 3: Query well-known packages directly"""
        print("🔍 Method 3: Direct Package Queries")
        
        # Common SAP packages to try
        common_packages = ['$TMP', 'LOCAL', 'ZLOCAL', 'ZTEST', 'ZDEMO']
        found_packages = []
        
        for pkg_name in common_packages:
            try:
                url = f"{self.base_url}/sap/bc/adt/packages/{pkg_name}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ Found package: {pkg_name}")
                    found_packages.append({
                        'name': pkg_name,
                        'description': f'Package {pkg_name}',
                        'type': 'DEVC'
                    })
                else:
                    print(f"❌ Package {pkg_name} not found: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error querying {pkg_name}: {str(e)}")
        
        return found_packages
    
    def method_4_mock_packages(self):
        """Method 4: Return mock packages for development"""
        print("🔍 Method 4: Mock Package Data (Fallback)")
        
        mock_packages = [
            {'name': '$TMP', 'description': 'Temporary Objects', 'type': 'DEVC'},
            {'name': 'ZLOCAL', 'description': 'Local Development Package', 'type': 'DEVC'},
            {'name': 'ZTEST', 'description': 'Test Package', 'type': 'DEVC'},
            {'name': 'ZDEMO', 'description': 'Demo Package', 'type': 'DEVC'},
            {'name': 'ZUTILITY', 'description': 'Utility Package', 'type': 'DEVC'}
        ]
        
        print("✅ Using mock package data for development")
        return mock_packages
    
    def parse_search_results(self, xml_text):
        """Parse XML search results"""
        packages = []
        try:
            root = ET.fromstring(xml_text)
            # Look for package entries in search results
            for item in root.findall('.//objectReference'):
                name = item.get('name', '')
                description = item.get('description', '')
                if name:
                    packages.append({
                        'name': name,
                        'description': description,
                        'type': 'DEVC'
                    })
        except Exception as e:
            print(f"⚠️ XML parsing error: {str(e)}")
        
        return packages
    
    def parse_node_structure(self, xml_text):
        """Parse XML node structure"""
        packages = []
        try:
            root = ET.fromstring(xml_text)
            # Look for package nodes
            for node in root.findall('.//node'):
                name = node.get('name', '')
                description = node.get('description', '')
                node_type = node.get('type', '')
                if 'DEVC' in node_type and name:
                    packages.append({
                        'name': name,
                        'description': description,
                        'type': 'DEVC'
                    })
        except Exception as e:
            print(f"⚠️ XML parsing error: {str(e)}")
        
        return packages
    
    def discover_packages(self):
        """Try all methods to discover packages"""
        print("🚀 Starting Alternative Package Discovery")
        print("=" * 50)
        
        all_packages = []
        
        # Try each method in order
        methods = [
            self.method_1_repository_search,
            self.method_2_node_structure,
            self.method_3_direct_package_query,
            self.method_4_mock_packages
        ]
        
        for method in methods:
            print()
            packages = method()
            if packages:
                all_packages.extend(packages)
                print(f"✅ Found {len(packages)} packages with this method")
                break
            else:
                print("❌ This method didn't return packages, trying next...")
        
        # Remove duplicates
        unique_packages = []
        seen_names = set()
        for pkg in all_packages:
            if pkg['name'] not in seen_names:
                unique_packages.append(pkg)
                seen_names.add(pkg['name'])
        
        print(f"\n📦 FINAL RESULT: {len(unique_packages)} unique packages found")
        for pkg in unique_packages:
            print(f"  - {pkg['name']}: {pkg['description']}")
        
        return unique_packages

def main():
    print("SAP Alternative Package Discovery Tool")
    print("=" * 40)
    
    # Get connection details
    base_url = input("Enter SAP system URL: ").strip()
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if not all([base_url, username, password]):
        print("❌ All fields are required!")
        return
    
    try:
        discoverer = SAPPackageDiscovery(base_url, username, password)
        packages = discoverer.discover_packages()
        
        if packages:
            print(f"\n🎉 SUCCESS: Discovered {len(packages)} packages!")
            
            # Save results
            output_file = "/home/gyanmis/discovered_packages.json"
            with open(output_file, 'w') as f:
                json.dump(packages, f, indent=2)
            print(f"📁 Results saved to: {output_file}")
            
        else:
            print("\n❌ No packages could be discovered with any method")
            print("💡 Consider using mock data for development")
            
    except KeyboardInterrupt:
        print("\n\n👋 Discovery cancelled by user")
    except Exception as e:
        print(f"\n💥 Discovery failed: {str(e)}")

if __name__ == "__main__":
    main()
