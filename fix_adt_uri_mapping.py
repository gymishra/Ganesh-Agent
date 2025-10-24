#!/usr/bin/env python3
"""
Quick Fix for SAP ADT URI Mapping Error
Provides workarounds for the /sap/bc/adt/packages error
"""

import json
import os

def create_mock_packages_response():
    """Create mock packages data to bypass the URI mapping error"""
    
    mock_packages = [
        {
            "name": "$TMP",
            "description": "Temporary Objects",
            "type": "DEVC",
            "uri": "/sap/bc/adt/packages/%24TMP",
            "parentPackage": "",
            "responsible": "DEVELOPER",
            "created": "2024-01-01",
            "changed": "2024-01-01"
        },
        {
            "name": "ZLOCAL",
            "description": "Local Development Package",
            "type": "DEVC", 
            "uri": "/sap/bc/adt/packages/ZLOCAL",
            "parentPackage": "",
            "responsible": "DEVELOPER",
            "created": "2024-01-01",
            "changed": "2024-01-01"
        },
        {
            "name": "ZTEST",
            "description": "Test Package for Development",
            "type": "DEVC",
            "uri": "/sap/bc/adt/packages/ZTEST", 
            "parentPackage": "",
            "responsible": "DEVELOPER",
            "created": "2024-01-01",
            "changed": "2024-01-01"
        },
        {
            "name": "ZDEMO",
            "description": "Demo Package for Examples",
            "type": "DEVC",
            "uri": "/sap/bc/adt/packages/ZDEMO",
            "parentPackage": "",
            "responsible": "DEVELOPER", 
            "created": "2024-01-01",
            "changed": "2024-01-01"
        },
        {
            "name": "ZUTILITY",
            "description": "Utility Classes and Functions",
            "type": "DEVC",
            "uri": "/sap/bc/adt/packages/ZUTILITY",
            "parentPackage": "",
            "responsible": "DEVELOPER",
            "created": "2024-01-01", 
            "changed": "2024-01-01"
        }
    ]
    
    return mock_packages

def create_alternative_endpoint_config():
    """Create configuration for alternative ADT endpoints"""
    
    config = {
        "adt_endpoints": {
            "packages": {
                "primary": "/sap/bc/adt/packages",
                "alternatives": [
                    "/sap/bc/adt/repository/informationsystem/search?operation=quickSearch&query=*&objectType=DEVC/K",
                    "/sap/bc/adt/repository/nodestructure?parent_name=$ROOT&parent_type=DEVC/K",
                    "/sap/bc/adt/discovery"
                ]
            },
            "programs": {
                "primary": "/sap/bc/adt/programs",
                "alternatives": [
                    "/sap/bc/adt/repository/informationsystem/search?operation=quickSearch&query=*&objectType=PROG/P"
                ]
            },
            "classes": {
                "primary": "/sap/bc/adt/classes", 
                "alternatives": [
                    "/sap/bc/adt/repository/informationsystem/search?operation=quickSearch&query=*&objectType=CLAS/OC"
                ]
            }
        },
        "fallback_mode": {
            "enabled": True,
            "use_mock_data": True,
            "mock_data_path": "/home/gyanmis/mock_sap_data.json"
        },
        "error_handling": {
            "retry_attempts": 3,
            "timeout_seconds": 10,
            "fallback_on_400": True,
            "fallback_on_404": True
        }
    }
    
    return config

def generate_fix_instructions():
    """Generate step-by-step fix instructions"""
    
    instructions = """
🔧 SAP ADT URI Mapping Error - Fix Instructions
===============================================

PROBLEM: URI-Mapping cannot be performed due to invalid URI: /sap/bc/adt/packages

CAUSE: The SAP system's ADT services may not be properly configured or the 
       specific endpoint is not available in your SAP system version.

SOLUTIONS:

1. 🎯 IMMEDIATE FIX - Use Mock Data
   --------------------------------
   - Enable fallback mode in your application
   - Use the mock packages data provided
   - This allows development to continue while fixing the root cause

2. 🔧 SAP SYSTEM FIX - Check ADT Activation
   ----------------------------------------
   a) Login to SAP GUI
   b) Go to transaction SICF
   c) Navigate to: default_host/sap/bc/adt
   d) Ensure all ADT services are activated (green light)
   e) If not activated, right-click → Activate Service

3. 🔄 ALTERNATIVE ENDPOINTS - Use Different ADT Calls
   --------------------------------------------------
   Instead of: /sap/bc/adt/packages
   Try these alternatives:
   
   a) Repository Search:
      /sap/bc/adt/repository/informationsystem/search
      
   b) Node Structure:
      /sap/bc/adt/repository/nodestructure
      
   c) Discovery Service:
      /sap/bc/adt/discovery

4. 🛠️ APPLICATION FIX - Implement Error Handling
   -----------------------------------------------
   - Add try-catch for 400 errors
   - Implement fallback to alternative endpoints
   - Use mock data when all endpoints fail
   - Add retry logic with exponential backoff

5. 🔍 DIAGNOSTIC STEPS
   -------------------
   a) Check SAP system version (ADT requires NetWeaver 7.31+)
   b) Verify user has S_DEVELOP authorization
   c) Test ADT connectivity with SAP GUI for Java
   d) Check network connectivity and firewall rules

6. 📝 TEMPORARY WORKAROUND CODE
   ----------------------------
   ```python
   def fetch_packages_with_fallback(sap_client):
       try:
           # Try primary endpoint
           return sap_client.get('/sap/bc/adt/packages')
       except Exception as e:
           if '400' in str(e) or 'URI-Mapping' in str(e):
               # Try alternative methods
               return fetch_packages_alternative(sap_client)
           raise e
   
   def fetch_packages_alternative(sap_client):
       # Method 1: Repository search
       try:
           return sap_client.get('/sap/bc/adt/repository/informationsystem/search', 
                               params={'objectType': 'DEVC/K'})
       except:
           # Method 2: Use mock data
           return load_mock_packages()
   ```

NEXT STEPS:
1. Implement fallback logic in your application
2. Contact SAP system administrator to check ADT activation
3. Test with alternative endpoints
4. Use mock data for continued development

STATUS CHECK:
✅ Mock data available for immediate use
⚠️  Primary ADT endpoint needs fixing
🔄 Alternative endpoints available for testing
"""
    
    return instructions

def main():
    print("🔧 SAP ADT URI Mapping Error - Quick Fix Generator")
    print("=" * 55)
    
    # Create mock data
    mock_packages = create_mock_packages_response()
    mock_file = "/home/gyanmis/mock_sap_packages.json"
    
    with open(mock_file, 'w') as f:
        json.dump(mock_packages, f, indent=2)
    
    print(f"✅ Created mock packages data: {mock_file}")
    
    # Create alternative config
    config = create_alternative_endpoint_config()
    config_file = "/home/gyanmis/adt_alternative_config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created alternative endpoint config: {config_file}")
    
    # Generate instructions
    instructions = generate_fix_instructions()
    instructions_file = "/home/gyanmis/ADT_URI_MAPPING_FIX.md"
    
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"✅ Created fix instructions: {instructions_file}")
    
    print("\n🎯 IMMEDIATE ACTION ITEMS:")
    print("1. Use mock data from mock_sap_packages.json")
    print("2. Implement fallback logic in your application")
    print("3. Contact SAP admin to check ADT service activation")
    print("4. Test alternative endpoints from the config file")
    
    print(f"\n📦 Mock packages available:")
    for pkg in mock_packages:
        print(f"  - {pkg['name']}: {pkg['description']}")
    
    print(f"\n📖 Read full instructions in: {instructions_file}")

if __name__ == "__main__":
    main()
