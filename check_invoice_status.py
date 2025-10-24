#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin
from datetime import datetime

class InvoiceStatusChecker:
    """Check invoice status in SAP system"""
    
    def __init__(self):
        # SAP connection details
        self.sap_url = "https://vhcals4hci.awspoc.club/"
        self.sap_username = "bpinst"
        self.sap_password = "welcome1"
        
        # Setup SAP session
        self.setup_sap_session()
        
        # Invoice-related services
        self.invoice_services = [
            'API_BILLING_DOCUMENT_SRV',
            'API_SALES_DOCUMENT_SRV', 
            'API_SALES_ORDER_SRV',
            'BILLING_DOCUMENT_SRV',
            'INVOICE_SRV'
        ]
    
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
            'User-Agent': 'Invoice-Status-Checker/1.0'
        })
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()
    
    def check_invoice_status(self, invoice_number):
        """Check the status of a specific invoice"""
        
        print(f"🔍 Checking Invoice Status")
        print("=" * 50)
        print(f"📄 Invoice Number: {invoice_number}")
        print(f"🌐 SAP System: {self.sap_url}")
        print(f"👤 User: {self.sap_username}")
        print()
        
        results = []
        
        # Try different invoice services
        for service in self.invoice_services:
            print(f"🔍 Trying service: {service}")
            result = self.search_in_service(service, invoice_number)
            if result:
                results.append(result)
        
        # Also try sales order services (invoices might be linked to sales orders)
        print(f"🔍 Checking related sales documents...")
        sales_result = self.check_related_sales_documents(invoice_number)
        if sales_result:
            results.append(sales_result)
        
        return results
    
    def search_in_service(self, service_name, invoice_number):
        """Search for invoice in a specific service"""
        
        base_url = f"{self.sap_url}sap/opu/odata/sap/{service_name}"
        
        # Common entity names for invoices/billing documents
        entity_names = [
            'A_BillingDocument',
            'A_BillingDocumentItem', 
            'A_SalesDocument',
            'A_Invoice',
            'BillingDocument',
            'Invoice'
        ]
        
        for entity in entity_names:
            try:
                # Try direct access by invoice number
                search_url = f"{base_url}/{entity}"
                
                # Try different search approaches
                search_queries = [
                    f"('{invoice_number}')",  # Direct key access
                    f"?$filter=BillingDocument eq '{invoice_number}'",
                    f"?$filter=SalesDocument eq '{invoice_number}'",
                    f"?$filter=DocumentNumber eq '{invoice_number}'",
                    f"?$filter=InvoiceNumber eq '{invoice_number}'",
                    f"?$filter=contains(BillingDocument,'{invoice_number}')",
                    f"?$top=10&$filter=BillingDocument eq '{invoice_number}'"
                ]
                
                for query in search_queries:
                    try:
                        full_url = search_url + query
                        print(f"   🔗 Trying: {entity} with {query}")
                        
                        response = self.sap_session.get(
                            full_url,
                            verify=False,
                            timeout=30
                        )
                        
                        print(f"      Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                
                                # Check if we found data
                                if 'd' in data:
                                    if 'results' in data['d'] and data['d']['results']:
                                        print(f"      ✅ Found data in {service_name}/{entity}")
                                        return {
                                            'service': service_name,
                                            'entity': entity,
                                            'data': data['d']['results'],
                                            'url': full_url
                                        }
                                    elif isinstance(data['d'], dict) and len(data['d']) > 1:
                                        print(f"      ✅ Found single record in {service_name}/{entity}")
                                        return {
                                            'service': service_name,
                                            'entity': entity,
                                            'data': [data['d']],
                                            'url': full_url
                                        }
                                
                            except json.JSONDecodeError:
                                continue
                        
                        elif response.status_code == 404:
                            continue  # Try next query
                        elif response.status_code == 401:
                            print(f"      🔐 Authentication required")
                            break  # No point trying other queries for this entity
                        else:
                            print(f"      ⚠️ Status: {response.status_code}")
                    
                    except Exception as e:
                        continue  # Try next query
                        
            except Exception as e:
                continue  # Try next entity
        
        return None
    
    def check_related_sales_documents(self, invoice_number):
        """Check if the number might be a sales order or related document"""
        
        print(f"🔍 Checking related sales documents...")
        
        # Try sales order service
        service_name = 'API_SALES_ORDER_SRV'
        base_url = f"{self.sap_url}sap/opu/odata/sap/{service_name}"
        
        search_queries = [
            f"/A_SalesOrder('{invoice_number}')",
            f"/A_SalesOrder?$filter=SalesOrder eq '{invoice_number}'",
            f"/A_SalesOrder?$filter=contains(SalesOrder,'{invoice_number}')",
            f"/A_SalesOrder?$top=10&$filter=SalesOrder eq '{invoice_number}'"
        ]
        
        for query in search_queries:
            try:
                full_url = base_url + query
                print(f"   🔗 Trying: {query}")
                
                response = self.sap_session.get(
                    full_url,
                    verify=False,
                    timeout=30
                )
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'd' in data and data['d']:
                            print(f"      ✅ Found related sales document")
                            return {
                                'service': service_name,
                                'entity': 'A_SalesOrder',
                                'data': [data['d']] if isinstance(data['d'], dict) else data['d'].get('results', []),
                                'url': full_url,
                                'type': 'related_sales_document'
                            }
                    except:
                        continue
                        
            except Exception as e:
                continue
        
        return None
    
    def display_results(self, results, invoice_number):
        """Display the search results"""
        
        print(f"\n📊 INVOICE STATUS RESULTS")
        print("=" * 60)
        print(f"📄 Invoice Number: {invoice_number}")
        print(f"📅 Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not results:
            print("❌ No invoice found with that number")
            print()
            print("💡 Possible reasons:")
            print("   • Invoice number doesn't exist")
            print("   • Invoice is in a different system/client")
            print("   • User doesn't have access to invoice data")
            print("   • Invoice number format is different")
            print()
            print("🔍 Suggestions:")
            print("   • Check the invoice number format")
            print("   • Try searching without leading zeros")
            print("   • Contact your SAP administrator")
            return
        
        for i, result in enumerate(results, 1):
            print(f"🏆 RESULT {i}: Found in {result['service']}")
            print("-" * 40)
            print(f"📋 Entity: {result['entity']}")
            print(f"🔗 URL: {result['url']}")
            
            if result.get('type') == 'related_sales_document':
                print("📝 Type: Related Sales Document")
            
            # Display the data
            data_items = result['data']
            for j, item in enumerate(data_items[:3], 1):  # Show first 3 items
                print(f"\n📄 Record {j}:")
                
                # Show key fields
                key_fields = [
                    'BillingDocument', 'SalesDocument', 'SalesOrder', 'DocumentNumber',
                    'BillingDocumentDate', 'SalesOrderDate', 'CreationDate',
                    'BillingDocumentType', 'SalesOrderType', 'DocumentType',
                    'SoldToParty', 'CustomerName', 'Customer',
                    'TotalNetAmount', 'TransactionCurrency',
                    'BillingDocumentIsCancelled', 'OverallSDProcessStatus', 'Status'
                ]
                
                for field in key_fields:
                    if field in item and item[field]:
                        print(f"   {field}: {item[field]}")
                
                # Show any status-related fields
                status_fields = [k for k in item.keys() if 'status' in k.lower() or 'state' in k.lower()]
                if status_fields:
                    print("   📊 Status Information:")
                    for status_field in status_fields:
                        print(f"      {status_field}: {item[status_field]}")
            
            if len(data_items) > 3:
                print(f"   ... and {len(data_items) - 3} more records")
            
            print()

def main():
    """Main function"""
    
    invoice_number = "1023456"
    
    print("🔍 SAP Invoice Status Checker")
    print("=" * 60)
    
    checker = InvoiceStatusChecker()
    results = checker.check_invoice_status(invoice_number)
    checker.display_results(results, invoice_number)
    
    return results

if __name__ == "__main__":
    main()
