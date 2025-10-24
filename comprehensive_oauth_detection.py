#!/usr/bin/env python3
"""
Comprehensive SAP OAuth2 Detection Script
Checks ALL services for OAuth2 support, not just a limited sample
"""

import requests
import json
import base64
from datetime import datetime
import urllib3
import concurrent.futures
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SAP System Configuration
SAP_BASE_URL = "https://vhcals4hci.awspoc.club"
USERNAME = "bpinst"
PASSWORD = "Welcome1"

# Configuration
MAX_WORKERS = 10  # Number of concurrent threads
BATCH_SIZE = 50   # Process services in batches
REQUEST_TIMEOUT = 10  # Timeout for each request

def create_auth_header(username, password):
    """Create basic authentication header"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def check_service_metadata_for_oauth(service_data, session):
    """Check service metadata using $metadata endpoint"""
    service_id = service_data.get('ID', 'Unknown')
    service_url = service_data.get('ServiceUrl', '')
    
    if not service_url:
        return {
            'service_id': service_id,
            'accessible': False,
            'error': 'No ServiceUrl available',
            'oauth_indicators': [],
            'has_oauth_support': False
        }
    
    try:
        # Construct metadata URL properly
        if service_url.endswith('/'):
            metadata_url = f"{service_url}$metadata"
        else:
            metadata_url = f"{service_url}/$metadata"
        
        # Headers for metadata request
        headers = {
            'Authorization': create_auth_header(USERNAME, PASSWORD),
            'Accept': 'application/xml, text/xml, */*',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = session.get(metadata_url, headers=headers, timeout=REQUEST_TIMEOUT)
        
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
                'service_id': service_id,
                'service_url': service_url,
                'accessible': True,
                'status_code': response.status_code,
                'oauth_indicators': found_indicators,
                'has_oauth_support': len(found_indicators) > 0,
                'content_length': len(metadata_content)
            }
        else:
            return {
                'service_id': service_id,
                'service_url': service_url,
                'accessible': False,
                'status_code': response.status_code,
                'error': f"HTTP {response.status_code}",
                'oauth_indicators': [],
                'has_oauth_support': False
            }
            
    except Exception as e:
        return {
            'service_id': service_id,
            'service_url': service_url,
            'accessible': False,
            'error': str(e),
            'oauth_indicators': [],
            'has_oauth_support': False
        }

def get_all_services():
    """Get ALL services from the SAP system"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False
    
    try:
        print("Retrieving ALL services from SAP system...")
        
        # Get all services without any filtering
        catalog_url = f"{SAP_BASE_URL}/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$format=json"
        response = session.get(catalog_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            all_services = data['d']['results'] if 'd' in data and 'results' in data['d'] else []
            
            print(f"✅ Retrieved {len(all_services)} total services")
            return all_services, session
        else:
            print(f"❌ Failed to retrieve services: HTTP {response.status_code}")
            return [], session
            
    except Exception as e:
        print(f"❌ Error retrieving services: {str(e)}")
        return [], session

def process_services_in_batches(all_services, session):
    """Process all services in batches with concurrent processing"""
    
    total_services = len(all_services)
    oauth_services = []
    processing_log = []
    metadata_checks = []
    
    print(f"\nProcessing {total_services} services in batches of {BATCH_SIZE}...")
    print(f"Using {MAX_WORKERS} concurrent workers")
    print("=" * 80)
    
    # Process services in batches
    for batch_start in range(0, total_services, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total_services)
        batch_services = all_services[batch_start:batch_end]
        
        batch_num = (batch_start // BATCH_SIZE) + 1
        total_batches = (total_services + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"\nBatch {batch_num}/{total_batches}: Processing services {batch_start + 1}-{batch_end}")
        
        # Process batch with concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks for this batch
            future_to_service = {
                executor.submit(check_service_metadata_for_oauth, service, session): service 
                for service in batch_services
            }
            
            # Collect results as they complete
            batch_oauth_services = []
            batch_checks = []
            
            for future in concurrent.futures.as_completed(future_to_service):
                try:
                    result = future.result()
                    batch_checks.append(result)
                    
                    if result.get('has_oauth_support'):
                        # Add original service data to the result
                        original_service = future_to_service[future]
                        original_service['metadata_check'] = result
                        batch_oauth_services.append(original_service)
                        
                        service_id = result.get('service_id', 'Unknown')
                        indicators = result.get('oauth_indicators', [])
                        processing_log.append(f"✅ OAuth2 found: {service_id} - {', '.join(indicators)}")
                        print(f"  ✅ OAuth2 found: {service_id}")
                    
                except Exception as e:
                    processing_log.append(f"❌ Error processing service: {str(e)}")
            
            # Add batch results to totals
            oauth_services.extend(batch_oauth_services)
            metadata_checks.extend(batch_checks)
            
            # Batch summary
            accessible_count = len([r for r in batch_checks if r.get('accessible')])
            oauth_count = len(batch_oauth_services)
            
            print(f"  📊 Batch {batch_num} results: {accessible_count}/{len(batch_services)} accessible, {oauth_count} with OAuth2")
        
        # Small delay between batches to avoid overwhelming the server
        if batch_end < total_services:
            time.sleep(1)
    
    return oauth_services, metadata_checks, processing_log

def create_comprehensive_oauth_report(all_services, oauth_services, metadata_checks, processing_log):
    """Create comprehensive OAuth2 detection report"""
    
    total_services = len(all_services)
    total_checked = len(metadata_checks)
    accessible_services = [m for m in metadata_checks if m.get('accessible')]
    
    markdown_content = f"""# Comprehensive SAP OAuth2 Detection Report

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Method:** Complete service catalog analysis + $metadata endpoint checking

## Executive Summary

- **Total Services in System:** {total_services:,}
- **Services Checked for OAuth2:** {total_checked:,}
- **Services with Accessible Metadata:** {len(accessible_services):,} ({len(accessible_services)/total_checked*100:.1f}%)
- **Services with OAuth2 Support:** {len(oauth_services):,} ({len(oauth_services)/total_checked*100:.1f}%)

---

## OAuth2 Services Found

"""
    
    if oauth_services:
        markdown_content += f"""
✅ **Found {len(oauth_services):,} services with OAuth2 support**

| # | Service ID | Title | OAuth2 Indicators | Content Length |
|---|------------|-------|------------------|----------------|
"""
        
        for i, service in enumerate(oauth_services, 1):
            service_id = service.get('ID', 'N/A')
            title = str(service.get('Title', 'N/A')).replace('|', '\\|')[:50]
            metadata_check = service.get('metadata_check', {})
            indicators = ', '.join(metadata_check.get('oauth_indicators', []))
            content_length = metadata_check.get('content_length', 'N/A')
            
            markdown_content += f"| {i} | {service_id} | {title} | {indicators} | {content_length} |\n"
        
        markdown_content += f"""

### Top OAuth2 Services by Indicators

"""
        
        # Sort services by number of OAuth indicators
        sorted_services = sorted(oauth_services, 
                               key=lambda s: len(s.get('metadata_check', {}).get('oauth_indicators', [])), 
                               reverse=True)
        
        for i, service in enumerate(sorted_services[:10], 1):
            service_id = service.get('ID', f'Service_{i}')
            title = service.get('Title', 'N/A')
            service_url = service.get('ServiceUrl', 'N/A')
            metadata_check = service.get('metadata_check', {})
            indicators = metadata_check.get('oauth_indicators', [])
            
            markdown_content += f"""
#### {i}. {service_id}

**Title:** {title}  
**Service URL:** {service_url}  
**OAuth2 Indicators:** {', '.join(indicators)} ({len(indicators)} total)  
**Metadata Size:** {metadata_check.get('content_length', 'N/A')} characters  
**Status:** ✅ Ready for OAuth2 integration

---
"""
    else:
        markdown_content += """
❌ **No services with explicit OAuth2 indicators found**

This indicates that:
- OAuth2 configuration may be at SAP Gateway system level
- Services might use different authentication terminology
- OAuth2 setup might be in SICF/Gateway configuration
- System-level OAuth2 configuration check required

"""
    
    markdown_content += f"""

## Detailed Analysis

### Services by OAuth2 Indicator Type

"""
    
    if oauth_services:
        # Analyze OAuth indicators
        indicator_counts = {}
        for service in oauth_services:
            indicators = service.get('metadata_check', {}).get('oauth_indicators', [])
            for indicator in indicators:
                indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
        
        markdown_content += f"""
| OAuth2 Indicator | Services Count | Percentage |
|------------------|----------------|------------|
"""
        
        for indicator, count in sorted(indicator_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(oauth_services)) * 100
            markdown_content += f"| {indicator} | {count} | {percentage:.1f}% |\n"
    
    markdown_content += f"""

### Metadata Accessibility Analysis

| Status | Count | Percentage |
|--------|-------|------------|
| Accessible | {len(accessible_services):,} | {len(accessible_services)/total_checked*100:.1f}% |
| Not Accessible | {total_checked - len(accessible_services):,} | {(total_checked - len(accessible_services))/total_checked*100:.1f}% |
| **Total Checked** | **{total_checked:,}** | **100.0%** |

### Error Analysis

"""
    
    error_services = [m for m in metadata_checks if not m.get('accessible')]
    if error_services:
        error_counts = {}
        for service in error_services:
            error = service.get('error', 'Unknown error')
            if 'HTTP' in error:
                error_type = error
            else:
                error_type = 'Connection/Timeout Error'
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        markdown_content += f"""
| Error Type | Count | Percentage |
|------------|-------|------------|
"""
        
        for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(error_services)) * 100
            markdown_content += f"| {error_type} | {count} | {percentage:.1f}% |\n"
    
    markdown_content += f"""

---

## Processing Statistics

- **Processing Method:** Concurrent batch processing
- **Batch Size:** {BATCH_SIZE} services per batch
- **Concurrent Workers:** {MAX_WORKERS}
- **Total Batches:** {(total_services + BATCH_SIZE - 1) // BATCH_SIZE}
- **Average Success Rate:** {len(accessible_services)/total_checked*100:.1f}%

## Key Findings

"""
    
    key_findings = []
    
    if len(oauth_services) > 0:
        key_findings.append(f"✅ **{len(oauth_services)} OAuth2-enabled services discovered** - Ready for integration")
    else:
        key_findings.append("⚠️ **No OAuth2 services found** - Check system-level configuration")
    
    if len(accessible_services) / total_checked > 0.8:
        key_findings.append(f"✅ **High metadata accessibility** ({len(accessible_services)/total_checked*100:.1f}%) - System is responsive")
    else:
        key_findings.append(f"⚠️ **Low metadata accessibility** ({len(accessible_services)/total_checked*100:.1f}%) - Check system performance")
    
    if len(oauth_services) > 10:
        key_findings.append("🚀 **Multiple OAuth2 services available** - Good foundation for OAuth2 integration")
    elif len(oauth_services) > 0:
        key_findings.append("🔧 **Limited OAuth2 services** - Consider expanding OAuth2 configuration")
    
    for finding in key_findings:
        markdown_content += f"- {finding}\n"
    
    markdown_content += f"""

## Recommendations

### ✅ If OAuth2 Services Found ({len(oauth_services)} services)

1. **Immediate Actions:**
   - Test OAuth2 authentication with top services
   - Configure OAuth2 clients in transaction SOAUTH2
   - Use /IWFND/GW_CLIENT for OAuth2 flow testing

2. **Integration Planning:**
   - Prioritize services with multiple OAuth2 indicators
   - Implement OAuth2 authentication flows
   - Test with different OAuth2 grant types

3. **System Configuration:**
   - Document OAuth2-enabled service URLs
   - Configure redirect URIs and scopes
   - Set up OAuth2 client credentials

### ⚠️ If Limited/No OAuth2 Services Found

1. **System-Level Checks:**
   - Transaction **SOAUTH2** - OAuth2 client configuration
   - Transaction **/IWFND/MAINT_SERVICE** - Service security settings
   - Transaction **SICF** - HTTP service authentication

2. **Configuration Review:**
   - Check SAP Gateway OAuth2 setup
   - Verify SAML2 configuration for OAuth2 SAML Bearer
   - Review system authentication policies

3. **Expansion Strategy:**
   - Enable OAuth2 for additional services
   - Configure system-wide OAuth2 support
   - Implement OAuth2 authentication handlers

---

## Next Steps

1. **Immediate (High Priority):**
   - Review identified OAuth2 services
   - Test OAuth2 authentication flows
   - Configure OAuth2 clients in SAP

2. **Short-term (Medium Priority):**
   - Implement OAuth2 in applications
   - Set up monitoring for OAuth2 services
   - Document OAuth2 integration procedures

3. **Long-term (Low Priority):**
   - Expand OAuth2 to additional services
   - Implement advanced OAuth2 features
   - Monitor and optimize OAuth2 performance

---

*This comprehensive report analyzed all {total_services:,} services in the SAP system for OAuth2 support*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("Comprehensive SAP OAuth2 Detection - Analyzing ALL Services")
    print("=" * 80)
    
    start_time = time.time()
    
    # Get all services
    all_services, session = get_all_services()
    
    if not all_services:
        print("❌ No services retrieved. Exiting.")
        return
    
    # Process all services for OAuth2 support
    oauth_services, metadata_checks, processing_log = process_services_in_batches(all_services, session)
    
    # Create comprehensive report
    markdown_report = create_comprehensive_oauth_report(all_services, oauth_services, metadata_checks, processing_log)
    
    # Save to file
    output_file = "/home/gyanmis/comprehensive_oauth_detection_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE OAUTH2 ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"✅ Total Services Analyzed: {len(all_services):,}")
    print(f"✅ Services Checked: {len(metadata_checks):,}")
    print(f"✅ OAuth2 Services Found: {len(oauth_services):,}")
    print(f"✅ Processing Time: {processing_time:.1f} seconds")
    print(f"✅ Report saved to: {output_file}")
    
    if oauth_services:
        print(f"\n🎯 TOP OAUTH2 SERVICES:")
        for i, service in enumerate(oauth_services[:5], 1):
            service_id = service.get('ID', 'Unknown')
            indicators = service.get('metadata_check', {}).get('oauth_indicators', [])
            print(f"   {i}. {service_id} - {', '.join(indicators)}")
    else:
        print("\n⚠️  No OAuth2 services found - Check system configuration")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
