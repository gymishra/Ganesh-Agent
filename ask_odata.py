#!/usr/bin/env python3

import boto3
import json
import sys
import argparse

def query_sagemaker_endpoint(endpoint_name, question):
    """Query the SageMaker endpoint with a question"""
    
    try:
        # Initialize SageMaker runtime client
        runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')
        
        # Prepare the query
        payload = json.dumps([question])
        
        print(f"🤖 Asking the OData Model...")
        print(f"❓ Question: {question}")
        print("-" * 50)
        
        # Invoke the endpoint
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=payload
        )
        
        # Parse the response
        result = json.loads(response['Body'].read().decode())
        
        print(f"🎯 Model Response: {result}")
        
        # Interpret the result
        if isinstance(result, dict) and 'predictions' in result:
            predictions = result['predictions']
            if predictions:
                category = predictions[0]
                
                # Provide category-specific advice
                advice = {
                    'order': """
🎯 ORDER CATEGORY - Perfect for sales order creation!
💡 Recommended OData Services:
   • API_SALES_ORDER_SRV - Primary sales order creation
   • API_SALES_QUOTATION_SRV - Convert quotations to orders
   • API_SALES_CONTRACT_SRV - Contract-based orders
   
📋 Typical Operations:
   • POST /A_SalesOrder - Create new sales order
   • GET /A_SalesOrder - Read existing orders
   • PATCH /A_SalesOrder - Update order details
                    """,
                    
                    'customer': """
🎯 CUSTOMER CATEGORY - Essential for order headers!
💡 Recommended OData Services:
   • API_BUSINESS_PARTNER - Complete customer data
   • API_CUSTOMER_MASTER_SRV - Customer master records
   • API_CUSTOMER_MATERIAL_SRV - Customer-specific materials
   
📋 Typical Operations:
   • GET /A_Customer - Retrieve customer details
   • GET /A_BusinessPartner - Get business partner info
                    """,
                    
                    'product': """
🎯 PRODUCT CATEGORY - Needed for order line items!
💡 Recommended OData Services:
   • API_PRODUCT_SRV - Product master data
   • API_MATERIAL_DOCUMENT_SRV - Material information
   • API_PRODUCT_VALUATION_SRV - Product pricing
   
📋 Typical Operations:
   • GET /A_Product - Get product details
   • GET /A_ProductPlant - Plant-specific product data
                    """,
                    
                    'financial': """
🎯 FINANCIAL CATEGORY - Important for pricing and billing!
💡 Recommended OData Services:
   • API_PRICING_SRV - Pricing conditions
   • API_BILLING_DOCUMENT_SRV - Billing documents
   • API_PAYMENT_SRV - Payment processing
   
📋 Typical Operations:
   • GET /A_PricingCondition - Get pricing info
   • POST /A_BillingDocument - Create billing document
                    """,
                    
                    'general': """
🎯 GENERAL CATEGORY - May need more specific details
💡 For Sales Order Creation, you typically need:
   1. 🎯 Primary: API_SALES_ORDER_SRV
   2. 👤 Customer: API_BUSINESS_PARTNER
   3. 📦 Product: API_PRODUCT_SRV
   4. 💰 Pricing: API_PRICING_SRV
   
📋 Try asking more specific questions like:
   • "Sales order creation API"
   • "Customer data for orders"
   • "Product information service"
                    """
                }
                
                print(advice.get(category, f"Category: {category}"))
        
        return result
        
    except Exception as e:
        print(f"❌ Error querying model: {str(e)}")
        return None

def interactive_mode():
    """Interactive mode for asking questions"""
    
    endpoint_name = 'odata-classifier-fixed-2025-08-10-18-21-17'
    
    print("🤖 Interactive OData Assistant")
    print("=" * 50)
    print("Ask me questions about OData services!")
    print("Type 'quit' or 'exit' to stop.")
    print()
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print()
            query_sagemaker_endpoint(endpoint_name, question)
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description='Ask questions about OData services')
    parser.add_argument('question', nargs='*', help='Question to ask (if not provided, starts interactive mode)')
    parser.add_argument('--endpoint', default='odata-classifier-fixed-2025-08-10-18-21-17', 
                       help='SageMaker endpoint name')
    
    args = parser.parse_args()
    
    if args.question:
        # Single question mode
        question = ' '.join(args.question)
        print("🤖 OData Service Assistant")
        print("=" * 50)
        query_sagemaker_endpoint(args.endpoint, question)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
