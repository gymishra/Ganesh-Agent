#!/usr/bin/env python3

import boto3
import json
import requests
import base64
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

class InteractiveSAPODataAssistant:
    """Complete interactive assistant for SAP OData operations"""
    
    def __init__(self):
        # SageMaker endpoint
        self.endpoint_name = 'odata-classifier-fixed-2025-08-10-18-21-17'
        self.sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')
        
        # SAP connection details
        self.sap_url = "https://vhcals4hci.awspoc.club/"
        self.sap_username = "bpinst"
        self.sap_password = "welcome1"
        
        # Setup SAP session
        self.setup_sap_session()
        
        # OData service mappings
        self.service_mappings = {
            'sales_order': {
                'primary_service': 'API_SALES_ORDER_SRV',
                'entities': ['A_SalesOrder', 'A_SalesOrderItem'],
                'required_fields': {
                    'header': ['SalesOrderType', 'SoldToParty', 'SalesOrganization', 'DistributionChannel', 'Division'],
                    'item': ['Material', 'RequestedQuantity', 'RequestedQuantityUnit']
                }
            },
            'customer': {
                'primary_service': 'API_BUSINESS_PARTNER',
                'entities': ['A_Customer', 'A_BusinessPartner'],
                'required_fields': {
                    'search': ['BusinessPartner', 'CustomerName']
                }
            },
            'product': {
                'primary_service': 'API_PRODUCT_SRV',
                'entities': ['A_Product', 'A_ProductPlant'],
                'required_fields': {
                    'search': ['Product', 'ProductDescription']
                }
            }
        }
    
    def setup_sap_session(self):
        """Setup authenticated SAP session"""
        
        self.sap_session = requests.Session()
        
        # Setup authentication
        auth_string = f"{self.sap_username}:{self.sap_password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.sap_session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': 'Fetch'
        })
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()
    
    def query_sagemaker_model(self, question):
        """Query our deployed SageMaker model"""
        
        print(f"🤖 Asking our deployed model...")
        print(f"❓ Question: {question}")
        print("-" * 50)
        
        try:
            # Prepare the query
            payload = json.dumps([question])
            
            # Invoke the endpoint
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=payload
            )
            
            # Parse the response
            result = json.loads(response['Body'].read().decode())
            
            print(f"🎯 Model Response: {result}")
            
            if isinstance(result, dict) and 'predictions' in result:
                category = result['predictions'][0] if result['predictions'] else 'general'
                print(f"📊 Classification: {category}")
                return category
            
            return 'general'
            
        except Exception as e:
            print(f"❌ Error querying model: {str(e)}")
            return 'general'
    
    def determine_odata_service(self, category, question):
        """Determine the appropriate OData service based on model response"""
        
        print(f"\n🔍 Determining OData Service...")
        print("-" * 50)
        
        # Map model categories to our services
        category_mapping = {
            'order': 'sales_order',
            'customer': 'customer', 
            'product': 'product',
            'general': 'sales_order'  # Default to sales order for general queries
        }
        
        service_type = category_mapping.get(category, 'sales_order')
        service_info = self.service_mappings[service_type]
        
        print(f"✅ Recommended Service: {service_info['primary_service']}")
        print(f"📋 Main Entities: {', '.join(service_info['entities'])}")
        
        return service_type, service_info
    
    def collect_required_information(self, service_type, service_info):
        """Collect required information from user"""
        
        print(f"\n📝 Information Collection")
        print("=" * 50)
        
        collected_data = {}
        
        if service_type == 'sales_order':
            print("🎯 To create a sales order, I need the following information:")
            print()
            
            # Sales Order Header Information
            print("📋 SALES ORDER HEADER:")
            collected_data['header'] = {}
            
            # Sales Order Type
            order_type = input("1. Sales Order Type (e.g., 'OR' for standard order): ").strip()
            collected_data['header']['SalesOrderType'] = order_type or 'OR'
            
            # Customer
            customer = input("2. Customer Number (Sold-to Party): ").strip()
            if not customer:
                print("   ⚠️ Customer number is required. Using default: 1000001")
                customer = "1000001"
            collected_data['header']['SoldToParty'] = customer
            
            # Sales Organization
            sales_org = input("3. Sales Organization (e.g., '1000'): ").strip()
            collected_data['header']['SalesOrganization'] = sales_org or '1000'
            
            # Distribution Channel
            dist_channel = input("4. Distribution Channel (e.g., '10'): ").strip()
            collected_data['header']['DistributionChannel'] = dist_channel or '10'
            
            # Division
            division = input("5. Division (e.g., '00'): ").strip()
            collected_data['header']['Division'] = division or '00'
            
            print("\n📦 SALES ORDER ITEMS:")
            collected_data['items'] = []
            
            # Collect items
            item_count = 1
            while True:
                print(f"\n--- Item {item_count} ---")
                
                material = input(f"Material/Product ID (or 'done' to finish): ").strip()
                if material.lower() == 'done':
                    break
                
                if not material:
                    print("   ⚠️ Material ID is required for items")
                    continue
                
                quantity = input(f"Quantity: ").strip()
                if not quantity:
                    quantity = "1"
                
                unit = input(f"Unit (e.g., 'EA', 'PC'): ").strip()
                if not unit:
                    unit = "EA"
                
                item_data = {
                    'SalesOrderItem': str(item_count * 10),  # SAP typically uses 10, 20, 30...
                    'Material': material,
                    'RequestedQuantity': quantity,
                    'RequestedQuantityUnit': unit
                }
                
                collected_data['items'].append(item_data)
                item_count += 1
                
                if len(collected_data['items']) >= 5:  # Limit to 5 items for demo
                    print("   📝 Maximum 5 items for this demo")
                    break
            
            if not collected_data['items']:
                print("   ⚠️ Adding default item")
                collected_data['items'].append({
                    'SalesOrderItem': '10',
                    'Material': 'MAT001',
                    'RequestedQuantity': '1',
                    'RequestedQuantityUnit': 'EA'
                })
        
        elif service_type == 'customer':
            print("👤 Customer Information Search:")
            search_term = input("Enter customer name or number to search: ").strip()
            collected_data['search_term'] = search_term
        
        elif service_type == 'product':
            print("📦 Product Information Search:")
            search_term = input("Enter product name or ID to search: ").strip()
            collected_data['search_term'] = search_term
        
        return collected_data
    
    def execute_odata_operation(self, service_info, collected_data, service_type):
        """Execute the actual OData operation"""
        
        print(f"\n🚀 Executing OData Operation")
        print("=" * 50)
        
        service_name = service_info['primary_service']
        base_url = f"{self.sap_url}sap/opu/odata/sap/{service_name}"
        
        print(f"🌐 Service: {service_name}")
        print(f"🔗 Base URL: {base_url}")
        
        try:
            if service_type == 'sales_order':
                return self.create_sales_order(base_url, collected_data)
            elif service_type == 'customer':
                return self.search_customers(base_url, collected_data)
            elif service_type == 'product':
                return self.search_products(base_url, collected_data)
        
        except Exception as e:
            print(f"❌ OData operation failed: {str(e)}")
            return None
    
    def create_sales_order(self, base_url, data):
        """Create a sales order via OData"""
        
        print("📝 Creating Sales Order...")
        
        # First, get CSRF token
        csrf_response = self.sap_session.get(
            base_url,
            verify=False,
            timeout=30
        )
        
        csrf_token = csrf_response.headers.get('x-csrf-token')
        if csrf_token:
            self.sap_session.headers['X-CSRF-Token'] = csrf_token
            print(f"✅ CSRF token obtained")
        
        # Prepare sales order payload
        order_payload = {
            "SalesOrderType": data['header']['SalesOrderType'],
            "SoldToParty": data['header']['SoldToParty'],
            "SalesOrganization": data['header']['SalesOrganization'],
            "DistributionChannel": data['header']['DistributionChannel'],
            "Division": data['header']['Division'],
            "to_Item": []
        }
        
        # Add items
        for item in data['items']:
            order_payload["to_Item"].append({
                "SalesOrderItem": item['SalesOrderItem'],
                "Material": item['Material'],
                "RequestedQuantity": item['RequestedQuantity'],
                "RequestedQuantityUnit": item['RequestedQuantityUnit']
            })
        
        print(f"📤 Payload: {json.dumps(order_payload, indent=2)}")
        
        # Execute POST request
        create_url = f"{base_url}/A_SalesOrder"
        
        response = self.sap_session.post(
            create_url,
            json=order_payload,
            verify=False,
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Sales Order Created Successfully!")
            try:
                result = response.json()
                if 'd' in result:
                    order_data = result['d']
                    print(f"🎯 Sales Order Number: {order_data.get('SalesOrder', 'N/A')}")
                    return order_data
            except:
                pass
            return {"status": "success", "response": response.text[:500]}
        else:
            print(f"❌ Failed to create sales order")
            print(f"📝 Response: {response.text[:500]}")
            return {"status": "error", "message": response.text[:500]}
    
    def search_customers(self, base_url, data):
        """Search for customers"""
        
        print(f"🔍 Searching customers for: {data['search_term']}")
        
        search_url = f"{base_url}/A_Customer"
        if data['search_term']:
            search_url += f"?$filter=contains(CustomerName,'{data['search_term']}')"
        
        response = self.sap_session.get(
            search_url,
            verify=False,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                customers = result.get('d', {}).get('results', [])
                print(f"✅ Found {len(customers)} customers")
                return customers[:5]  # Return first 5
            except:
                pass
        
        return {"status": "error", "message": response.text[:500]}
    
    def search_products(self, base_url, data):
        """Search for products"""
        
        print(f"🔍 Searching products for: {data['search_term']}")
        
        search_url = f"{base_url}/A_Product"
        if data['search_term']:
            search_url += f"?$filter=contains(Product,'{data['search_term']}')"
        
        response = self.sap_session.get(
            search_url,
            verify=False,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                products = result.get('d', {}).get('results', [])
                print(f"✅ Found {len(products)} products")
                return products[:5]  # Return first 5
            except:
                pass
        
        return {"status": "error", "message": response.text[:500]}
    
    def run_interactive_session(self):
        """Run the complete interactive session"""
        
        print("🤖 Interactive SAP OData Assistant")
        print("=" * 60)
        print("I will help you execute OData operations on your SAP system!")
        print("Process: Question → Model → OData Service → Data Collection → Execution")
        print()
        
        while True:
            try:
                # Step 1: Get user question
                print("🎯 STEP 1: Your Question")
                print("-" * 30)
                question = input("❓ What would you like to do? (or 'quit' to exit): ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                print()
                
                # Step 2: Query SageMaker model
                print("🎯 STEP 2: Consulting Our Model")
                print("-" * 30)
                category = self.query_sagemaker_model(question)
                
                # Step 3: Determine OData service
                print("🎯 STEP 3: OData Service Selection")
                print("-" * 30)
                service_type, service_info = self.determine_odata_service(category, question)
                
                # Step 4: Collect required information
                print("🎯 STEP 4: Information Collection")
                print("-" * 30)
                collected_data = self.collect_required_information(service_type, service_info)
                
                # Step 5: Execute OData operation
                print("🎯 STEP 5: OData Execution")
                print("-" * 30)
                result = self.execute_odata_operation(service_info, collected_data, service_type)
                
                # Show results
                print(f"\n🎉 OPERATION COMPLETE!")
                print("=" * 60)
                
                if result:
                    if isinstance(result, dict) and result.get('status') == 'success':
                        print("✅ Operation successful!")
                    elif isinstance(result, list):
                        print(f"✅ Found {len(result)} results")
                        for i, item in enumerate(result[:3], 1):
                            print(f"   {i}. {item}")
                    else:
                        print(f"📊 Result: {result}")
                else:
                    print("❌ Operation failed")
                
                print("\n" + "="*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("Let's try again...\n")

def main():
    """Main function"""
    
    assistant = InteractiveSAPODataAssistant()
    assistant.run_interactive_session()

if __name__ == "__main__":
    main()
