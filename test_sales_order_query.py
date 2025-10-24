#!/usr/bin/env python3

import boto3
import json
import sys

def query_odata_model(endpoint_name, query_text):
    """Query the deployed OData model"""
    
    print(f"🔍 Querying OData Model: {endpoint_name}")
    print(f"📝 Question: {query_text}")
    print("=" * 60)
    
    try:
        # Initialize SageMaker runtime client
        runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')
        
        # Prepare the query
        payload = json.dumps([query_text])
        
        print(f"📤 Sending query to endpoint...")
        
        # Invoke the endpoint
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=payload
        )
        
        # Parse the response
        result = json.loads(response['Body'].read().decode())
        
        print(f"✅ Response received!")
        print(f"📊 Classification Result: {result}")
        
        # Interpret the result
        if isinstance(result, dict) and 'predictions' in result:
            predictions = result['predictions']
            if predictions:
                category = predictions[0]
                print(f"\n🎯 Model Classification: '{category}'")
                
                # Provide interpretation based on category
                interpretations = {
                    'order': "✅ This query is related to ORDER management - perfect for sales order creation!",
                    'product': "📦 This query is related to PRODUCT management - useful for sales order line items.",
                    'customer': "👤 This query is related to CUSTOMER management - needed for sales order headers.",
                    'financial': "💰 This query is related to FINANCIAL processes - relevant for pricing and billing.",
                    'general': "ℹ️ This query is classified as GENERAL - may need more specific OData service details."
                }
                
                interpretation = interpretations.get(category, f"🤔 Category '{category}' - check specific OData services.")
                print(f"💡 Interpretation: {interpretation}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error querying model: {str(e)}")
        return None

def test_sales_order_queries():
    """Test various sales order related queries"""
    
    endpoint_name = 'odata-classifier-fixed-2025-08-10-18-21-17'
    
    # Test queries related to sales orders
    test_queries = [
        "Which OData service is useful to create sales order?",
        "Sales order creation API",
        "Order management service",
        "Create new sales document",
        "Sales order header data",
        "Order line items management",
        "Customer order processing",
        "Sales document workflow",
        "Order fulfillment service",
        "Sales transaction processing"
    ]
    
    print("🚀 Testing Sales Order Related Queries")
    print("=" * 60)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}/{len(test_queries)}")
        result = query_odata_model(endpoint_name, query)
        results.append({
            'query': query,
            'result': result
        })
        print("-" * 40)
    
    # Summary
    print(f"\n📊 SUMMARY OF RESULTS")
    print("=" * 60)
    
    for i, test in enumerate(results, 1):
        query = test['query']
        result = test['result']
        
        if result and isinstance(result, dict) and 'predictions' in result:
            category = result['predictions'][0] if result['predictions'] else 'unknown'
            print(f"{i:2d}. {query[:50]:<50} → {category}")
        else:
            print(f"{i:2d}. {query[:50]:<50} → error")
    
    return results

def query_specific_odata_services():
    """Query about specific OData services that might be useful for sales orders"""
    
    endpoint_name = 'odata-classifier-fixed-2025-08-10-18-21-17'
    
    # Common SAP OData services related to sales
    odata_services = [
        "API_SALES_ORDER_SRV - Sales Order API",
        "API_CUSTOMER_MASTER_SRV - Customer Master Data",
        "API_PRODUCT_SRV - Product Master Data", 
        "API_BUSINESS_PARTNER - Business Partner Service",
        "API_MATERIAL_DOCUMENT_SRV - Material Document",
        "API_SALES_QUOTATION_SRV - Sales Quotation",
        "API_SALES_CONTRACT_SRV - Sales Contract",
        "API_DELIVERY_DOCUMENT_SRV - Delivery Document",
        "API_BILLING_DOCUMENT_SRV - Billing Document",
        "API_PRICING_SRV - Pricing Service"
    ]
    
    print("\n🔍 Testing Specific OData Services for Sales Order Creation")
    print("=" * 70)
    
    for service in odata_services:
        print(f"\n📋 Testing: {service}")
        result = query_odata_model(endpoint_name, service)
        print("-" * 50)

if __name__ == "__main__":
    try:
        print("🎯 OData Model Query Tool for Sales Order Creation")
        print("=" * 70)
        
        # Test your specific question
        endpoint_name = 'odata-classifier-fixed-2025-08-10-18-21-17'
        your_question = "Which OData service is useful to create sales order?"
        
        print(f"\n🎯 YOUR SPECIFIC QUESTION:")
        result = query_odata_model(endpoint_name, your_question)
        
        print(f"\n" + "="*70)
        
        # Run comprehensive tests
        if len(sys.argv) > 1 and sys.argv[1] == '--comprehensive':
            test_sales_order_queries()
            query_specific_odata_services()
        else:
            print(f"\n💡 Tip: Run with '--comprehensive' for more detailed testing")
            print(f"   Example: python test_sales_order_query.py --comprehensive")
        
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1)
