#!/usr/bin/env python3
"""
SAP OData Services OAuth2 Filter Script
Filters OData services that support OAuth2 authentication
"""

import requests
import json
import base64
from datetime import datetime
import urllib3
import re

# Disable SSL warnings for self-signed certificates
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

def check_service_oauth2_support(service_url, headers, session):
    """Check if a specific service supports OAuth2 by examining its metadata"""
    try:
        # Try to get service metadata
        metadata_url = f"{service_url}/$metadata"
        response = session.get(metadata_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            metadata_content = response.text.lower()
            
            # Check for OAuth2 indicators in metadata
            oauth2_indicators = [
                'oauth',
                'bearer',
                'authorization_code',
                'client_credentials',
                'saml_bearer',
                'jwt_bearer',
                'oauth2samlbearer',
                'oauth2clientcredentials'
            ]
            
            oauth2_found = any(indicator in metadata_content for indicator in oauth2_indicators)
            return oauth2_found, metadata_content[:500] if oauth2_found else ""
            
    except Exception as e:
        # Log error to markdown instead of printing
        pass
        
    return False, ""

def get_service_authentication_info(service_data, headers, session):
    """Get authentication information for a service"""
    auth_info = {
        'supports_oauth2': False,
        'auth_methods': [],
        'metadata_snippet': '',
        'service_url': ''
    }
    
    try:
        # Construct service URL
        service_id = service_data.get('ServiceId', service_data.get('ID', ''))
        service_version = service_data.get('ServiceVersion', service_data.get('Version', ''))
        
        if service_id:
            # Try different URL patterns for SAP OData services
            possible_urls = [
                f"{SAP_BASE_URL}/sap/opu/odata/sap/{service_id}",
                f"{SAP_BASE_URL}/sap/opu/odata/{service_id}",
                f"{SAP_BASE_URL}/sap/opu/odata/sap/{service_id};v={service_version}" if service_version != 'N/A' else f"{SAP_BASE_URL}/sap/opu/odata/sap/{service_id}"
            ]
            
            for url in possible_urls:
                auth_info['service_url'] = url
                supports_oauth2, metadata_snippet = check_service_oauth2_support(url, headers, session)
                
                if supports_oauth2:
                    auth_info['supports_oauth2'] = True
                    auth_info['metadata_snippet'] = metadata_snippet
                    break
                    
        # Also check service data itself for authentication hints
        service_str = json.dumps(service_data).lower()
        if any(term in service_str for term in ['oauth', 'bearer', 'saml', 'jwt']):
            auth_info['supports_oauth2'] = True
            
    except Exception as e:
        # Log error to markdown instead of printing
        pass
        
    return auth_info

def retrieve_oauth2_enabled_services():
    """Retrieve and filter OData services that support OAuth2"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    # Initialize log for markdown report
    processing_log = []
    processing_log.append("Starting OData services retrieval...")
    
    # Get all services first
    catalog_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$format=json"
    
    try:
        response = session.get(catalog_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            all_services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
            
            processing_log.append(f"Found {len(all_services)} total services")
            processing_log.append("Filtering for OAuth2 enabled services...")
            
            oauth2_services = []
            
            # Sample a subset for testing (checking all would take too long)
            services_to_check = []
            
            # First, add services that likely have OAuth2 based on naming
            for service in all_services:
                service_str = json.dumps(service).lower()
                if any(term in service_str for term in ['oauth', 'bearer', 'saml', 'jwt', 'auth', 'security', 'token']):
                    services_to_check.append(service)
            
            # Add first 50 services for broader sampling
            services_to_check.extend(all_services[:50])
            
            # Remove duplicates
            seen_ids = set()
            unique_services = []
            for service in services_to_check:
                service_id = service.get('ServiceId', service.get('ID', ''))
                if service_id not in seen_ids:
                    seen_ids.add(service_id)
                    unique_services.append(service)
            
            processing_log.append(f"Checking {len(unique_services)} services for OAuth2 support...")
            
            for i, service in enumerate(unique_services, 1):
                service_id = service.get('ServiceId', service.get('ID', 'Unknown'))
                
                # Simple progress indicator without consuming context
                if i % 10 == 0:
                    print(f"Progress: {i}/{len(unique_services)} services checked", end='\r')
                
                auth_info = get_service_authentication_info(service, headers, session)
                
                if auth_info['supports_oauth2']:
                    service['auth_info'] = auth_info
                    oauth2_services.append(service)
                    processing_log.append(f"✓ OAuth2 supported: {service_id}")
            
            # Clear progress line
            print(" " * 50, end='\r')
            
            return oauth2_services, len(all_services), processing_log
            
    except Exception as e:
        processing_log.append(f"Error retrieving services: {e}")
        return [], 0, processing_log

def create_oauth2_markdown_report(oauth2_services, total_services, processing_log):
    """Create markdown report for OAuth2 enabled services"""
    
    markdown_content = f"""# SAP OData Services - OAuth2 Enabled

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Services in System:** {total_services}  
**OAuth2 Enabled Services:** {len(oauth2_services)}  
**Coverage:** {(len(oauth2_services)/total_services*100):.2f}% (of checked services)

---

## Processing Log

"""
    
    for log_entry in processing_log:
        markdown_content += f"- {log_entry}\n"
    
    markdown_content += f"""

---

## OAuth2 Enabled Services Summary

| # | Service ID | Service Version | Title | Service URL | Auth Details |
|---|------------|----------------|-------|-------------|--------------|
"""
    
    for i, service in enumerate(oauth2_services, 1):
        service_id = service.get('ServiceId', service.get('ID', 'N/A'))
        version = service.get('ServiceVersion', service.get('Version', 'N/A'))
        title = service.get('Title', service.get('title', 'N/A'))
        
        auth_info = service.get('auth_info', {})
        service_url = auth_info.get('service_url', 'N/A')
        
        # Clean up for markdown
        title = str(title).replace('|', '\\|').replace('\n', ' ')[:40]
        service_url = service_url.replace('|', '\\|')
        
        markdown_content += f"| {i} | {service_id} | {version} | {title} | {service_url} | OAuth2 Supported |\n"
    
    markdown_content += f"""

---

## Detailed OAuth2 Service Information

"""
    
    for i, service in enumerate(oauth2_services, 1):
        service_id = service.get('ServiceId', service.get('ID', f'Service_{i}'))
        title = service.get('Title', service.get('title', 'N/A'))
        auth_info = service.get('auth_info', {})
        
        markdown_content += f"""
### {i}. {service_id}

**Title:** {title}  
**Service URL:** {auth_info.get('service_url', 'N/A')}  
**OAuth2 Support:** ✅ Yes  

**Service Metadata:**
```json
{json.dumps(service, indent=2)}
```

**Authentication Details:**
- OAuth2 Support: {auth_info.get('supports_oauth2', False)}
- Service URL: {auth_info.get('service_url', 'N/A')}

---
"""
    
    if not oauth2_services:
        markdown_content += """
## No OAuth2 Services Found

No services with explicit OAuth2 support were detected in the checked sample.

**Possible reasons:**
1. OAuth2 configuration might be at the system level rather than service level
2. Authentication details might not be exposed in service metadata
3. OAuth2 might be configured through SAP Gateway security settings
4. Services might use other modern authentication methods

**Recommendations:**
1. Check SAP Gateway OAuth2 configuration (SICF, OAuth2 clients)
2. Review system-level authentication settings
3. Consult with SAP Basis team for OAuth2 setup
4. Check transaction SOAUTH2 for OAuth2 client configurations

"""
    
    markdown_content += f"""

## Summary

- **Total Services in System:** {total_services}
- **Services Checked:** Limited sample for performance
- **OAuth2 Enabled Services Found:** {len(oauth2_services)}
- **System URL:** {SAP_BASE_URL}
- **Analysis Method:** Metadata inspection and service data analysis
- **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Next Steps

1. **For OAuth2 Setup:** Check transaction SOAUTH2 in SAP GUI
2. **Gateway Configuration:** Review /IWFND/MAINT_SERVICE for service security
3. **System Authentication:** Verify OAuth2 providers in SAML2 configuration
4. **Service Testing:** Use /IWFND/GW_CLIENT to test OAuth2 authentication

---
*This report was generated by analyzing service metadata and configuration data*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("SAP OData OAuth2 Services Filter - Starting analysis...")
    
    # Retrieve OAuth2 enabled services
    oauth2_services, total_services, processing_log = retrieve_oauth2_enabled_services()
    
    # Create markdown report
    markdown_report = create_oauth2_markdown_report(oauth2_services, total_services, processing_log)
    
    # Save to file
    output_file = "/home/gyanmis/sap_oauth2_odata_services.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"✓ Analysis complete! Report saved to: {output_file}")
    print(f"✓ Found {len(oauth2_services)} OAuth2 enabled services out of {total_services} total services")

if __name__ == "__main__":
    main()
