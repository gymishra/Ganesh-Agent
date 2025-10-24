#!/usr/bin/env python3

import requests
import json
import base64
from datetime import datetime

class InvoiceODataGuide:
    """Comprehensive guide for invoice-related OData services"""
    
    def __init__(self):
        # Working SAP credentials
        self.sap_url = "https://vhcals4hci.awspoc.club/"
        self.username = "bpinst"
        self.password = "Welcome1"
        
        # Setup session
        self.setup_session()
        
        # Invoice-related OData services mapping
        self.invoice_services = {
            'primary_billing': {
                'service': 'API_BILLING_DOCUMENT_SRV',
                'description': 'Primary service for billing documents and invoices',
                'entities': ['A_BillingDocument', 'A_BillingDocumentItem', 'A_BillingDocumentPartner'],
                'key_fields': ['BillingDocument', 'BillingDocumentDate', 'BillingDocumentType'],
                'status': 'access_forbidden',  # Based on our testing
                'use_case': 'Direct invoice access and management'
            },
            'sales_documents': {
                'service': 'API_SALES_ORDER_SRV',
                'description': 'Sales orders that can be linked to invoices',
                'entities': ['A_SalesOrder', 'A_SalesOrderItem', 'A_SalesOrderBillingPlan'],
                'key_fields': ['SalesOrder', 'SalesOrderDate', 'TotalNetAmount'],
                'status': 'accessible',  # Based on our testing
                'use_case': 'Find sales orders that generated invoices'
            },
            'customer_data': {
                'service': 'API_BUSINESS_PARTNER',
                'description': 'Customer information related to invoices',
                'entities': ['A_Customer', 'A_BusinessPartner', 'A_CustomerCompany'],
                'key_fields': ['Customer', 'CustomerName', 'BusinessPartner'],
                'status': 'accessible',
                'use_case': 'Get customer details for invoice recipients'
            },
            'financial_documents': {
                'service': 'API_FINANCIALACCOUNTINGDOCUMENT_SRV',
                'description': 'Financial accounting documents including invoice postings',
                'entities': ['A_FinancialAccountingDocument', 'A_FinancialAccountingDocumentItem'],
                'key_fields': ['AccountingDocument', 'CompanyCode', 'FiscalYear'],
                'status': 'unknown',
                'use_case': 'Financial impact of invoices'
            }
        }
    
    def setup_session(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        auth_b64 = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json'
        })
        
        requests.packages.urllib3.disable_warnings()
    
    def display_model_response(self):
        """Display what our model said about invoice OData services"""
        
        print("🤖 OUR SAGEMAKER MODEL RESPONSE")
        print("=" * 60)
        print("❓ Question: 'Show me the OData relevant for getting details of an invoice number'")
        print("🎯 Model Classification: GENERAL")
        print("📊 Model Confidence: Standard fallback response")
        print()
        print("💡 Model Interpretation:")
        print("   The model classified this as 'general' because it's using our")
        print("   fallback classifier due to sklearn compatibility issues.")
        print("   However, based on SAP expertise, here are the ACTUAL services:")
        print()
    
    def display_invoice_odata_services(self):
        """Display comprehensive invoice OData services"""
        
        print("🎯 ACTUAL INVOICE-RELATED ODATA SERVICES")
        print("=" * 60)
        
        for category, info in self.invoice_services.items():
            status_icon = "✅" if info['status'] == 'accessible' else "❌" if info['status'] == 'access_forbidden' else "❓"
            
            print(f"\n{status_icon} {category.upper().replace('_', ' ')}")
            print("-" * 40)
            print(f"📋 Service: {info['service']}")
            print(f"📝 Description: {info['description']}")
            print(f"🎯 Use Case: {info['use_case']}")
            print(f"📊 Status: {info['status']}")
            print(f"🏗️ Key Entities: {', '.join(info['entities'])}")
            print(f"🔑 Key Fields: {', '.join(info['key_fields'])}")
    
    def test_accessible_services(self):
        """Test which services are actually accessible"""
        
        print(f"\n🔍 TESTING SERVICE ACCESSIBILITY")
        print("=" * 60)
        
        accessible_services = []
        
        for category, info in self.invoice_services.items():
            service_name = info['service']
            print(f"\n🔍 Testing: {service_name}")
            
            try:
                service_url = f"{self.sap_url}sap/opu/odata/sap/{service_name}/"
                response = self.session.get(service_url, verify=False, timeout=30)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ ACCESSIBLE - Can retrieve invoice data")
                    info['status'] = 'accessible'
                    accessible_services.append(info)
                    
                    # Test metadata
                    metadata_url = f"{service_url}$metadata"
                    metadata_response = self.session.get(metadata_url, verify=False, timeout=30)
                    if metadata_response.status_code == 200:
                        print(f"   ✅ Metadata available")
                
                elif response.status_code == 403:
                    print(f"   🚫 ACCESS FORBIDDEN - User lacks authorization")
                    info['status'] = 'access_forbidden'
                
                elif response.status_code == 404:
                    print(f"   ❌ NOT FOUND - Service not available")
                    info['status'] = 'not_found'
                
                elif response.status_code == 401:
                    print(f"   🔐 AUTH REQUIRED - Credentials issue")
                    info['status'] = 'auth_required'
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                info['status'] = 'error'
        
        return accessible_services
    
    def provide_implementation_examples(self, accessible_services):
        """Provide practical implementation examples"""
        
        print(f"\n💻 IMPLEMENTATION EXAMPLES")
        print("=" * 60)
        
        if not accessible_services:
            print("❌ No accessible invoice services found with current user permissions")
            print()
            print("💡 Alternative approaches:")
            print("1. Use sales order data to find related billing information")
            print("2. Request additional user authorizations for billing services")
            print("3. Use financial document services if available")
            return
        
        for service_info in accessible_services:
            service_name = service_info['service']
            entities = service_info['entities']
            
            print(f"\n🎯 {service_name}")
            print("-" * 30)
            
            if service_name == 'API_SALES_ORDER_SRV':
                print("📝 Use Case: Find sales orders that generated invoices")
                print("💻 Example Queries:")
                print(f"   • Get sales order: GET /sap/opu/odata/sap/{service_name}/A_SalesOrder('12345')")
                print(f"   • Search by customer: GET /sap/opu/odata/sap/{service_name}/A_SalesOrder?$filter=SoldToParty eq '1000001'")
                print(f"   • Get billing plan: GET /sap/opu/odata/sap/{service_name}/A_SalesOrderBillingPlan")
                
            elif service_name == 'API_BUSINESS_PARTNER':
                print("📝 Use Case: Get customer details for invoice recipients")
                print("💻 Example Queries:")
                print(f"   • Get customer: GET /sap/opu/odata/sap/{service_name}/A_Customer('1000001')")
                print(f"   • Search customers: GET /sap/opu/odata/sap/{service_name}/A_Customer?$filter=contains(CustomerName,'SAP')")
                
            elif service_name == 'API_BILLING_DOCUMENT_SRV':
                print("📝 Use Case: Direct invoice access (if authorized)")
                print("💻 Example Queries:")
                print(f"   • Get invoice: GET /sap/opu/odata/sap/{service_name}/A_BillingDocument('90000001')")
                print(f"   • Get invoice items: GET /sap/opu/odata/sap/{service_name}/A_BillingDocumentItem")
                print(f"   • Search by date: GET /sap/opu/odata/sap/{service_name}/A_BillingDocument?$filter=BillingDocumentDate ge datetime'2023-01-01T00:00:00'")
    
    def demonstrate_invoice_lookup(self):
        """Demonstrate actual invoice lookup with available services"""
        
        print(f"\n🎯 PRACTICAL INVOICE LOOKUP DEMONSTRATION")
        print("=" * 60)
        
        # Since we can't access billing documents directly, show alternative approach
        print("📋 Scenario: Looking up invoice details for a sales transaction")
        print()
        
        # Step 1: Find sales orders (which we can access)
        print("1️⃣ STEP 1: Find Related Sales Orders")
        print("-" * 30)
        
        try:
            sales_url = f"{self.sap_url}sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder?$top=3"
            response = self.session.get(sales_url, verify=False, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'd' in data and 'results' in data['d']:
                    orders = data['d']['results']
                    
                    print("✅ Found sales orders that may have generated invoices:")
                    for order in orders:
                        sales_order = order.get('SalesOrder', 'N/A')
                        customer = order.get('SoldToParty', 'N/A')
                        amount = order.get('TotalNetAmount', 'N/A')
                        currency = order.get('TransactionCurrency', 'N/A')
                        
                        print(f"   📄 Sales Order: {sales_order}")
                        print(f"      Customer: {customer} | Amount: {amount} {currency}")
                        
                        # Show how to get more details
                        print(f"      🔗 Details URL: /sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder('{sales_order}')")
                        print()
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Step 2: Show customer lookup
        print("2️⃣ STEP 2: Get Customer Details")
        print("-" * 30)
        print("💻 Example: GET /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_Customer('1000119')")
        print("📊 Returns: Customer name, address, contact details")
        print()
        
        # Step 3: Explain billing document approach
        print("3️⃣ STEP 3: Access Billing Documents (When Authorized)")
        print("-" * 30)
        print("🔐 Requires: Additional user authorizations")
        print("💻 Service: API_BILLING_DOCUMENT_SRV")
        print("📊 Provides: Direct invoice access, amounts, status, line items")

def main():
    """Main function"""
    
    print("🎯 INVOICE ODATA SERVICES GUIDE")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Based on SageMaker Model Query + SAP System Analysis")
    print()
    
    guide = InvoiceODataGuide()
    
    # Show model response
    guide.display_model_response()
    
    # Show comprehensive service list
    guide.display_invoice_odata_services()
    
    # Test accessibility
    accessible_services = guide.test_accessible_services()
    
    # Provide implementation examples
    guide.provide_implementation_examples(accessible_services)
    
    # Demonstrate practical lookup
    guide.demonstrate_invoice_lookup()
    
    print(f"\n📋 SUMMARY")
    print("=" * 70)
    print("🤖 Model Response: General (fallback classifier)")
    print("🎯 Actual Invoice Services: 4 identified")
    print(f"✅ Accessible Services: {len(accessible_services)}")
    print("💡 Recommendation: Use sales order data as proxy for invoice information")
    print("🔐 Note: Direct billing access requires additional user permissions")

if __name__ == "__main__":
    main()
