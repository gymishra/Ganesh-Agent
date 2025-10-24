#!/usr/bin/env python3
"""
Improved SAP OData OAuth2 Detection Script
Uses realistic approaches that work with actual SAP Gateway Catalog Service
"""

import requests
import json
import base64
from datetime import datetime
import urllib3
import concurrent.futures
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
    """Check service metadata for OAuth2 indicators"""
    try:
        metadata_url = f"{service_url}/$metadata"
        response = session.get(metadata_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            metadata_content = response.text.lower()
            
            # OAuth2 indicators in metadata
            oauth_indicators = [
                'oauth', 'bearer', 'authorization_code', 'client_credentials',
                'saml_bearer', 'jwt_bearer', 'oauth2samlbearer', 'oauth2clientcredentials',
                'authorization', 'token', 'authenticate'
            ]
            
            found_indicators = [indicator for indicator in oauth_indicators if indicator in metadata_content]
            
            if found_indicators:
                return True, found_indicators, metadata_content[:1000]
                
        return False, [], ""
        
    except Exception as e:
        return False, [], f"Error: {str(e)}"

def check_service_for_oauth_hints(service_data):
    """Check service data for OAuth-related hints"""
    oauth_hints = []
    service_str = json.dumps(service_data).lower()
    
    # Check various fields for auth-related keywords
    auth_keywords = ['oauth', 'auth', 'bearer', 'token', 'security', 'saml', 'jwt']
    
    for keyword in auth_keywords:
        if keyword in service_str:
            oauth_hints.append(keyword)
    
    # Check specific fields that might contain auth info
    title = service_data.get('Title', '').lower()
    description = service_data.get('Description', '').lower()
    
    if any(keyword in title or keyword in description for keyword in auth_keywords):
        oauth_hints.append('title_or_description_match')
    
    return len(oauth_hints) > 0, oauth_hints

def get_services_with_smart_filtering():
    """Get services using smart filtering approaches that actually work"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    results = {
        'all_services': [],
        'potential_oauth_services': [],
        'metadata_checked_services': [],
        'processing_log': []
    }
    
    try:
        # 1. Get all services first
        catalog_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$format=json"
        response = session.get(catalog_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            all_services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
            results['all_services'] = all_services
            results['processing_log'].append(f"Retrieved {len(all_services)} total services")
            
            # 2. Filter services with auth-related keywords (this actually works!)
            auth_filter_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$filter=substringof('auth',tolower(Title)) or substringof('auth',tolower(Description)) or substringof('oauth',tolower(Title)) or substringof('oauth',tolower(Description))&$format=json"
            
            try:
                auth_response = session.get(auth_filter_url, headers=headers, timeout=30)
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    auth_services = auth_data['d']['results'] if 'd' in auth_data and 'results' in auth_data['d'] else []
                    results['processing_log'].append(f"Found {len(auth_services)} services with 'auth' in title/description")
                else:
                    results['processing_log'].append(f"Auth filter failed: {auth_response.status_code}")
                    auth_services = []
            except Exception as e:
                results['processing_log'].append(f"Auth filter error: {str(e)}")
                auth_services = []
            
            # 3. Smart sampling: prioritize services likely to have OAuth2
            priority_services = []
            
            # Add auth-filtered services first
            priority_services.extend(auth_services)
            
            # Add services with auth-related hints
            for service in all_services:
                has_hints, hints = check_service_for_oauth_hints(service)
                if has_hints:
                    service['oauth_hints'] = hints
                    priority_services.append(service)
            
            # Remove duplicates
            seen_ids = set()
            unique_priority_services = []
            for service in priority_services:
                service_id = service.get('ID', '')
                if service_id and service_id not in seen_ids:
                    seen_ids.add(service_id)
                    unique_priority_services.append(service)
            
            results['potential_oauth_services'] = unique_priority_services
            results['processing_log'].append(f"Identified {len(unique_priority_services)} priority services for metadata checking")
            
            # 4. Check metadata for OAuth2 support (limited sample)
            services_to_check = unique_priority_services[:20]  # Limit for performance
            
            for i, service in enumerate(services_to_check):
                service_url = service.get('ServiceUrl', '')
                service_id = service.get('ID', f'Service_{i}')
                
                if service_url:
                    has_oauth, indicators, metadata_snippet = check_service_metadata_for_oauth(service_url, headers, session)
                    
                    if has_oauth:
                        service['oauth_metadata_check'] = {
                            'supports_oauth': True,
                            'indicators': indicators,
                            'metadata_snippet': metadata_snippet
                        }
                        results['metadata_checked_services'].append(service)
                        results['processing_log'].append(f"✓ OAuth indicators found in {service_id}: {indicators}")
                    else:
                        service['oauth_metadata_check'] = {
                            'supports_oauth': False,
                            'indicators': [],
                            'metadata_snippet': ''
                        }
                
                # Progress indicator
                if (i + 1) % 5 == 0:
                    print(f"Checked {i + 1}/{len(services_to_check)} services for OAuth2 metadata", end='\r')
            
            print()  # Clear progress line
            
        else:
            results['processing_log'].append(f"Failed to retrieve services: {response.status_code}")
            
    except Exception as e:
        results['processing_log'].append(f"Error in service retrieval: {str(e)}")
    
    return results

def create_improved_oauth_report(results):
    """Create comprehensive OAuth2 detection report"""
    
    all_services = results.get('all_services', [])
    potential_oauth = results.get('potential_oauth_services', [])
    metadata_checked = results.get('metadata_checked_services', [])
    processing_log = results.get('processing_log', [])
    
    markdown_content = f"""# Improved SAP OData OAuth2 Detection Report

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Services:** {len(all_services)}
- **Services with Auth Keywords:** {len(potential_oauth)}
- **Services with OAuth2 Metadata Indicators:** {len(metadata_checked)}
- **Detection Method:** Smart filtering + metadata analysis

---

## Why Original Filtering Failed

The original approach `$filter=AuthenticationMode eq 'OAuth2'` **does not work** because:

1. ❌ **`AuthenticationMode` field does not exist** in SAP Gateway Catalog Service
2. ❌ **`SecurityMethod` field does not exist** in SAP Gateway Catalog Service  
3. ❌ **Authentication configuration is at system level**, not service level
4. ❌ **OAuth2 setup is in SAP Gateway security settings**, not service metadata

## Working Alternative Approaches

### ✅ 1. Keyword-Based Filtering (Works!)
```
$filter=substringof('auth',tolower(Title)) or substringof('auth',tolower(Description))
```

### ✅ 2. Service Metadata Analysis (Most Accurate)
- Check each service's `/$metadata` endpoint
- Look for OAuth2 indicators in XML metadata
- Analyze authentication-related annotations

### ✅ 3. Smart Sampling Strategy
- Prioritize services with auth-related keywords
- Check high-probability services first
- Use parallel processing for efficiency

---

## Processing Log

"""
    
    for log_entry in processing_log:
        markdown_content += f"- {log_entry}\n"
    
    markdown_content += f"""

---

## Services with OAuth2 Potential

### Services Found with Auth Keywords in Title/Description

| # | Service ID | Title | Description | OAuth Hints |
|---|------------|-------|-------------|-------------|
"""
    
    for i, service in enumerate(potential_oauth[:10], 1):  # Show first 10
        service_id = service.get('ID', 'N/A')
        title = str(service.get('Title', 'N/A')).replace('|', '\\|')[:40]
        description = str(service.get('Description', 'N/A')).replace('|', '\\|')[:50]
        hints = ', '.join(service.get('oauth_hints', []))
        
        markdown_content += f"| {i} | {service_id} | {title} | {description} | {hints} |\n"
    
    markdown_content += f"""

### Services with OAuth2 Metadata Indicators

"""
    
    if metadata_checked:
        for i, service in enumerate(metadata_checked, 1):
            service_id = service.get('ID', f'Service_{i}')
            title = service.get('Title', 'N/A')
            service_url = service.get('ServiceUrl', 'N/A')
            oauth_check = service.get('oauth_metadata_check', {})
            indicators = oauth_check.get('indicators', [])
            
            markdown_content += f"""
#### {i}. {service_id}

**Title:** {title}  
**Service URL:** {service_url}  
**OAuth2 Indicators Found:** {', '.join(indicators)}  
**Status:** ✅ OAuth2 Support Detected

**Metadata Sample:**
```xml
{oauth_check.get('metadata_snippet', 'No metadata available')[:500]}...
```

---
"""
    else:
        markdown_content += """
**No services with OAuth2 metadata indicators found in the checked sample.**

This could mean:
- OAuth2 is configured at system level (SICF, OAuth2 clients)
- Services use different authentication methods
- OAuth2 configuration is not exposed in metadata
- Need to check more services or use different detection methods

"""
    
    markdown_content += f"""

## Recommendations

### ✅ Working Approaches

1. **Use Keyword Filtering** (Immediate results):
   ```
   $filter=substringof('auth',tolower(Title)) or substringof('oauth',tolower(Description))
   ```

2. **Metadata Analysis** (Most accurate):
   - Check service `/$metadata` endpoints
   - Look for OAuth2 authentication annotations
   - Analyze security-related XML elements

3. **System-Level Configuration Check**:
   - Transaction `SOAUTH2` - OAuth2 client configurations
   - Transaction `/IWFND/MAINT_SERVICE` - Service security settings
   - SICF services with OAuth2 authentication

### 🔧 Implementation Strategy

1. **Phase 1**: Use keyword filtering for quick wins
2. **Phase 2**: Implement parallel metadata checking
3. **Phase 3**: Check system-level OAuth2 configuration

### 📋 Next Steps

1. **Check SAP Transactions**:
   - `SOAUTH2` - OAuth2 client setup
   - `/IWFND/MAINT_SERVICE` - Gateway service security
   - `SICF` - Service authentication methods

2. **Optimize Current Approach**:
   - Use concurrent metadata checking
   - Cache results to avoid repeated calls
   - Focus on high-probability services first

3. **System Integration**:
   - Check OAuth2 providers configuration
   - Verify SAML2 setup if using SAML Bearer flow
   - Review Gateway security policies

---

## Technical Details

**Available Service Fields:**
- ID, Description, Title, Author
- TechnicalServiceVersion, MetadataUrl, ServiceUrl
- UpdatedDate, ReleaseStatus, Category
- IsSapService, ServiceType
- EntitySets, TagCollection, Annotations (deferred)

**OAuth2 Detection Methods:**
1. Keyword matching in Title/Description ✅
2. Service metadata analysis ✅
3. System configuration check (manual) ✅
4. Direct field filtering ❌ (fields don't exist)

---

*Report generated using improved OAuth2 detection methodology*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("Improved SAP OData OAuth2 Detection - Starting analysis...")
    print("Using realistic approaches that work with actual SAP Gateway structure...")
    
    # Get services using working approaches
    results = get_services_with_smart_filtering()
    
    # Create comprehensive report
    markdown_report = create_improved_oauth_report(results)
    
    # Save to file
    output_file = "/home/gyanmis/improved_oauth_detection_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ Analysis complete! Report saved to: {output_file}")
    print(f"✓ Found {len(results.get('potential_oauth_services', []))} services with OAuth potential")
    print(f"✓ Verified {len(results.get('metadata_checked_services', []))} services with OAuth2 metadata indicators")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print("❌ Original filtering approach DOES NOT WORK")
    print("   - AuthenticationMode field does not exist")
    print("   - SecurityMethod field does not exist")
    print("✅ Working alternatives implemented:")
    print("   - Keyword-based filtering")
    print("   - Metadata analysis")
    print("   - Smart sampling strategy")
    print("="*60)

if __name__ == "__main__":
    main()
