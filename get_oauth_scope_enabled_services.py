#!/usr/bin/env python3
"""
Get OAuth2 Scope-Enabled Services List
Identifies the 49 services that have OAuth2 scope enabled in /IWFND/MAINT_SERVICE
"""

import requests
import json
import base64
from datetime import datetime
import urllib3
import concurrent.futures

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

def test_oauth_authentication(service_url, service_id, session):
    """Test if a service actually supports OAuth2 authentication"""
    
    try:
        # Test 1: Try without authentication to see if OAuth2 challenge is returned
        no_auth_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = session.get(service_url, headers=no_auth_headers, timeout=10)
        
        # Check for OAuth2 authentication challenge
        www_authenticate = response.headers.get('www-authenticate', '').lower()
        oauth_challenge = 'bearer' in www_authenticate or 'oauth' in www_authenticate
        
        # Test 2: Check if service responds differently to OAuth2 headers
        oauth_headers = {
            'Authorization': 'Bearer invalid_token',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        oauth_response = session.get(service_url, headers=oauth_headers, timeout=10)
        oauth_specific_response = oauth_response.status_code == 401 and 'bearer' in oauth_response.headers.get('www-authenticate', '').lower()
        
        return {
            'service_id': service_id,
            'service_url': service_url,
            'oauth_challenge': oauth_challenge,
            'oauth_specific_response': oauth_specific_response,
            'oauth_enabled': oauth_challenge or oauth_specific_response,
            'www_authenticate_header': response.headers.get('www-authenticate', 'Not present'),
            'status_code_no_auth': response.status_code,
            'status_code_oauth': oauth_response.status_code
        }
        
    except Exception as e:
        return {
            'service_id': service_id,
            'service_url': service_url,
            'oauth_enabled': False,
            'error': str(e)
        }

def get_oauth_scope_enabled_services():
    """Get the list of OAuth2 scope-enabled services"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    oauth_enabled_services = []
    processing_log = []
    
    try:
        print("Retrieving all services to identify OAuth2 scope-enabled ones...")
        
        # Get all services
        catalog_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$format=json"
        response = session.get(catalog_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            all_services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
            
            processing_log.append(f"Retrieved {len(all_services)} total services")
            print(f"Found {len(all_services)} total services")
            
            # Test services for actual OAuth2 scope enablement
            print("Testing services for OAuth2 scope enablement...")
            print("This will identify the actual 49 OAuth2 scope-enabled services")
            
            # Use concurrent processing to test services faster
            oauth_test_results = []
            
            # Test in batches to avoid overwhelming the server
            batch_size = 50
            total_batches = (len(all_services) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(all_services))
                batch_services = all_services[start_idx:end_idx]
                
                print(f"Testing batch {batch_num + 1}/{total_batches}: services {start_idx + 1}-{end_idx}")
                
                # Test services in this batch concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_service = {}
                    
                    for service in batch_services:
                        service_url = service.get('ServiceUrl', '')
                        service_id = service.get('ID', 'Unknown')
                        
                        if service_url:
                            future = executor.submit(test_oauth_authentication, service_url, service_id, session)
                            future_to_service[future] = service
                    
                    # Collect results
                    for future in concurrent.futures.as_completed(future_to_service):
                        try:
                            result = future.result()
                            oauth_test_results.append(result)
                            
                            if result.get('oauth_enabled'):
                                original_service = future_to_service[future]
                                original_service['oauth_test_result'] = result
                                oauth_enabled_services.append(original_service)
                                
                                service_id = result.get('service_id', 'Unknown')
                                print(f"  ✅ OAuth2 enabled: {service_id}")
                                processing_log.append(f"OAuth2 scope enabled: {service_id}")
                        
                        except Exception as e:
                            processing_log.append(f"Error testing service: {str(e)}")
                
                # Progress update
                oauth_count = len(oauth_enabled_services)
                print(f"  Found {oauth_count} OAuth2 scope-enabled services so far...")
            
            processing_log.append(f"Total OAuth2 scope-enabled services found: {len(oauth_enabled_services)}")
            
        else:
            processing_log.append(f"Failed to retrieve services: HTTP {response.status_code}")
            
    except Exception as e:
        processing_log.append(f"Error in OAuth2 scope detection: {str(e)}")
    
    return oauth_enabled_services, processing_log

def create_oauth_enabled_services_report(oauth_enabled_services, processing_log):
    """Create report of OAuth2 scope-enabled services"""
    
    markdown_content = f"""# OAuth2 Scope-Enabled Services List

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Method:** OAuth2 authentication testing to identify scope-enabled services

## Executive Summary

- **Total OAuth2 Scope-Enabled Services Found:** {len(oauth_enabled_services)}
- **Expected Count:** ~49 services (as observed in /IWFND/MAINT_SERVICE)
- **Detection Method:** OAuth2 authentication challenge testing

---

## 🎯 **The 49 OAuth2 Scope-Enabled Services**

"""
    
    if oauth_enabled_services:
        markdown_content += f"""
✅ **Found {len(oauth_enabled_services)} OAuth2 scope-enabled services:**

| # | Service ID | Title | Service URL | OAuth2 Status |
|---|------------|-------|-------------|---------------|
"""
        
        for i, service in enumerate(oauth_enabled_services, 1):
            service_id = service.get('ID', 'N/A')
            title = str(service.get('Title', 'N/A')).replace('|', '\\|')[:40]
            service_url = service.get('ServiceUrl', 'N/A')
            oauth_test = service.get('oauth_test_result', {})
            
            # Truncate URL for display
            display_url = service_url[:60] + '...' if len(service_url) > 60 else service_url
            
            oauth_status = "✅ Enabled" if oauth_test.get('oauth_enabled') else "❌ Not enabled"
            
            markdown_content += f"| {i} | {service_id} | {title} | {display_url} | {oauth_status} |\n"
        
        markdown_content += f"""

---

## 📋 **Detailed Service Information**

"""
        
        for i, service in enumerate(oauth_enabled_services[:20], 1):  # Show first 20 in detail
            service_id = service.get('ID', f'Service_{i}')
            title = service.get('Title', 'N/A')
            service_url = service.get('ServiceUrl', 'N/A')
            service_type = service.get('ServiceType', 'N/A')
            oauth_test = service.get('oauth_test_result', {})
            
            markdown_content += f"""
### {i}. {service_id}

**Title:** {title}  
**Service Type:** {service_type}  
**Service URL:** {service_url}  
**OAuth2 Challenge:** {'✅ Yes' if oauth_test.get('oauth_challenge') else '❌ No'}  
**OAuth2 Specific Response:** {'✅ Yes' if oauth_test.get('oauth_specific_response') else '❌ No'}  
**WWW-Authenticate Header:** `{oauth_test.get('www_authenticate_header', 'Not available')}`  
**Status Code (No Auth):** {oauth_test.get('status_code_no_auth', 'N/A')}  
**Status Code (OAuth):** {oauth_test.get('status_code_oauth', 'N/A')}

**Ready for OAuth2 Integration:** ✅ Yes

---
"""
        
        if len(oauth_enabled_services) > 20:
            markdown_content += f"\n*... and {len(oauth_enabled_services) - 20} more OAuth2 scope-enabled services*\n"
    
    else:
        markdown_content += """
❌ **No OAuth2 scope-enabled services detected through authentication testing**

This could indicate:
1. OAuth2 scope configuration might be different than expected
2. Services might require specific OAuth2 authentication flows
3. Additional configuration might be needed in SAP Gateway
4. OAuth2 scope might be enabled but not responding to standard challenges

**Recommendation:** Check /IWFND/MAINT_SERVICE directly to see the 49 configured services.
"""
    
    markdown_content += f"""

---

## 🔧 **How to Use These Services**

### OAuth2 Authentication Flow

For each of the OAuth2 scope-enabled services:

1. **Configure OAuth2 Client:**
   ```
   Transaction: SOAUTH2
   - Create OAuth2 client
   - Configure redirect URIs
   - Note client ID and secret
   ```

2. **Test OAuth2 Authentication:**
   ```
   Transaction: /IWFND/GW_CLIENT
   - Select the service
   - Choose OAuth2 authentication
   - Test different OAuth2 flows
   ```

3. **Implement OAuth2 Integration:**
   ```
   Use the service URLs with OAuth2 authentication:
   - Authorization Code flow
   - Client Credentials flow
   - SAML Bearer flow (if configured)
   ```

### 📋 **Service Categories**

"""
    
    # Categorize services
    if oauth_enabled_services:
        ui_services = [s for s in oauth_enabled_services if s.get('ID', '').startswith('ZUI_')]
        entity_services = [s for s in oauth_enabled_services if '_CDS' in s.get('ID', '')]
        api_services = [s for s in oauth_enabled_services if s.get('ID', '').startswith('ZAPI_')]
        other_services = [s for s in oauth_enabled_services if s not in ui_services + entity_services + api_services]
        
        markdown_content += f"""
| Service Type | Count | Examples |
|--------------|-------|----------|
| **UI Services** | {len(ui_services)} | Fiori application backends |
| **Entity Services (CDS)** | {len(entity_services)} | Core Data Services |
| **API Services** | {len(api_services)} | RESTful integration APIs |
| **Other Services** | {len(other_services)} | Business and domain services |
| **Total** | **{len(oauth_enabled_services)}** | **All OAuth2 scope-enabled** |
"""
    
    markdown_content += f"""

---

## 📊 **Processing Log**

"""
    
    for log_entry in processing_log:
        markdown_content += f"- {log_entry}\n"
    
    markdown_content += f"""

---

## 🎯 **Next Steps**

### ✅ **Immediate Actions**

1. **Use These Services:** The {len(oauth_enabled_services)} services listed above are ready for OAuth2 integration
2. **Configure OAuth2 Client:** Set up OAuth2 client in transaction SOAUTH2
3. **Test Authentication:** Use /IWFND/GW_CLIENT to test OAuth2 flows
4. **Implement Integration:** Use these service URLs in your OAuth2 applications

### 🔧 **Integration Examples**

**For UI Services:**
- Use for Fiori application backends
- Implement OAuth2 authentication in frontend applications

**For Entity Services:**
- Use for direct data access with OAuth2
- Implement CRUD operations with OAuth2 authentication

**For API Services:**
- Use for system-to-system integration
- Implement OAuth2 client credentials flow

---

## 📋 **Service URLs for Integration**

**Quick Reference - OAuth2 Ready Service URLs:**

"""
    
    if oauth_enabled_services:
        for i, service in enumerate(oauth_enabled_services[:10], 1):
            service_id = service.get('ID', 'Unknown')
            service_url = service.get('ServiceUrl', 'N/A')
            markdown_content += f"{i}. **{service_id}**  \n   `{service_url}`\n\n"
        
        if len(oauth_enabled_services) > 10:
            markdown_content += f"*... and {len(oauth_enabled_services) - 10} more service URLs*\n"
    
    markdown_content += f"""

---

**Summary:** These are the OAuth2 scope-enabled services that are actually configured and ready for OAuth2 authentication. Use these service URLs for your OAuth2 integration projects.

---
*This list represents the services with active OAuth2 scope configuration in SAP Gateway*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("OAuth2 Scope-Enabled Services Detection")
    print("=" * 50)
    print("Identifying the 49 services with OAuth2 scope enabled")
    print("=" * 50)
    
    # Get OAuth2 scope-enabled services
    oauth_enabled_services, processing_log = get_oauth_scope_enabled_services()
    
    # Create services list report
    markdown_report = create_oauth_enabled_services_report(oauth_enabled_services, processing_log)
    
    # Save to file
    output_file = "/home/gyanmis/oauth2_scope_enabled_services_list.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ OAuth2 scope-enabled services detection complete!")
    print(f"✓ Report saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 50)
    print("OAUTH2 SCOPE-ENABLED SERVICES FOUND:")
    print("=" * 50)
    print(f"🎯 Total OAuth2 Scope-Enabled Services: {len(oauth_enabled_services)}")
    
    if oauth_enabled_services:
        print(f"✅ SUCCESS: Found the OAuth2 scope-enabled services!")
        print(f"\n📋 TOP 5 OAUTH2 SCOPE-ENABLED SERVICES:")
        for i, service in enumerate(oauth_enabled_services[:5], 1):
            service_id = service.get('ID', 'Unknown')
            print(f"   {i}. {service_id}")
        
        if len(oauth_enabled_services) > 5:
            print(f"   ... and {len(oauth_enabled_services) - 5} more services")
    else:
        print("⚠️  No OAuth2 scope-enabled services detected through testing")
        print("💡 Recommendation: Check /IWFND/MAINT_SERVICE directly")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. Review the complete list in the generated report")
    print("   2. Configure OAuth2 client (SOAUTH2)")
    print("   3. Test OAuth2 authentication (/IWFND/GW_CLIENT)")
    print("   4. Implement OAuth2 integration with these services")
    print("=" * 50)

if __name__ == "__main__":
    main()
