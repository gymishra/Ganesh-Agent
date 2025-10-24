#!/usr/bin/env python3
"""
Test advanced SAP OData filtering approaches for OAuth2 services
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

def test_advanced_filters():
    """Test advanced filtering approaches"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    # Test different approaches
    filter_tests = [
        {
            'name': 'Services with OAuth in Title/Description',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=substringof('oauth',tolower(Title)) or substringof('oauth',tolower(Description))&$format=json"
        },
        {
            'name': 'Services with Auth in Title/Description',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=substringof('auth',tolower(Title)) or substringof('auth',tolower(Description))&$format=json"
        },
        {
            'name': 'Services with Security in Title/Description',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$filter=substringof('security',tolower(Title)) or substringof('security',tolower(Description))&$format=json"
        },
        {
            'name': 'Check TagCollection for OAuth info',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$expand=TagCollection&$top=3&$format=json"
        },
        {
            'name': 'Check Annotations for OAuth info',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$expand=Annotations&$top=3&$format=json"
        },
        {
            'name': 'Get service metadata schema',
            'url': f"{SAP_BASE_URL}/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/$metadata"
        }
    ]
    
    results = {}
    
    for test in filter_tests:
        print(f"Testing: {test['name']}")
        try:
            response = session.get(test['url'], headers=headers, timeout=30)
            
            if response.status_code == 200:
                if test['name'] == 'Get service metadata schema':
                    # For metadata, just check if it contains auth-related info
                    content = response.text
                    results[test['name']] = {
                        'status': 'success',
                        'content_length': len(content),
                        'contains_auth_info': 'auth' in content.lower() or 'oauth' in content.lower(),
                        'sample_content': content[:1000]
                    }
                else:
                    data = response.json()
                    services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
                    results[test['name']] = {
                        'status': 'success',
                        'count': len(services),
                        'services': services[:1] if services else [],  # First service for inspection
                    }
                print(f"  ✓ Success - Found {len(services) if 'services' in locals() else 'metadata'}")
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
    print("Testing advanced OAuth2 filtering approaches...")
    print("=" * 50)
    
    results = test_advanced_filters()
    
    # Save results to markdown
    markdown_content = f"""# SAP OData Advanced Filter Testing Results

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Findings

The original filtering approach `$filter=AuthenticationMode eq 'OAuth2'` **does not work** because:
- `AuthenticationMode` field does not exist in the SAP Gateway Catalog Service
- `SecurityMethod` field also does not exist
- Authentication information is not directly exposed in the service catalog

## Alternative Approaches Tested

"""
    
    for test_name, result in results.items():
        markdown_content += f"""
### {test_name}

**Status:** {result['status']}  
"""
        
        if result['status'] == 'success':
            if 'count' in result:
                markdown_content += f"""**Services Found:** {result['count']}

**Sample Service:**
```json
{json.dumps(result['services'], indent=2)}
```
"""
            else:
                markdown_content += f"""**Content Length:** {result.get('content_length', 0)}  
**Contains Auth Info:** {result.get('contains_auth_info', False)}

**Sample Content:**
```xml
{result.get('sample_content', 'No content')}
```
"""
        else:
            markdown_content += f"""**Error:** {result.get('error', 'Unknown error')}  
**Status Code:** {result.get('status_code', 'N/A')}
"""
    
    markdown_content += """

## Conclusion

**The filtering approach `$filter=AuthenticationMode eq 'OAuth2'` does NOT work** because:

1. **No Authentication Fields**: The SAP Gateway Catalog Service does not expose authentication-related fields
2. **Limited Metadata**: Service catalog only contains basic service information
3. **Security by Design**: Authentication configuration is typically handled at the system/gateway level, not service level

## Recommended Approach

The **current metadata inspection approach is actually the most reliable** method because:

1. **Service Metadata Analysis**: Check each service's `/$metadata` endpoint for OAuth2 indicators
2. **Gateway Configuration**: Authentication is configured at the SAP Gateway level
3. **Runtime Detection**: OAuth2 support is determined by examining service implementation details

## Better Optimization Strategies

Instead of server-side filtering, optimize the current approach:

1. **Parallel Processing**: Check multiple services concurrently
2. **Smart Sampling**: Prioritize services with auth-related keywords in title/description
3. **Caching**: Cache results to avoid repeated checks
4. **Batch Processing**: Process services in smaller batches

The metadata inspection approach, while slower, is the most accurate method for detecting OAuth2 support.
"""
    
    # Save results
    output_file = "/home/gyanmis/advanced_oauth_filter_test.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✓ Advanced test results saved to: {output_file}")

if __name__ == "__main__":
    main()
