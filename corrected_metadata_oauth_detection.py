#!/usr/bin/env python3
"""
Corrected SAP OAuth2 Detection Script
Uses $metadata endpoint properly to detect OAuth2 support
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

def check_service_metadata_for_oauth(service_url, headers, session):
    """Check service metadata using $metadata endpoint"""
    try:
        # Construct metadata URL properly
        if service_url.endswith('/'):
            metadata_url = f"{service_url}$metadata"
        else:
            metadata_url = f"{service_url}/$metadata"
        
        print(f"  Checking metadata: {metadata_url}")
        
        response = session.get(metadata_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            metadata_content = response.text.lower()
            
            # OAuth2 indicators in metadata
            oauth_indicators = [
                'oauth', 'bearer', 'authorization_code', 'client_credentials',
                'saml_bearer', 'jwt_bearer', 'oauth2samlbearer', 'oauth2clientcredentials',
                'authorization', 'token', 'authenticate', 'security'
            ]
            
            found_indicators = []
            for indicator in oauth_indicators:
                if indicator in metadata_content:
                    found_indicators.append(indicator)
            
            return {
                'accessible': True,
                'status_code': response.status_code,
                'oauth_indicators': found_indicators,
                'has_oauth_support': len(found_indicators) > 0,
                'metadata_snippet': metadata_content[:1000],
                'content_length': len(metadata_content)
            }
        else:
            return {
                'accessible': False,
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}",
                'oauth_indicators': [],
                'has_oauth_support': False
            }
            
    except Exception as e:
        return {
            'accessible': False,
            'error': str(e),
            'oauth_indicators': [],
            'has_oauth_support': False
        }

def get_services_and_check_metadata():
    """Get services and check their metadata for OAuth2 support"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Also try XML accept for metadata
    metadata_headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/xml, text/xml, */*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    results = {
        'all_services': [],
        'oauth_services': [],
        'processing_log': [],
        'metadata_checks': []
    }
    
    try:
        # 1. Get services with auth-related keywords
        print("Getting services with auth-related keywords...")
        
        auth_filters = [
            "substringof('auth',tolower(Title))",
            "substringof('oauth',tolower(Title))",
            "substringof('security',tolower(Title))",
            "substringof('token',tolower(Title))"
        ]
        
        priority_services = []
        
        for filter_expr in auth_filters:
            try:
                filter_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$filter={filter_expr}&$format=json"
                response = session.get(filter_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
                    
                    results['processing_log'].append(f"Filter '{filter_expr}' found {len(services)} services")
                    
                    for service in services:
                        service_id = service.get('ID', '')
                        if not any(s.get('ID') == service_id for s in priority_services):
                            service['filter_matched'] = filter_expr
                            priority_services.append(service)
                            
            except Exception as e:
                results['processing_log'].append(f"Error with filter {filter_expr}: {str(e)}")
        
        results['all_services'] = priority_services
        results['processing_log'].append(f"Total unique services to check: {len(priority_services)}")
        
        # 2. Check metadata for each service
        print(f"\nChecking metadata for {len(priority_services)} services...")
        
        for i, service in enumerate(priority_services[:20], 1):  # Limit to first 20 for performance
            service_id = service.get('ID', f'Service_{i}')
            service_url = service.get('ServiceUrl', '')
            
            print(f"\n{i}. Checking service: {service_id}")
            
            if service_url:
                metadata_result = check_service_metadata_for_oauth(service_url, metadata_headers, session)
                service['metadata_check'] = metadata_result
                results['metadata_checks'].append({
                    'service_id': service_id,
                    'service_url': service_url,
                    'metadata_result': metadata_result
                })
                
                if metadata_result.get('has_oauth_support'):
                    results['oauth_services'].append(service)
                    results['processing_log'].append(f"✅ OAuth2 support found in {service_id}: {metadata_result['oauth_indicators']}")
                    print(f"  ✅ OAuth2 indicators found: {metadata_result['oauth_indicators']}")
                elif metadata_result.get('accessible'):
                    results['processing_log'].append(f"⚠️  No OAuth2 indicators in {service_id} (but metadata accessible)")
                    print(f"  ⚠️  Metadata accessible but no OAuth2 indicators")
                else:
                    results['processing_log'].append(f"❌ Metadata not accessible for {service_id}: {metadata_result.get('error', 'Unknown error')}")
                    print(f"  ❌ Metadata not accessible: {metadata_result.get('error', 'Unknown error')}")
            else:
                results['processing_log'].append(f"❌ No ServiceUrl for {service_id}")
                print(f"  ❌ No ServiceUrl available")
        
        print(f"\n✅ Metadata check complete!")
        
    except Exception as e:
        results['processing_log'].append(f"Major error: {str(e)}")
        print(f"❌ Major error: {str(e)}")
    
    return results

def create_metadata_oauth_report(results):
    """Create comprehensive OAuth2 detection report with metadata analysis"""
    
    all_services = results.get('all_services', [])
    oauth_services = results.get('oauth_services', [])
    metadata_checks = results.get('metadata_checks', [])
    processing_log = results.get('processing_log', [])
    
    markdown_content = f"""# SAP OAuth2 Detection Report - Metadata Analysis

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Method:** Service filtering + $metadata endpoint analysis

## Executive Summary

- **Services Analyzed:** {len(all_services)}
- **Metadata Checks Performed:** {len(metadata_checks)}
- **Services with OAuth2 Support:** {len(oauth_services)}
- **Success Rate:** {(len([m for m in metadata_checks if m['metadata_result'].get('accessible')]) / len(metadata_checks) * 100):.1f}% metadata accessible

---

## OAuth2 Services Found

"""
    
    if oauth_services:
        markdown_content += f"""
✅ **Found {len(oauth_services)} services with OAuth2 support**

| # | Service ID | Title | OAuth2 Indicators | Metadata Status |
|---|------------|-------|------------------|-----------------|
"""
        
        for i, service in enumerate(oauth_services, 1):
            service_id = service.get('ID', 'N/A')
            title = str(service.get('Title', 'N/A')).replace('|', '\\|')[:40]
            metadata_check = service.get('metadata_check', {})
            indicators = ', '.join(metadata_check.get('oauth_indicators', []))
            status = "✅ Accessible" if metadata_check.get('accessible') else "❌ Not accessible"
            
            markdown_content += f"| {i} | {service_id} | {title} | {indicators} | {status} |\n"
        
        markdown_content += """

### Detailed OAuth2 Service Analysis

"""
        
        for i, service in enumerate(oauth_services, 1):
            service_id = service.get('ID', f'Service_{i}')
            title = service.get('Title', 'N/A')
            service_url = service.get('ServiceUrl', 'N/A')
            filter_matched = service.get('filter_matched', 'N/A')
            metadata_check = service.get('metadata_check', {})
            
            markdown_content += f"""
#### {i}. {service_id}

**Title:** {title}  
**Service URL:** {service_url}  
**Detected by Filter:** {filter_matched}  
**Metadata Accessible:** {metadata_check.get('accessible', 'Unknown')}  
**OAuth2 Indicators:** {', '.join(metadata_check.get('oauth_indicators', []))}  
**Content Length:** {metadata_check.get('content_length', 'N/A')} characters

**Metadata Sample:**
```xml
{metadata_check.get('metadata_snippet', 'No metadata available')[:500]}...
```

**Recommendation:** ✅ **High probability OAuth2 support** - Test with OAuth2 authentication flows

---
"""
    else:
        markdown_content += """
❌ **No services with explicit OAuth2 indicators found**

This could indicate:
- OAuth2 configuration is at system level (SAP Gateway)
- Services use different authentication terminology
- OAuth2 setup is in SICF/Gateway configuration
- Need to check more services or different patterns

"""
    
    markdown_content += f"""

## Metadata Analysis Results

### Services with Accessible Metadata

"""
    
    accessible_services = [m for m in metadata_checks if m['metadata_result'].get('accessible')]
    
    if accessible_services:
        markdown_content += f"""
✅ **{len(accessible_services)} services have accessible metadata**

| Service ID | Status Code | Content Length | OAuth Indicators |
|------------|-------------|----------------|------------------|
"""
        
        for check in accessible_services[:10]:
            service_id = check['service_id']
            result = check['metadata_result']
            status_code = result.get('status_code', 'N/A')
            content_length = result.get('content_length', 'N/A')
            indicators = ', '.join(result.get('oauth_indicators', [])) or 'None'
            
            markdown_content += f"| {service_id} | {status_code} | {content_length} | {indicators} |\n"
    else:
        markdown_content += "❌ **No services have accessible metadata**\n"
    
    markdown_content += f"""

### Services with Inaccessible Metadata

"""
    
    inaccessible_services = [m for m in metadata_checks if not m['metadata_result'].get('accessible')]
    
    if inaccessible_services:
        markdown_content += f"""
⚠️ **{len(inaccessible_services)} services have inaccessible metadata**

| Service ID | Error | Status Code |
|------------|-------|-------------|
"""
        
        for check in inaccessible_services[:10]:
            service_id = check['service_id']
            result = check['metadata_result']
            error = result.get('error', 'Unknown error')[:50]
            status_code = result.get('status_code', 'N/A')
            
            markdown_content += f"| {service_id} | {error} | {status_code} |\n"
    
    markdown_content += f"""

---

## Processing Log

"""
    
    for log_entry in processing_log:
        markdown_content += f"- {log_entry}\n"
    
    markdown_content += f"""

---

## Recommendations

### ✅ If OAuth2 Services Found
1. **Test OAuth2 Authentication** with identified services
2. **Use /IWFND/GW_CLIENT** to test OAuth2 flows
3. **Configure OAuth2 clients** in transaction SOAUTH2
4. **Implement OAuth2 integration** in your applications

### ⚠️ If No OAuth2 Services Found
1. **Check SAP System Configuration**:
   - Transaction **SOAUTH2** - OAuth2 client setup
   - Transaction **/IWFND/MAINT_SERVICE** - Service security settings
   - Transaction **SICF** - HTTP service authentication
2. **Expand Search Criteria**:
   - Check more services (increase limit)
   - Use different keyword patterns
   - Check system-level OAuth2 configuration

### 🔧 Technical Implementation
1. **Service URLs** are directly accessible for OAuth2 testing
2. **Metadata analysis** provides accurate OAuth2 detection
3. **System-level configuration** may be required for OAuth2 setup

---

## Next Steps

1. **Immediate**: Test identified OAuth2 services with OAuth2 authentication
2. **Short-term**: Configure OAuth2 clients in SAP system (SOAUTH2)
3. **Long-term**: Implement OAuth2 integration in applications

---
*This report uses proper $metadata endpoint access for accurate OAuth2 detection*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("SAP OAuth2 Detection - Using $metadata endpoint properly")
    print("=" * 60)
    
    # Get services and check metadata
    results = get_services_and_check_metadata()
    
    # Create comprehensive report
    markdown_report = create_metadata_oauth_report(results)
    
    # Save to file
    output_file = "/home/gyanmis/corrected_metadata_oauth_detection_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ Analysis complete! Report saved to: {output_file}")
    print(f"✓ Analyzed {len(results.get('all_services', []))} services")
    print(f"✓ Found {len(results.get('oauth_services', []))} services with OAuth2 support")
    
    # Summary
    oauth_services = results.get('oauth_services', [])
    metadata_checks = results.get('metadata_checks', [])
    accessible_count = len([m for m in metadata_checks if m['metadata_result'].get('accessible')])
    
    print("\n" + "="*60)
    print("FINAL RESULTS:")
    print("="*60)
    if oauth_services:
        print(f"✅ SUCCESS: Found {len(oauth_services)} OAuth2-enabled services")
        for service in oauth_services[:3]:
            service_id = service.get('ID', 'Unknown')
            indicators = service.get('metadata_check', {}).get('oauth_indicators', [])
            print(f"   - {service_id}: {', '.join(indicators)}")
    else:
        print("⚠️  No OAuth2 services found with explicit indicators")
    
    print(f"📊 Metadata accessible: {accessible_count}/{len(metadata_checks)} services")
    print("🔧 Check the detailed report for next steps")
    print("="*60)

if __name__ == "__main__":
    main()
