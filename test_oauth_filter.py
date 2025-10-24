#!/usr/bin/env python3
"""
Test SAP OData OAuth2 filtering using OData query parameters
"""

import requests
import json
import base64
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SAP System Configuration
SAP_BASE_URL = "https://vhcals4hci.awspoc.club"
USERNAME = "bpinst"
PASSWORD = "Welcome1"

def create_auth_header(username, password):
    """Create basic authentication header"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def test_oauth_filter():
    """Test different OAuth2 filtering approaches"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    # Test different filter approaches
    filter_tests = [
        {
            'name': 'AuthenticationMode OAuth2',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=AuthenticationMode eq 'OAuth2'&$format=json"
        },
        {
            'name': 'AuthenticationMode oauth2 (lowercase)',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=AuthenticationMode eq 'oauth2'&$format=json"
        },
        {
            'name': 'Contains OAuth',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=substringof('OAuth',AuthenticationMode)&$format=json"
        },
        {
            'name': 'Security Method OAuth2',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=SecurityMethod eq 'OAuth2'&$format=json"
        },
        {
            'name': 'All services (to see available fields)',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$top=5&$format=json"
        }
    ]
    
    results = {}
    
    for test in filter_tests:
        print(f"Testing: {test['name']}")
        try:
            response = session.get(test['url'], headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
                results[test['name']] = {
                    'status': 'success',
                    'count': len(services),
                    'services': services[:2] if services else [],  # First 2 for inspection
                    'sample_fields': list(services[0].keys()) if services else []
                }
                print(f"  ✓ Found {len(services)} services")
            else:
                results[test['name']] = {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
                print(f"  ✗ Error {response.status_code}")
                
        except Exception as e:
            results[test['name']] = {
                'status': 'exception',
                'error': str(e)
            }
            print(f"  ✗ Exception: {e}")
    
    return results

def main():
    print("Testing OAuth2 filtering approaches...")
    print("=" * 50)
    
    results = test_oauth_filter()
    
    # Save results to markdown
    markdown_content = f"""# SAP OData OAuth2 Filter Testing Results

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results

"""
    
    for test_name, result in results.items():
        markdown_content += f"""
### {test_name}

**Status:** {result['status']}  
"""
        
        if result['status'] == 'success':
            markdown_content += f"""**Services Found:** {result['count']}  
**Available Fields:** {', '.join(result['sample_fields'])}

**Sample Services:**
```json
{json.dumps(result['services'], indent=2)}
```
"""
        else:
            markdown_content += f"""**Error:** {result.get('error', 'Unknown error')}  
**Status Code:** {result.get('status_code', 'N/A')}
"""
    
    markdown_content += """

## Analysis

Based on these tests, we can determine:
1. Which filter approach works best
2. What authentication-related fields are available
3. The most efficient way to query OAuth2 services

## Recommendations

The most effective approach should be used to update the main filtering script.
"""
    
    # Save results
    output_file = "/home/gyanmis/oauth_filter_test_results.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✓ Test results saved to: {output_file}")

if __name__ == "__main__":
    main()
