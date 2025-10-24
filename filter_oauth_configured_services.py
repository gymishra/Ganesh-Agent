#!/usr/bin/env python3
"""
Filter Services with Specific OAuth2 Configuration Markers
Looks for services with explicit OAuth2 configuration indicators like oauth=X
"""

import requests
import json
import base64
from datetime import datetime
import urllib3
import xml.etree.ElementTree as ET

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

def check_service_oauth_configuration_markers(service, session):
    """Check for specific OAuth2 configuration markers in service"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    service_id = service.get('ID', 'Unknown')
    service_url = service.get('ServiceUrl', '')
    
    oauth_markers = {
        'service_id': service_id,
        'service_url': service_url,
        'oauth_configured': False,
        'oauth_markers_found': [],
        'configuration_details': {}
    }
    
    try:
        # Method 1: Check service properties for OAuth markers
        service_json = json.dumps(service).lower()
        
        # Look for OAuth configuration markers in service data
        oauth_config_markers = [
            'oauth=true', 'oauth=x', 'oauth=1', 'oauth=enabled',
            'authentication=oauth', 'auth_type=oauth', 'security=oauth',
            'oauth_required=true', 'oauth_enabled=true'
        ]
        
        for marker in oauth_config_markers:
            if marker in service_json:
                oauth_markers['oauth_markers_found'].append(marker)
                oauth_markers['oauth_configured'] = True
        
        # Method 2: Check for OAuth2 in service annotations or tags
        if 'TagCollection' in service:
            tag_collection = service.get('TagCollection', {})
            if isinstance(tag_collection, dict):
                tag_str = json.dumps(tag_collection).lower()
                if 'oauth' in tag_str:
                    oauth_markers['oauth_markers_found'].append('oauth_in_tags')
                    oauth_markers['oauth_configured'] = True
        
        # Method 3: Check service metadata for OAuth configuration
        if service_url:
            try:
                # Get service metadata
                metadata_url = f"{service_url}/$metadata"
                metadata_headers = {
                    'Authorization': create_auth_header(USERNAME, PASSWORD),
                    'Accept': 'application/xml, text/xml, */*',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                metadata_response = session.get(metadata_url, headers=metadata_headers, timeout=10)
                
                if metadata_response.status_code == 200:
                    metadata_content = metadata_response.text.lower()
                    
                    # Look for OAuth configuration in metadata
                    oauth_metadata_markers = [
                        'oauth="true"', 'oauth="x"', 'oauth="enabled"',
                        'authentication="oauth"', 'security="oauth2"',
                        'auth-type="oauth"', 'oauth-required="true"'
                    ]
                    
                    for marker in oauth_metadata_markers:
                        if marker in metadata_content:
                            oauth_markers['oauth_markers_found'].append(f'metadata:{marker}')
                            oauth_markers['oauth_configured'] = True
                    
                    # Check for OAuth2 annotations
                    if 'oauth' in metadata_content and ('annotation' in metadata_content or 'property' in metadata_content):
                        oauth_markers['oauth_markers_found'].append('oauth_annotation')
                        oauth_markers['oauth_configured'] = True
                
            except Exception as e:
                oauth_markers['metadata_error'] = str(e)
        
        # Method 4: Check service type and category for OAuth indicators
        service_type = service.get('ServiceType', '').lower()
        category = service.get('Category', '').lower()
        
        if 'oauth' in service_type or 'oauth' in category:
            oauth_markers['oauth_markers_found'].append('oauth_in_type_or_category')
            oauth_markers['oauth_configured'] = True
        
        # Method 5: Check for OAuth2 in service description or title
        title = service.get('Title', '').lower()
        description = service.get('Description', '').lower()
        
        oauth_title_markers = ['oauth', 'oauth2', 'bearer', 'token', 'auth']
        if any(marker in title or marker in description for marker in oauth_title_markers):
            oauth_markers['oauth_markers_found'].append('oauth_in_title_or_description')
            # Don't set oauth_configured=True for this as it's too broad
        
        # Method 6: Try to access service with OAuth2 header to see specific response
        try:
            oauth_test_headers = {
                'Authorization': 'Bearer test_token',
                'Accept': 'application/json'
            }
            
            oauth_test_response = session.get(service_url, headers=oauth_test_headers, timeout=5)
            
            # Check for specific OAuth2 configuration responses
            if oauth_test_response.status_code == 401:
                www_auth = oauth_test_response.headers.get('www-authenticate', '').lower()
                
                # Look for specific OAuth2 configuration indicators
                oauth_response_markers = [
                    'bearer realm=', 'oauth realm=', 'scope=', 'error=invalid_token',
                    'oauth_problem=', 'bearer error='
                ]
                
                for marker in oauth_response_markers:
                    if marker in www_auth:
                        oauth_markers['oauth_markers_found'].append(f'response:{marker}')
                        oauth_markers['oauth_configured'] = True
                        break
        
        except Exception as e:
            pass
        
    except Exception as e:
        oauth_markers['error'] = str(e)
    
    return oauth_markers

def get_oauth_configured_services_with_markers():
    """Get services with specific OAuth2 configuration markers"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    oauth_configured_services = []
    processing_log = []
    
    try:
        print("Searching for services with specific OAuth2 configuration markers...")
        
        # Try different approaches to find OAuth2 configured services
        
        # Approach 1: Try to filter services with OAuth in various fields
        oauth_filter_attempts = [
            # Try filtering by OAuth in different fields
            "$filter=substringof('oauth',tolower(ID))",
            "$filter=substringof('OAuth',ID)",
            "$filter=substringof('AUTH',ID)",
            "$filter=substringof('oauth',tolower(TechnicalServiceName))",
            "$filter=substringof('bearer',tolower(Title))",
            "$filter=substringof('token',tolower(Title))",
            # Try to expand related collections that might contain OAuth info
            "$expand=TagCollection,Annotations",
            "$expand=TagCollection&$filter=substringof('oauth',tolower(Title))",
        ]
        
        all_potential_services = []
        
        for filter_attempt in oauth_filter_attempts:
            try:
                filter_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?{filter_attempt}&$format=json"
                response = session.get(filter_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
                    
                    processing_log.append(f"Filter '{filter_attempt}' found {len(services)} services")
                    print(f"Filter '{filter_attempt}' found {len(services)} services")
                    
                    # Add unique services
                    for service in services:
                        service_id = service.get('ID', '')
                        if not any(s.get('ID') == service_id for s in all_potential_services):
                            all_potential_services.append(service)
                
            except Exception as e:
                processing_log.append(f"Filter '{filter_attempt}' failed: {str(e)}")
        
        # Approach 2: Get a sample of all services and check for OAuth markers
        print("Getting sample of all services to check for OAuth configuration markers...")
        
        all_services_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$top=100&$format=json"
        response = session.get(all_services_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            sample_services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
            
            # Add sample services to potential list
            for service in sample_services:
                service_id = service.get('ID', '')
                if not any(s.get('ID') == service_id for s in all_potential_services):
                    all_potential_services.append(service)
        
        processing_log.append(f"Total potential services to check: {len(all_potential_services)}")
        print(f"Checking {len(all_potential_services)} services for OAuth2 configuration markers...")
        
        # Check each potential service for OAuth configuration markers
        for i, service in enumerate(all_potential_services, 1):
            service_id = service.get('ID', 'Unknown')
            
            if i % 10 == 0:
                print(f"Checked {i}/{len(all_potential_services)} services...")
            
            oauth_markers = check_service_oauth_configuration_markers(service, session)
            
            if oauth_markers.get('oauth_configured'):
                service['oauth_markers'] = oauth_markers
                oauth_configured_services.append(service)
                
                markers_found = oauth_markers.get('oauth_markers_found', [])
                processing_log.append(f"✅ OAuth2 configured: {service_id} - {', '.join(markers_found)}")
                print(f"  ✅ OAuth2 configured: {service_id}")
        
        processing_log.append(f"Total OAuth2 configured services found: {len(oauth_configured_services)}")
        
    except Exception as e:
        processing_log.append(f"Error in OAuth2 marker detection: {str(e)}")
    
    return oauth_configured_services, processing_log

def create_oauth_markers_report(oauth_services, processing_log):
    """Create report of services with OAuth2 configuration markers"""
    
    markdown_content = f"""# Services with OAuth2 Configuration Markers

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Method:** OAuth2 configuration marker detection

## Executive Summary

- **Services with OAuth2 Configuration Markers:** {len(oauth_services)}
- **Detection Method:** Looking for oauth=X, authentication=oauth, and similar markers
- **These services have explicit OAuth2 configuration indicators**

---

## 🎯 **Services with OAuth2 Configuration Markers**

"""
    
    if oauth_services:
        markdown_content += f"""
✅ **Found {len(oauth_services)} services with OAuth2 configuration markers:**

| # | Service ID | Title | OAuth2 Markers Found |
|---|------------|-------|---------------------|
"""
        
        for i, service in enumerate(oauth_services, 1):
            service_id = service.get('ID', 'N/A')
            title = str(service.get('Title', 'N/A')).replace('|', '\\|')[:40]
            oauth_markers = service.get('oauth_markers', {})
            markers_found = ', '.join(oauth_markers.get('oauth_markers_found', []))
            
            markdown_content += f"| {i} | {service_id} | {title} | {markers_found} |\n"
        
        markdown_content += f"""

---

## 📋 **Detailed OAuth2 Configuration Analysis**

"""
        
        for i, service in enumerate(oauth_services, 1):
            service_id = service.get('ID', f'Service_{i}')
            title = service.get('Title', 'N/A')
            service_url = service.get('ServiceUrl', 'N/A')
            oauth_markers = service.get('oauth_markers', {})
            
            markdown_content += f"""
### {i}. {service_id}

**Title:** {title}  
**Service URL:** {service_url}  
**OAuth2 Configured:** ✅ Yes  
**Configuration Markers:** {', '.join(oauth_markers.get('oauth_markers_found', []))}

**Configuration Details:**
- Service has explicit OAuth2 configuration markers
- These markers indicate OAuth2 is specifically configured
- Service likely requires OAuth2 authentication

**Integration Ready:** ✅ Yes - Use OAuth2 authentication

---
"""
    
    else:
        markdown_content += """
❌ **No services with explicit OAuth2 configuration markers found**

This could indicate:
1. **OAuth2 configuration uses different markers** than we searched for
2. **OAuth2 is configured at system level** without service-level markers
3. **Different OAuth2 configuration approach** in this SAP system
4. **OAuth2 markers are in different service properties** not checked

**Alternative approaches to try:**

1. **Check /IWFND/MAINT_SERVICE directly** for OAuth2 configuration
2. **Look for services with specific OAuth2 scopes** configured
3. **Check for OAuth2 client assignments** to services
4. **Review system-level OAuth2 configuration** (SOAUTH2)

**Recommended filters to try in /IWFND/MAINT_SERVICE:**
- Filter by "OAuth2" in service configuration
- Look for services with "Bearer" authentication
- Check services with specific OAuth2 scopes
- Filter by OAuth2 client assignments
"""
    
    markdown_content += f"""

---

## 🔍 **Alternative OAuth2 Detection Methods**

Since we didn't find services with explicit oauth=X markers, here are other approaches:

### Method 1: Check Service Configuration in /IWFND/MAINT_SERVICE
```
1. Go to transaction /IWFND/MAINT_SERVICE
2. Use filters:
   - Authentication Type = "OAuth2"
   - Security Method = "Bearer"
   - OAuth2 Scope configured
3. Look for services with OAuth2 client assignments
```

### Method 2: Check OAuth2 System Configuration
```
Transaction: SOAUTH2
- Look for OAuth2 clients
- Check which services are assigned to OAuth2 clients
- Review OAuth2 scope configurations
```

### Method 3: Check Gateway Service Security
```
Transaction: /IWFND/MAINT_SERVICE
- Select a service
- Go to "OAuth" or "Security" tab
- Look for OAuth2 configuration options
```

### Method 4: Test OAuth2 Authentication
```
Use /IWFND/GW_CLIENT to test services:
- Try OAuth2 authentication
- Check which services accept OAuth2 tokens
- Identify services that require OAuth2
```

---

## 📊 **Processing Log**

"""
    
    for log_entry in processing_log:
        markdown_content += f"- {log_entry}\n"
    
    markdown_content += f"""

---

## 🎯 **Recommendations**

### ✅ **If OAuth2 Services Found**
1. **Use these services** for OAuth2 integration
2. **Configure OAuth2 client** in SOAUTH2
3. **Test OAuth2 authentication** with these services

### ⚠️ **If No OAuth2 Services Found**
1. **Check /IWFND/MAINT_SERVICE manually** for OAuth2 configuration
2. **Look for the 49 services you observed** using different filters
3. **Check system-level OAuth2 configuration** in SOAUTH2
4. **Try different OAuth2 marker patterns** in service metadata

### 🔧 **Next Steps**
1. **Manual verification** in /IWFND/MAINT_SERVICE
2. **Check OAuth2 client configuration** in SOAUTH2
3. **Test specific services** with OAuth2 authentication
4. **Review SAP documentation** for OAuth2 service configuration

---

**Summary:** This analysis looked for explicit OAuth2 configuration markers like oauth=X in service properties and metadata. The results show services that have been specifically configured with OAuth2 indicators.

---
*This report focuses on services with explicit OAuth2 configuration markers rather than OAuth2 capability*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("Searching for Services with OAuth2 Configuration Markers")
    print("=" * 60)
    print("Looking for oauth=X, authentication=oauth, and similar markers")
    print("=" * 60)
    
    # Get services with OAuth2 configuration markers
    oauth_services, processing_log = get_oauth_configured_services_with_markers()
    
    # Create detailed report
    markdown_report = create_oauth_markers_report(oauth_services, processing_log)
    
    # Save to file
    output_file = "/home/gyanmis/oauth_configuration_markers_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ OAuth2 configuration marker analysis complete!")
    print(f"✓ Report saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("OAUTH2 CONFIGURATION MARKERS FOUND:")
    print("=" * 60)
    print(f"🎯 Services with OAuth2 Markers: {len(oauth_services)}")
    
    if oauth_services:
        print(f"✅ SUCCESS: Found services with explicit OAuth2 configuration!")
        print(f"\n📋 SERVICES WITH OAUTH2 MARKERS:")
        for i, service in enumerate(oauth_services[:5], 1):
            service_id = service.get('ID', 'Unknown')
            markers = service.get('oauth_markers', {}).get('oauth_markers_found', [])
            print(f"   {i}. {service_id} - {', '.join(markers[:2])}")
        
        if len(oauth_services) > 5:
            print(f"   ... and {len(oauth_services) - 5} more services")
    else:
        print("⚠️  No services with explicit OAuth2 configuration markers found")
        print("💡 Try checking /IWFND/MAINT_SERVICE manually for OAuth2 config")
    
    print("\n🔧 RECOMMENDATION:")
    if oauth_services:
        print("   Use these services for OAuth2 integration")
    else:
        print("   Check /IWFND/MAINT_SERVICE for OAuth2 configuration")
        print("   Look for services with OAuth2 scopes or client assignments")
    print("=" * 60)

if __name__ == "__main__":
    main()
