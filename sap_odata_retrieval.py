#!/usr/bin/env python3
"""
SAP OData Services Retrieval Script
Retrieves OData services from SAP Gateway Service Catalog via REST API
"""

import requests
import json
import base64
from datetime import datetime
import urllib3

# Disable SSL warnings for self-signed certificates (common in SAP systems)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SAP System Configuration
SAP_BASE_URL = "https://vhcals4hci.awspoc.club"
USERNAME = "bpinst"
PASSWORD = "Welcome1"

# Service Catalog Endpoints to try
ENDPOINTS = [
    "/sap/opu/odata/iwfnd/catalogservice;v=2/ServiceCollection?$format=json",
    "/sap/opu/odata/iwfnd/catalogservice/ServiceCollection?$format=json",
    "/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$format=json",
    "/sap/bc/rest/iwfnd/catalogservice/ServiceCollection?$format=json"
]

def create_auth_header(username, password):
    """Create basic authentication header"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

def retrieve_odata_services():
    """Retrieve OData services from SAP Gateway"""
    
    headers = {
        'Authorization': create_auth_header(USERNAME, PASSWORD),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    session = requests.Session()
    session.verify = False  # Disable SSL verification for self-signed certs
    
    services_data = []
    
    print("Attempting to connect to SAP system...")
    print(f"Base URL: {SAP_BASE_URL}")
    
    for endpoint in ENDPOINTS:
        full_url = SAP_BASE_URL + endpoint
        print(f"\nTrying endpoint: {endpoint}")
        
        try:
            response = session.get(full_url, headers=headers, timeout=30)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Successfully connected!")
                
                try:
                    data = response.json()
                    
                    # Handle different response structures
                    if 'd' in data and 'results' in data['d']:
                        services_data = data['d']['results']
                    elif 'value' in data:
                        services_data = data['value']
                    elif 'results' in data:
                        services_data = data['results']
                    else:
                        services_data = data
                    
                    print(f"Found {len(services_data)} services")
                    return services_data
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print("Response content:", response.text[:500])
                    
            elif response.status_code == 401:
                print("✗ Authentication failed - check credentials")
            elif response.status_code == 404:
                print("✗ Endpoint not found")
            else:
                print(f"✗ HTTP Error: {response.status_code}")
                print("Response:", response.text[:200])
                
        except requests.exceptions.ConnectionError:
            print("✗ Connection failed - check URL and network connectivity")
        except requests.exceptions.Timeout:
            print("✗ Request timeout")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    return []

def create_markdown_report(services_data):
    """Create markdown report from services data"""
    
    if not services_data:
        return """# SAP OData Services Report

## Status: No Services Retrieved

Unfortunately, no OData services could be retrieved from the SAP system.

**Possible reasons:**
- Authentication issues
- Network connectivity problems
- Service catalog not accessible via REST API
- Different endpoint structure

**Recommendations:**
1. Verify credentials and system accessibility
2. Check if Gateway services are properly configured
3. Try accessing via SAP GUI transaction IWFND/MAIN_SERVICE
4. Contact SAP system administrator for assistance

---
*Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    markdown_content = f"""# SAP OData Services Report

**System:** {SAP_BASE_URL}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Services:** {len(services_data)}

---

## Service Catalog

| # | Service ID | Service Version | Title | Description |
|---|------------|----------------|-------|-------------|
"""
    
    for i, service in enumerate(services_data, 1):
        # Handle different possible field names
        service_id = service.get('ServiceId', service.get('ID', service.get('service_id', 'N/A')))
        version = service.get('ServiceVersion', service.get('Version', service.get('version', 'N/A')))
        title = service.get('Title', service.get('title', service.get('ServiceTitle', 'N/A')))
        description = service.get('Description', service.get('description', service.get('ServiceDescription', 'N/A')))
        
        # Clean up text for markdown
        title = str(title).replace('|', '\\|').replace('\n', ' ')[:50]
        description = str(description).replace('|', '\\|').replace('\n', ' ')[:100]
        
        markdown_content += f"| {i} | {service_id} | {version} | {title} | {description} |\n"
    
    markdown_content += f"""

---

## Detailed Service Information

"""
    
    for i, service in enumerate(services_data, 1):
        service_id = service.get('ServiceId', service.get('ID', service.get('service_id', f'Service_{i}')))
        markdown_content += f"""
### {i}. {service_id}

```json
{json.dumps(service, indent=2)}
```

---
"""
    
    markdown_content += f"""

## Summary

- **Total Services Found:** {len(services_data)}
- **System URL:** {SAP_BASE_URL}
- **Retrieval Method:** REST API via Gateway Service Catalog
- **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*This report was automatically generated using the SAP Gateway Service Catalog REST API*
"""
    
    return markdown_content

def main():
    """Main execution function"""
    print("SAP OData Services Retrieval Tool")
    print("=" * 40)
    
    # Retrieve services
    services = retrieve_odata_services()
    
    # Create markdown report
    markdown_report = create_markdown_report(services)
    
    # Save to file
    output_file = "/home/gyanmis/sap_odata_services_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✓ Report saved to: {output_file}")
    print(f"✓ Found {len(services)} OData services")

if __name__ == "__main__":
    main()
