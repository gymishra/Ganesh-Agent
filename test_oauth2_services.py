#!/usr/bin/env python3
"""
Test OAuth2 Authentication with Discovered Services
Tests the 6 OAuth2-enabled services found in the metadata analysis
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

# OAuth2-enabled services discovered
OAUTH2_SERVICES = [
    {
        'id': 'ZAPS_BUM_COLLABORATION_USER_SRV_0001',
        'title': 'APS_BUM_COLLABORATION_USER_SRV',
        'url': 'https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BUM_COLLABORATION_USER_SRV'
    },
    {
        'id': 'ZAPS_BUM_EMPLOYEE_SRV_0001', 
        'title': 'APS_BUM_EMPLOYEE_SRV',
        'url': 'https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BUM_EMPLOYEE_SRV'
    },
    {
        'id': 'ZAPS_BUM_EXT_RESOURCE_SRV_0001',
        'title': 'APS_BUM_EXT_RESOURCE_SRV', 
        'url': 'https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BUM_EXT_RESOURCE_SRV'
    },
    {
        'id': 'ZAPS_EXT_CCV_SRV_0001',
        'title': 'APS_EXT_CCV_SRV',
        'url': 'https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_EXT_CCV_SRV'
    },
    {
        'id': 'ZAPS_EXT_EIT_IMPORT_SRV_0001',
        'title': 'APS_EXT_EIT_IMPORT_SRV',
        'url': 'https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_EXT_EIT_IMPORT_SRV'
    },
    {
        'id': 'ZUI_PROCREPAIRQTANS_0001',
        'title': 'UI_PROCREPAIRQTANS',
        'url': 'https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/UI_PROCREPAIRQTANS'
    }
]

def create_auth_header(username, password):
    """Create basic authentication header"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def test_service_authentication(service, session):
    """Test different authentication methods with a service"""
    
    results = {
        'service_id': service['id'],
        'service_url': service['url'],
        'tests': {}
    }
    
    # Test 1: Basic Authentication (current method)
    basic_headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = session.get(service['url'], headers=basic_headers, timeout=15)
        results['tests']['basic_auth'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'content_type': response.headers.get('content-type', 'Unknown'),
            'response_size': len(response.text) if response.text else 0
        }
    except Exception as e:
        results['tests']['basic_auth'] = {
            'success': False,
            'error': str(e)
        }
    
    # Test 2: Check for OAuth2 authentication challenges
    no_auth_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = session.get(service['url'], headers=no_auth_headers, timeout=15)
        results['tests']['no_auth'] = {
            'status_code': response.status_code,
            'www_authenticate': response.headers.get('www-authenticate', 'Not present'),
            'oauth_challenge': 'Bearer' in response.headers.get('www-authenticate', ''),
            'response_size': len(response.text) if response.text else 0
        }
    except Exception as e:
        results['tests']['no_auth'] = {
            'error': str(e)
        }
    
    # Test 3: Check service document structure
    try:
        service_doc_url = service['url'] + '?$format=json'
        response = session.get(service_doc_url, headers=basic_headers, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                entity_sets = []
                if 'd' in data and 'EntitySets' in data['d']:
                    entity_sets = data['d']['EntitySets']
                elif 'value' in data:
                    entity_sets = [item.get('name', 'Unknown') for item in data['value']]
                
                results['tests']['service_document'] = {
                    'success': True,
                    'entity_sets_count': len(entity_sets),
                    'entity_sets': entity_sets[:5],  # First 5 entity sets
                    'has_data': len(entity_sets) > 0
                }
            except json.JSONDecodeError:
                results['tests']['service_document'] = {
                    'success': False,
                    'error': 'Invalid JSON response'
                }
        else:
            results['tests']['service_document'] = {
                'success': False,
                'status_code': response.status_code
            }
    except Exception as e:
        results['tests']['service_document'] = {
            'success': False,
            'error': str(e)
        }
    
    return results

def test_all_oauth2_services():
    """Test all discovered OAuth2 services"""
    
    session = requests.Session()
    session.verify = False
    
    test_results = []
    
    print("Testing OAuth2-enabled services...")
    print("=" * 60)
    
    for i, service in enumerate(OAUTH2_SERVICES, 1):
        print(f"\n{i}. Testing service: {service['id']}")
        print(f"   URL: {service['url']}")
        
        result = test_service_authentication(service, session)
        test_results.append(result)
        
        # Display immediate results
        basic_auth = result['tests'].get('basic_auth', {})
        no_auth = result['tests'].get('no_auth', {})
        service_doc = result['tests'].get('service_document', {})
        
        if basic_auth.get('success'):
            print(f"   ✅ Basic Auth: Success ({basic_auth.get('status_code')})")
        else:
            print(f"   ❌ Basic Auth: Failed ({basic_auth.get('status_code', 'Error')})")
        
        if no_auth.get('oauth_challenge'):
            print(f"   🔐 OAuth Challenge: {no_auth.get('www_authenticate')}")
        else:
            print(f"   ⚠️  No OAuth Challenge detected")
        
        if service_doc.get('success') and service_doc.get('has_data'):
            print(f"   📊 Entity Sets: {service_doc.get('entity_sets_count')} found")
        else:
            print(f"   📊 Service Document: Not accessible or empty")
    
    return test_results

def create_oauth2_test_report(test_results):
    """Create OAuth2 authentication test report"""
    
    markdown_content = f"""# OAuth2 Services Authentication Test Report

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Services Tested:** {len(test_results)}

## Test Summary

| # | Service ID | Basic Auth | OAuth Challenge | Entity Sets | Status |
|---|------------|------------|-----------------|-------------|--------|
"""
    
    for i, result in enumerate(test_results, 1):
        service_id = result['service_id']
        basic_auth = result['tests'].get('basic_auth', {})
        no_auth = result['tests'].get('no_auth', {})
        service_doc = result['tests'].get('service_document', {})
        
        basic_status = "✅" if basic_auth.get('success') else "❌"
        oauth_status = "🔐" if no_auth.get('oauth_challenge') else "⚠️"
        entity_count = service_doc.get('entity_sets_count', 0)
        overall_status = "Ready" if basic_auth.get('success') and entity_count > 0 else "Issues"
        
        markdown_content += f"| {i} | {service_id} | {basic_status} | {oauth_status} | {entity_count} | {overall_status} |\n"
    
    markdown_content += f"""

## Detailed Test Results

"""
    
    for i, result in enumerate(test_results, 1):
        service_id = result['service_id']
        service_url = result['service_url']
        tests = result['tests']
        
        markdown_content += f"""
### {i}. {service_id}

**Service URL:** {service_url}

#### Authentication Tests

**Basic Authentication:**
"""
        
        basic_auth = tests.get('basic_auth', {})
        if basic_auth.get('success'):
            markdown_content += f"""- ✅ **Success** (Status: {basic_auth.get('status_code')})
- Content Type: {basic_auth.get('content_type', 'Unknown')}
- Response Size: {basic_auth.get('response_size', 0)} bytes
"""
        else:
            markdown_content += f"""- ❌ **Failed** 
- Error: {basic_auth.get('error', f"HTTP {basic_auth.get('status_code', 'Unknown')}")}
"""
        
        markdown_content += f"""
**OAuth2 Challenge Test:**
"""
        
        no_auth = tests.get('no_auth', {})
        if no_auth.get('oauth_challenge'):
            markdown_content += f"""- 🔐 **OAuth2 Challenge Detected**
- WWW-Authenticate Header: `{no_auth.get('www_authenticate', 'Not available')}`
- Status Code: {no_auth.get('status_code', 'Unknown')}
"""
        else:
            markdown_content += f"""- ⚠️ **No OAuth2 Challenge**
- WWW-Authenticate Header: `{no_auth.get('www_authenticate', 'Not present')}`
- Status Code: {no_auth.get('status_code', 'Unknown')}
"""
        
        markdown_content += f"""
**Service Document Analysis:**
"""
        
        service_doc = tests.get('service_document', {})
        if service_doc.get('success') and service_doc.get('has_data'):
            entity_sets = service_doc.get('entity_sets', [])
            markdown_content += f"""- ✅ **Service Document Accessible**
- Entity Sets Found: {service_doc.get('entity_sets_count', 0)}
- Sample Entity Sets: {', '.join(entity_sets)}
- **Recommendation:** Service is ready for OAuth2 integration
"""
        else:
            markdown_content += f"""- ❌ **Service Document Issues**
- Error: {service_doc.get('error', f"HTTP {service_doc.get('status_code', 'Unknown')}")}
- **Recommendation:** Check service configuration
"""
        
        markdown_content += f"""
---
"""
    
    # Summary and recommendations
    successful_services = [r for r in test_results if r['tests'].get('basic_auth', {}).get('success')]
    oauth_challenge_services = [r for r in test_results if r['tests'].get('no_auth', {}).get('oauth_challenge')]
    ready_services = [r for r in test_results if r['tests'].get('basic_auth', {}).get('success') and r['tests'].get('service_document', {}).get('has_data')]
    
    markdown_content += f"""

## Summary & Recommendations

### 📊 Test Results Summary
- **Total Services Tested:** {len(test_results)}
- **Services with Basic Auth Success:** {len(successful_services)}
- **Services with OAuth2 Challenge:** {len(oauth_challenge_services)}
- **Services Ready for Integration:** {len(ready_services)}

### ✅ Ready for OAuth2 Integration
"""
    
    if ready_services:
        for service in ready_services:
            service_id = service['service_id']
            entity_count = service['tests'].get('service_document', {}).get('entity_sets_count', 0)
            markdown_content += f"- **{service_id}** - {entity_count} entity sets available\n"
        
        markdown_content += f"""
### 🚀 Next Steps for OAuth2 Implementation

1. **Configure OAuth2 Client in SAP:**
   - Use transaction `SOAUTH2` to create OAuth2 client
   - Configure redirect URIs and scopes
   - Note the client ID and secret

2. **Test OAuth2 Authentication:**
   - Use `/IWFND/GW_CLIENT` to test OAuth2 flows
   - Test Authorization Code flow
   - Test Client Credentials flow

3. **Implement OAuth2 in Applications:**
   - Use discovered service URLs
   - Implement OAuth2 authentication flow
   - Test with entity sets found in service documents

### 🔧 Services Requiring Configuration
"""
        
        problem_services = [r for r in test_results if not r['tests'].get('basic_auth', {}).get('success')]
        if problem_services:
            for service in problem_services:
                service_id = service['service_id']
                error = service['tests'].get('basic_auth', {}).get('error', 'Authentication failed')
                markdown_content += f"- **{service_id}** - {error}\n"
        else:
            markdown_content += "- All services are accessible with basic authentication\n"
    else:
        markdown_content += """
⚠️ **No services are currently ready for OAuth2 integration**

**Recommended Actions:**
1. Check SAP system OAuth2 configuration (SOAUTH2)
2. Verify service security settings (/IWFND/MAINT_SERVICE)
3. Review SICF authentication handlers
4. Contact SAP Basis team for OAuth2 setup assistance
"""
    
    markdown_content += f"""

---
*This report tests the OAuth2-enabled services discovered through metadata analysis*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("OAuth2 Services Authentication Test")
    print("Testing the 6 discovered OAuth2-enabled services...")
    
    # Test all OAuth2 services
    test_results = test_all_oauth2_services()
    
    # Create test report
    markdown_report = create_oauth2_test_report(test_results)
    
    # Save to file
    output_file = "/home/gyanmis/oauth2_services_test_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ OAuth2 service testing complete!")
    print(f"✓ Report saved to: {output_file}")
    
    # Summary
    successful_services = [r for r in test_results if r['tests'].get('basic_auth', {}).get('success')]
    ready_services = [r for r in test_results if r['tests'].get('basic_auth', {}).get('success') and r['tests'].get('service_document', {}).get('has_data')]
    
    print("\n" + "="*60)
    print("OAUTH2 SERVICES TEST SUMMARY:")
    print("="*60)
    print(f"✅ Services with Basic Auth: {len(successful_services)}/{len(test_results)}")
    print(f"🚀 Services Ready for OAuth2: {len(ready_services)}/{len(test_results)}")
    
    if ready_services:
        print("\n🎯 READY FOR OAUTH2 INTEGRATION:")
        for service in ready_services[:3]:
            service_id = service['service_id']
            print(f"   - {service_id}")
    
    print("\n🔧 NEXT: Configure OAuth2 clients in SAP (SOAUTH2)")
    print("="*60)

if __name__ == "__main__":
    main()
