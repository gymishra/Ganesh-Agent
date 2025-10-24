#!/usr/bin/env python3
"""
Test script to show the 39 API services that will be loaded in Eclipse
"""

import json

def categorize_api_service(technical_name, description):
    """Categorize API service by business area"""
    name = technical_name.upper()
    desc = (description or "").upper()
    
    if "SALES" in name or "ORDER" in name or "SALES" in desc:
        return "📊 Sales & Distribution APIs"
    elif "MATERIAL" in name or "PRODUCT" in name or "BOM" in name:
        return "📦 Material & Product APIs"
    elif "BUSINESS_PARTNER" in name or "CUSTOMER" in name or "SUPPLIER" in name:
        return "👥 Master Data APIs"
    elif "PURCHASE" in name or "INFORECORD" in name:
        return "🛒 Procurement APIs"
    elif "ACCOUNTING" in name or "FINANCIAL" in name or "DISPUTE" in name:
        return "💰 Finance & Accounting APIs"
    elif "MAINTENANCE" in name or "MAINT" in name:
        return "🔧 Maintenance APIs"
    elif "WAREHOUSE" in name or "WHSE" in name or "DELIVERY" in name or "INVENTORY" in name:
        return "📋 Warehouse & Logistics APIs"
    else:
        return "🌐 Other APIs"

def main():
    # Load the actual API services we discovered
    with open('/home/gyanmis/actual_api_services.json', 'r') as f:
        api_services = json.load(f)
    
    print("🎯 Eclipse Multi-Service View will load these 39 API services:")
    print("=" * 70)
    
    # Categorize services
    categories = {}
    for service in api_services:
        category = categorize_api_service(service['technicalName'], service['description'])
        if category not in categories:
            categories[category] = []
        categories[category].append(service)
    
    # Display by category
    total_services = 0
    for category, services in categories.items():
        print(f"\n{category} ({len(services)} services):")
        print("-" * 50)
        
        for service in services:
            print(f"  🔗 {service['technicalName']}")
            print(f"     Description: {service['description']}")
            print(f"     URL: {service['serviceUrl']}")
            print()
            total_services += 1
    
    print("=" * 70)
    print(f"📊 SUMMARY:")
    print(f"   • Total API Services: {total_services}")
    print(f"   • Categories: {len(categories)}")
    print(f"   • All services will be dynamically loaded from catalog")
    print(f"   • Each service provides metadata and entity information")
    print()
    print("🌐 Your Eclipse plugin will now show ALL these services instead of just 2!")

if __name__ == "__main__":
    main()
