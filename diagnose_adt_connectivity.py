#!/usr/bin/env python3
"""
SAP ADT Connectivity Diagnostic Tool
Helps troubleshoot URI mapping errors
"""

import requests
import json
from urllib.parse import urljoin
import sys

def test_adt_endpoints(base_url, username, password):
    """Test various ADT endpoints to diagnose connectivity issues"""
    
    print("🔍 SAP ADT Connectivity Diagnostic")
    print("=" * 50)
    
    # Common ADT endpoints to test
    endpoints = [
        "/sap/bc/adt/discovery",           # ADT Discovery
        "/sap/bc/adt/packages",            # Packages (the failing one)
        "/sap/bc/adt/repository/nodestructure", # Repository structure
        "/sap/bc/adt/programs",            # Programs
        "/sap/bc/adt/classes",             # Classes
        "/sap/bc/adt/compatibility/graph", # Compatibility
        "/sap/bc/adt/repository/informationsystem/search", # Search
    ]
    
    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'Accept': 'application/xml',
        'Content-Type': 'application/xml',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    print(f"🌐 Testing SAP System: {base_url}")
    print(f"👤 Username: {username}")
    print()
    
    results = {}
    
    for endpoint in endpoints:
        full_url = urljoin(base_url, endpoint)
        print(f"Testing: {endpoint}")
        
        try:
            response = session.get(full_url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ Status: {response.status_code} - OK")
                results[endpoint] = "SUCCESS"
            elif response.status_code == 401:
                print(f"  🔐 Status: {response.status_code} - Authentication required")
                results[endpoint] = "AUTH_ERROR"
            elif response.status_code == 404:
                print(f"  ❌ Status: {response.status_code} - Endpoint not found")
                results[endpoint] = "NOT_FOUND"
            elif response.status_code == 400:
                print(f"  ⚠️  Status: {response.status_code} - Bad request (URI mapping issue)")
                print(f"     Response: {response.text[:200]}...")
                results[endpoint] = "URI_MAPPING_ERROR"
            else:
                print(f"  ❓ Status: {response.status_code} - {response.reason}")
                results[endpoint] = f"ERROR_{response.status_code}"
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout - Endpoint not responding")
            results[endpoint] = "TIMEOUT"
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection Error - Cannot reach endpoint")
            results[endpoint] = "CONNECTION_ERROR"
        except Exception as e:
            print(f"  💥 Error: {str(e)}")
            results[endpoint] = f"ERROR: {str(e)}"
        
        print()
    
    # Summary
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    success_count = sum(1 for r in results.values() if r == "SUCCESS")
    total_count = len(results)
    
    print(f"✅ Successful endpoints: {success_count}/{total_count}")
    
    if results.get("/sap/bc/adt/packages") == "URI_MAPPING_ERROR":
        print("\n🎯 SPECIFIC ISSUE FOUND:")
        print("The /sap/bc/adt/packages endpoint has URI mapping issues.")
        print("\n💡 SOLUTIONS:")
        print("1. Check if ADT is properly activated in your SAP system")
        print("2. Verify the SAP system supports ADT (NetWeaver 7.31+)")
        print("3. Check transaction SICF for ADT services activation")
        print("4. Try alternative package discovery methods")
        
    elif results.get("/sap/bc/adt/discovery") != "SUCCESS":
        print("\n🎯 ROOT CAUSE FOUND:")
        print("ADT Discovery service is not working - ADT may not be activated")
        print("\n💡 SOLUTIONS:")
        print("1. Activate ADT in SAP system (transaction SICF)")
        print("2. Check SAP system version (requires NetWeaver 7.31+)")
        print("3. Verify user has ADT authorization")
        
    else:
        print("\n✅ ADT connectivity looks good!")
        print("The issue might be with specific package queries.")
    
    return results

def suggest_alternative_package_discovery():
    """Suggest alternative methods for package discovery"""
    
    print("\n🔄 ALTERNATIVE PACKAGE DISCOVERY METHODS")
    print("=" * 50)
    
    alternatives = [
        {
            "method": "Repository Information System",
            "endpoint": "/sap/bc/adt/repository/informationsystem/search",
            "description": "Use search-based package discovery"
        },
        {
            "method": "Node Structure",
            "endpoint": "/sap/bc/adt/repository/nodestructure",
            "description": "Browse repository structure hierarchically"
        },
        {
            "method": "Direct Package Query",
            "endpoint": "/sap/bc/adt/packages/{package_name}",
            "description": "Query specific packages directly"
        },
        {
            "method": "RFC-based Discovery",
            "endpoint": "RFC calls (non-ADT)",
            "description": "Use traditional RFC calls for package info"
        }
    ]
    
    for i, alt in enumerate(alternatives, 1):
        print(f"{i}. {alt['method']}")
        print(f"   Endpoint: {alt['endpoint']}")
        print(f"   Description: {alt['description']}")
        print()

if __name__ == "__main__":
    print("SAP ADT Connectivity Diagnostic Tool")
    print("=" * 40)
    
    # Example usage - replace with your actual values
    base_url = input("Enter SAP system URL (e.g., https://your-sap-system:8000): ").strip()
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if not all([base_url, username, password]):
        print("❌ All fields are required!")
        sys.exit(1)
    
    try:
        results = test_adt_endpoints(base_url, username, password)
        suggest_alternative_package_discovery()
        
        print("\n📝 NEXT STEPS:")
        print("1. Share these results with your SAP system administrator")
        print("2. Check SAP system ADT activation status")
        print("3. Try alternative package discovery methods")
        print("4. Verify user authorizations for ADT access")
        
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n💥 Diagnostic failed: {str(e)}")
