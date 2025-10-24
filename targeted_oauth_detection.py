#!/usr/bin/env python3
"""
Targeted SAP OAuth2 Detection Script
Focuses on specific service patterns and provides system configuration guidance
"""

import requests
import json
import base64
from datetime import datetime
import urllib3
import re

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

def get_high_priority_oauth_services():
    """Get services most likely to support OAuth2"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    results = {
        'high_priority_services': [],
        'system_info': {},
        'recommendations': [],
        'processing_log': []
    }
    
    try:
        # 1. Look for specific OAuth2-related service patterns
        oauth_patterns = [
            "substringof('oauth',tolower(Title))",
            "substringof('bearer',tolower(Title))",
            "substringof('token',tolower(Title))",
            "substringof('saml',tolower(Title))",
            "substringof('jwt',tolower(Title))",
            "substringof('security',tolower(Title))",
            "substringof('auth',tolower(Description))"
        ]
        
        for pattern in oauth_patterns:
            try:
                filter_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$filter={pattern}&$format=json"
                response = session.get(filter_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
                    
                    if services:
                        results['processing_log'].append(f"Found {len(services)} services matching pattern: {pattern}")
                        
                        # Add unique services
                        for service in services[:5]:  # Limit to first 5 per pattern
                            service_id = service.get('ID', '')
                            if not any(s.get('ID') == service_id for s in results['high_priority_services']):
                                service['detection_pattern'] = pattern
                                results['high_priority_services'].append(service)
                
            except Exception as e:
                results['processing_log'].append(f"Error with pattern {pattern}: {str(e)}")
        
        # 2. Check for standard SAP OAuth2 services
        standard_oauth_services = [
            'OAUTH2_SRV',
            'SECURITY_SRV', 
            'AUTH_SRV',
            'TOKEN_SRV',
            'SAML_SRV'
        ]
        
        for service_name in standard_oauth_services:
            try:
                filter_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$filter=substringof('{service_name}',ID)&$format=json"
                response = session.get(filter_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
                    
                    if services:
                        results['processing_log'].append(f"Found {len(services)} services with ID containing: {service_name}")
                        for service in services:
                            service['detection_pattern'] = f"Standard OAuth service: {service_name}"
                            results['high_priority_services'].append(service)
                            
            except Exception as e:
                results['processing_log'].append(f"Error checking standard service {service_name}: {str(e)}")
        
        # 3. Get system information
        try:
            # Try to get catalog service metadata for system info
            metadata_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/$metadata"
            response = session.get(metadata_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                results['system_info']['catalog_metadata_available'] = True
                results['system_info']['system_url'] = SAP_BASE_URL
                results['processing_log'].append("System catalog metadata accessible")
            else:
                results['system_info']['catalog_metadata_available'] = False
                
        except Exception as e:
            results['processing_log'].append(f"Error getting system info: {str(e)}")
        
        # 4. Generate recommendations based on findings
        if len(results['high_priority_services']) == 0:
            results['recommendations'].extend([
                "No OAuth2-specific services found in catalog",
                "OAuth2 is likely configured at SAP Gateway system level",
                "Check transaction SOAUTH2 for OAuth2 client configurations",
                "Review /IWFND/MAINT_SERVICE for service-level security settings",
                "Verify SICF services for OAuth2 authentication handlers"
            ])
        else:
            results['recommendations'].extend([
                f"Found {len(results['high_priority_services'])} potential OAuth2-related services",
                "Check metadata of identified services for OAuth2 support",
                "Verify service-level OAuth2 configuration in /IWFND/MAINT_SERVICE",
                "Test OAuth2 authentication with identified services"
            ])
        
        # 5. Check a few high-priority services for metadata
        for i, service in enumerate(results['high_priority_services'][:5]):
            service_url = service.get('ServiceUrl', '')
            if service_url:
                try:
                    metadata_url = f"{service_url}/$metadata"
                    response = session.get(metadata_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        metadata_content = response.text.lower()
                        oauth_indicators = ['oauth', 'bearer', 'authorization', 'token', 'saml', 'jwt']
                        found_indicators = [ind for ind in oauth_indicators if ind in metadata_content]
                        
                        service['metadata_check'] = {
                            'accessible': True,
                            'oauth_indicators': found_indicators,
                            'has_oauth_hints': len(found_indicators) > 0
                        }
                        
                        if found_indicators:
                            results['processing_log'].append(f"Service {service.get('ID', 'Unknown')} has OAuth indicators: {found_indicators}")
                    else:
                        service['metadata_check'] = {
                            'accessible': False,
                            'error_code': response.status_code
                        }
                        
                except Exception as e:
                    service['metadata_check'] = {
                        'accessible': False,
                        'error': str(e)
                    }
        
    except Exception as e:
        results['processing_log'].append(f"Major error in OAuth detection: {str(e)}")
    
    return results

def create_targeted_oauth_report(results):
    """Create targeted OAuth2 detection report"""
    
    high_priority = results.get('high_priority_services', [])
    system_info = results.get('system_info', {})
    recommendations = results.get('recommendations', [])
    processing_log = results.get('processing_log', [])
    
    markdown_content = f"""# Targeted SAP OAuth2 Detection Report

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Detection Strategy:** High-priority service patterns + system configuration guidance

## Executive Summary

- **High-Priority OAuth Services Found:** {len(high_priority)}
- **System Catalog Accessible:** {system_info.get('catalog_metadata_available', 'Unknown')}
- **Recommended Next Steps:** {len(recommendations)}

---

## Key Findings

### OAuth2 Service Detection Results

"""
    
    if high_priority:
        markdown_content += f"""
✅ **Found {len(high_priority)} potential OAuth2-related services**

| # | Service ID | Title | Detection Pattern | Metadata Check |
|---|------------|-------|------------------|----------------|
"""
        
        for i, service in enumerate(high_priority[:10], 1):
            service_id = service.get('ID', 'N/A')
            title = str(service.get('Title', 'N/A')).replace('|', '\\|')[:30]
            pattern = service.get('detection_pattern', 'N/A')[:40]
            
            metadata_check = service.get('metadata_check', {})
            if metadata_check.get('accessible'):
                if metadata_check.get('has_oauth_hints'):
                    check_status = f"✅ OAuth indicators: {', '.join(metadata_check.get('oauth_indicators', []))}"
                else:
                    check_status = "⚠️ No OAuth indicators"
            else:
                check_status = f"❌ Not accessible ({metadata_check.get('error_code', 'Error')})"
            
            markdown_content += f"| {i} | {service_id} | {title} | {pattern} | {check_status} |\n"
        
        markdown_content += """

### Detailed Service Analysis

"""
        
        for i, service in enumerate(high_priority[:5], 1):
            service_id = service.get('ID', f'Service_{i}')
            title = service.get('Title', 'N/A')
            service_url = service.get('ServiceUrl', 'N/A')
            pattern = service.get('detection_pattern', 'N/A')
            metadata_check = service.get('metadata_check', {})
            
            markdown_content += f"""
#### {i}. {service_id}

**Title:** {title}  
**Service URL:** {service_url}  
**Detection Pattern:** {pattern}  
**Metadata Accessible:** {metadata_check.get('accessible', 'Unknown')}  
"""
            
            if metadata_check.get('has_oauth_hints'):
                markdown_content += f"""**OAuth2 Indicators:** ✅ {', '.join(metadata_check.get('oauth_indicators', []))}  
**Recommendation:** High probability OAuth2 support - test with OAuth2 authentication

"""
            else:
                markdown_content += f"""**OAuth2 Indicators:** ❌ None found  
**Recommendation:** Check service configuration or system-level OAuth2 setup

"""
    else:
        markdown_content += """
❌ **No OAuth2-specific services found in service catalog**

This indicates that:
- OAuth2 is configured at SAP Gateway system level
- Authentication is handled centrally, not per service
- Need to check system-level OAuth2 configuration

"""
    
    markdown_content += f"""

---

## System Configuration Recommendations

### 🔧 SAP System Checks Required

"""
    
    for i, recommendation in enumerate(recommendations, 1):
        markdown_content += f"{i}. {recommendation}\n"
    
    markdown_content += f"""

### 📋 SAP Transaction Codes to Check

| Transaction | Purpose | What to Look For |
|-------------|---------|------------------|
| **SOAUTH2** | OAuth2 Client Configuration | OAuth2 clients, scopes, redirect URIs |
| **/IWFND/MAINT_SERVICE** | Gateway Service Maintenance | Service security settings, authentication methods |
| **SICF** | HTTP Service Configuration | OAuth2 authentication handlers, security settings |
| **SAML2** | SAML Configuration | SAML identity providers for OAuth2 SAML Bearer flow |
| **SM59** | RFC Destinations | OAuth2-enabled RFC connections |

### 🚀 Recommended Implementation Approach

#### Phase 1: System-Level Configuration Check
1. **Check SOAUTH2** - Verify OAuth2 clients are configured
2. **Review /IWFND/MAINT_SERVICE** - Check service security settings
3. **Verify SICF** - Ensure OAuth2 handlers are active

#### Phase 2: Service-Level Testing
1. **Test identified high-priority services** with OAuth2 authentication
2. **Use /IWFND/GW_CLIENT** to test OAuth2 flows
3. **Verify token-based authentication** works

#### Phase 3: Integration Implementation
1. **Configure OAuth2 client applications**
2. **Implement OAuth2 authentication flows**
3. **Test end-to-end OAuth2 integration**

---

## Processing Log

"""
    
    for log_entry in processing_log:
        markdown_content += f"- {log_entry}\n"
    
    markdown_content += f"""

---

## Conclusion

### Current Status
- **Service Catalog Analysis:** Complete
- **High-Priority Services:** {len(high_priority)} identified
- **System Configuration:** Requires manual check

### Next Actions Required

1. **Manual SAP System Check** (High Priority):
   - Login to SAP GUI
   - Check transaction SOAUTH2 for OAuth2 clients
   - Review /IWFND/MAINT_SERVICE for service security

2. **Service Testing** (Medium Priority):
   - Test identified services with OAuth2 authentication
   - Use /IWFND/GW_CLIENT for OAuth2 flow testing

3. **System Integration** (Low Priority):
   - Configure OAuth2 client applications
   - Implement OAuth2 authentication in applications

### Key Insight
**OAuth2 in SAP is typically configured at the system/gateway level, not at individual service level.** The service catalog provides service discovery, but authentication configuration is handled centrally through SAP Gateway and OAuth2 system settings.

---
*This targeted analysis focuses on realistic OAuth2 detection approaches for SAP systems*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("Targeted SAP OAuth2 Detection - Starting focused analysis...")
    print("Looking for high-priority OAuth2 services and system configuration...")
    
    # Get targeted OAuth2 services
    results = get_high_priority_oauth_services()
    
    # Create targeted report
    markdown_report = create_targeted_oauth_report(results)
    
    # Save to file
    output_file = "/home/gyanmis/targeted_oauth_detection_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ Targeted analysis complete! Report saved to: {output_file}")
    print(f"✓ Found {len(results.get('high_priority_services', []))} high-priority OAuth2 services")
    
    # Summary
    high_priority = results.get('high_priority_services', [])
    if high_priority:
        print(f"✅ FOUND: {len(high_priority)} potential OAuth2 services")
        print("🔍 NEXT: Check service metadata and system configuration")
    else:
        print("⚠️  NO OAuth2 services found in catalog")
        print("🔧 NEXT: Check SAP system-level OAuth2 configuration (SOAUTH2, /IWFND/MAINT_SERVICE)")
    
    print("\n" + "="*60)
    print("RECOMMENDED IMMEDIATE ACTION:")
    print("="*60)
    print("1. Check SAP transaction SOAUTH2 for OAuth2 clients")
    print("2. Review /IWFND/MAINT_SERVICE for service security")
    print("3. Verify SICF OAuth2 authentication handlers")
    print("="*60)

if __name__ == "__main__":
    main()
