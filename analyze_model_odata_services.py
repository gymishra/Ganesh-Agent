#!/usr/bin/env python3

import json
from datetime import datetime

def analyze_model_odata_services():
    """Analyze the OData services in our deployed model"""
    
    print("📊 OData Services Analysis - Our Deployed Model")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Model Endpoint: odata-classifier-fixed-2025-08-10-18-21-17")
    print()
    
    # Load the metadata used to train our model
    try:
        with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
            metadata = json.load(f)
        
        print("✅ Successfully loaded model training data")
        print()
        
        # Remove metadata section for analysis
        if '_metadata' in metadata:
            model_metadata = metadata.pop('_metadata')
        else:
            model_metadata = None
        
        # Count services
        total_services = len(metadata)
        
        print(f"📋 TOTAL ODATA SERVICES IN OUR MODEL: {total_services}")
        print("=" * 70)
        
        # Analyze each service
        service_analysis = []
        
        for service_name, service_data in metadata.items():
            analysis = {
                'name': service_name,
                'purpose': service_data.get('purpose', 'No purpose defined'),
                'entities': list(service_data.get('entities', {}).keys()),
                'entity_count': len(service_data.get('entities', {})),
                'use_cases': service_data.get('use_cases', []),
                'use_case_count': len(service_data.get('use_cases', [])),
                'endpoint': service_data.get('endpoint', 'No endpoint defined'),
                'has_oauth': 'oauth2_config' in service_data
            }
            service_analysis.append(analysis)
        
        # Display detailed service information
        for i, service in enumerate(service_analysis, 1):
            print(f"\n🎯 SERVICE {i}: {service['name']}")
            print("-" * 50)
            print(f"📝 Purpose: {service['purpose'][:100]}...")
            print(f"🏗️ Entities: {service['entity_count']} entities")
            print(f"   • {', '.join(service['entities'])}")
            print(f"💡 Use Cases: {service['use_case_count']} defined")
            print(f"🔐 OAuth2 Config: {'✅ Yes' if service['has_oauth'] else '❌ No'}")
            print(f"🌐 Endpoint: {service['endpoint']}")
            
            # Show sample use cases
            if service['use_cases']:
                print(f"📋 Sample Use Cases:")
                for use_case in service['use_cases'][:3]:  # Show first 3
                    print(f"   • {use_case}")
                if len(service['use_cases']) > 3:
                    print(f"   ... and {len(service['use_cases']) - 3} more")
        
        # Summary statistics
        print(f"\n📊 DETAILED STATISTICS")
        print("=" * 70)
        
        total_entities = sum(s['entity_count'] for s in service_analysis)
        total_use_cases = sum(s['use_case_count'] for s in service_analysis)
        oauth_services = sum(1 for s in service_analysis if s['has_oauth'])
        
        print(f"🎯 Total Services: {total_services}")
        print(f"🏗️ Total Entities: {total_entities}")
        print(f"💡 Total Use Cases: {total_use_cases}")
        print(f"🔐 OAuth2 Enabled Services: {oauth_services}")
        print(f"📊 Average Entities per Service: {total_entities / total_services:.1f}")
        print(f"📊 Average Use Cases per Service: {total_use_cases / total_services:.1f}")
        
        # Service categories
        print(f"\n🏷️ SERVICE CATEGORIES")
        print("-" * 30)
        
        categories = {
            'Customer Management': ['Customer', 'customer', 'Client'],
            'Sales & Orders': ['Sales', 'Order', 'sales', 'order'],
            'Product & Inventory': ['Product', 'Inventory', 'product', 'inventory'],
            'Financial': ['Financial', 'Payment', 'Invoice', 'financial'],
            'Supplier & Procurement': ['Supplier', 'Vendor', 'Purchase', 'supplier']
        }
        
        for category, keywords in categories.items():
            matching_services = []
            for service in service_analysis:
                if any(keyword in service['name'] or keyword in service['purpose'] for keyword in keywords):
                    matching_services.append(service['name'])
            
            if matching_services:
                print(f"📂 {category}: {len(matching_services)} services")
                for service_name in matching_services:
                    print(f"   • {service_name}")
        
        # Model metadata information
        if model_metadata:
            print(f"\n🤖 MODEL METADATA")
            print("-" * 30)
            print(f"📅 Created: {model_metadata.get('created_date', 'Unknown')}")
            print(f"🔧 Generator: {model_metadata.get('generator', 'Unknown')}")
            print(f"📝 Version: {model_metadata.get('version', 'Unknown')}")
            print(f"📋 Description: {model_metadata.get('description', 'No description')}")
            
            if 'optimization_notes' in model_metadata:
                print(f"⚡ Optimization Notes:")
                for note in model_metadata['optimization_notes']:
                    print(f"   • {note}")
        
        # Business domain coverage
        print(f"\n🎯 BUSINESS DOMAIN COVERAGE")
        print("-" * 40)
        
        domains = {
            'Customer Relationship Management': any('customer' in s['name'].lower() or 'customer' in s['purpose'].lower() for s in service_analysis),
            'Sales Order Management': any('sales' in s['name'].lower() or 'order' in s['name'].lower() for s in service_analysis),
            'Product & Inventory Management': any('product' in s['name'].lower() or 'inventory' in s['name'].lower() for s in service_analysis),
            'Financial Management': any('financial' in s['purpose'].lower() or 'payment' in s['purpose'].lower() for s in service_analysis),
            'Supplier Management': any('supplier' in s['purpose'].lower() or 'vendor' in s['purpose'].lower() for s in service_analysis)
        }
        
        for domain, covered in domains.items():
            status = "✅ Covered" if covered else "❌ Not Covered"
            print(f"   {domain}: {status}")
        
        # Use case analysis
        print(f"\n💡 USE CASE ANALYSIS")
        print("-" * 30)
        
        all_use_cases = []
        for service in service_analysis:
            all_use_cases.extend(service['use_cases'])
        
        # Find common keywords in use cases
        common_keywords = {}
        for use_case in all_use_cases:
            words = use_case.lower().split()
            for word in words:
                if len(word) > 3:  # Only count words longer than 3 characters
                    common_keywords[word] = common_keywords.get(word, 0) + 1
        
        # Show top keywords
        top_keywords = sorted(common_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("🔤 Most Common Keywords in Use Cases:")
        for keyword, count in top_keywords:
            print(f"   • {keyword}: {count} occurrences")
        
        return {
            'total_services': total_services,
            'total_entities': total_entities,
            'total_use_cases': total_use_cases,
            'services': service_analysis,
            'metadata': model_metadata
        }
        
    except FileNotFoundError:
        print("❌ Could not find model training data file")
        return None
    except Exception as e:
        print(f"❌ Error analyzing model data: {str(e)}")
        return None

def main():
    """Main function"""
    
    result = analyze_model_odata_services()
    
    if result:
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📊 Our model contains {result['total_services']} OData services")
        print(f"🏗️ With {result['total_entities']} total entities")
        print(f"💡 Covering {result['total_use_cases']} use cases")
        print()
        print("🤖 This is the knowledge base our SageMaker model uses to")
        print("   classify and recommend OData services for your questions!")
    else:
        print(f"\n❌ Analysis failed - could not load model data")

if __name__ == "__main__":
    main()
