#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin
from datetime import datetime

class InvoiceStatusChecker:
    """Check invoice status in SAP system with corrected credentials"""
    
    def __init__(self):
        # SAP connection details - CORRECTED PASSWORD
        self.sap_url = "https://vhcals4hci.awspoc.club/"
        self.sap_username = "bpinst"
        self.sap_password = "Welcome1"  # Corrected: Capital W
        
        # Setup SAP session
        self.setup_sap_session()
        
        # Invoice-related services
        self.invoice_services = [
            'API_BILLING_DOCUMENT_SRV',
            'API_SALES_DOCUMENT_SRV', 
            'API_SALES_ORDER_SRV',
            'BILLING_DOCUMENT_SRV'
        ]
    
    def setup_sap_session(self):
        """Setup authenticated SAP session with corrected password"""
        
        self.sap_session = requests.Session()
        
        # Setup authentication with corrected password
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
        
        print(f"🔐 Using credentials: {self.sap_username} / {self.sap_password}")
    
    def test_authentication(self):
        """Test if the corrected credentials work"""
        
        print(f"🔐 Testing Authentication with Corrected Password")
        print("-" * 50)
        
        # Test basic connectivity first
        test_url = f"{self.sap_url}sap/opu/odata/"
        
        try:
            response = self.sap_session.get(
                test_url,
                verify=False,
                timeout=30
            )
            
            print(f"📊 Auth Test Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Authentication successful!")
                return True
            elif response.status_code == 401:
                print("❌ Authentication still failing")
                return False
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def check_invoice_status(self, invoice_number):
        """Check the status of a specific invoice with corrected auth"""
        
        print(f"\n🔍 Checking Invoice Status with Corrected Credentials")
        print("=" * 60)
        print(f"📄 Invoice Number: {invoice_number}")
        print(f"🌐 SAP System: {self.sap_url}")
        print(f"👤 User: {self.sap_username}")
        print(f"🔑 Password: {self.sap_password}")
        print()
        
        # First test authentication
        if not self.test_authentication():
            print("❌ Cannot proceed - authentication failed")
            return []
        
        results = []
        
        # Try different invoice services with corrected auth
        for service in self.invoice_services:
            print(f"\n🔍 Trying service: {service}")
            result = self.search_in_service(service, invoice_number)
            if result:
                results.append(result)
                print(f"✅ Found data in {service}")
            else:
                print(f"❌ No data found in {service}")
        
        return results
    
    def search_in_service(self, service_name, invoice_number):
        """Search for invoice in a specific service with better error handling"""
        
        base_url = f"{self.sap_url}sap/opu/odata/sap/{service_name}"
        
        # Try to access the service root first
        try:
            root_response = self.sap_session.get(
                base_url,
                verify=False,
                timeout=30
            )
            
            print(f"   Service root status: {root_response.status_code}")
            
            if root_response.status_code == 401:
                print(f"   🔐 Still getting auth errors for {service_name}")
                return None
            elif root_response.status_code != 200:
                print(f"   ⚠️ Service not accessible: {root_response.status_code}")
                return None
            
        except Exception as e:
            print(f"   ❌ Service connection error: {str(e)}")
            return None
        
        # If service is accessible, try to find the invoice
        entity_names = [
            'A_BillingDocument',
            'A_SalesOrder',
            'A_SalesDocument'
        ]
        
        for entity in entity_names:
            try:
                # Try simple entity access first
                entity_url = f"{base_url}/{entity}"
                
                # Try different search approaches
                search_queries = [
                    f"?$filter=BillingDocument eq '{invoice_number}'",
                    f"?$filter=SalesOrder eq '{invoice_number}'",
                    f"?$filter=SalesDocument eq '{invoice_number}'",
                    f"?$top=5"  # Just get some sample data
                ]
                
                for query in search_queries:
                    try:
                        full_url = entity_url + query
                        print(f"   🔗 Trying: {entity} {query}")
                        
                        response = self.sap_session.get(
                            full_url,
                            verify=False,
                            timeout=30
                        )
                        
                        print(f"      Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                
                                if 'd' in data and 'results' in data['d']:
                                    results = data['d']['results']
                                    print(f"      ✅ Got {len(results)} records")
                                    
                                    # Look for our specific invoice
                                    matching_records = []
                                    for record in results:
                                        # Check various fields that might contain our invoice number
                                        for field in ['BillingDocument', 'SalesOrder', 'SalesDocument', 'DocumentNumber']:
                                            if field in record and str(record[field]) == str(invoice_number):
                                                matching_records.append(record)
                                                break
                                    
                                    if matching_records:
                                        return {
                                            'service': service_name,
                                            'entity': entity,
                                            'data': matching_records,
                                            'url': full_url
                                        }
                                    elif query == "?$top=5":
                                        # Show sample data structure
                                        print(f"      📋 Sample data structure:")
                                        if results:
                                            sample_fields = list(results[0].keys())[:5]
                                            print(f"         Fields: {sample_fields}")
                                
                            except json.JSONDecodeError as e:
                                print(f"      ⚠️ JSON decode error: {str(e)}")
                                continue
                        
                        elif response.status_code == 401:
                            print(f"      🔐 Auth required")
                            break
                        
                    except Exception as e:
                        print(f"      ❌ Query error: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"   ❌ Entity error: {str(e)}")
                continue
        
        return None
    
    def display_results(self, results, invoice_number):
        """Display the search results"""
        
        print(f"\n📊 INVOICE STATUS RESULTS (Corrected Auth)")
        print("=" * 60)
        print(f"📄 Invoice Number: {invoice_number}")
        print(f"🔑 Using Password: {self.sap_password}")
        print(f"📅 Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not results:
            print("❌ No invoice found with that number")
            print()
            print("💡 This could mean:")
            print("   • Invoice number doesn't exist in the system")
            print("   • Invoice is in a different client/company code")
            print("   • User still doesn't have sufficient authorization")
            print("   • Invoice number format needs adjustment")
            return
        
        for i, result in enumerate(results, 1):
            print(f"🏆 RESULT {i}: Found in {result['service']}")
            print("-" * 40)
            print(f"📋 Entity: {result['entity']}")
            print(f"🔗 URL: {result['url']}")
            
            # Display the data
            data_items = result['data']
            for j, item in enumerate(data_items, 1):
                print(f"\n📄 Invoice Record {j}:")
                
                # Show key invoice fields
                key_fields = [
                    'BillingDocument', 'SalesOrder', 'SalesDocument',
                    'BillingDocumentDate', 'CreationDate',
                    'BillingDocumentType', 'DocumentType',
                    'SoldToParty', 'CustomerName',
                    'TotalNetAmount', 'TransactionCurrency',
                    'BillingDocumentIsCancelled', 'OverallSDProcessStatus'
                ]
                
                for field in key_fields:
                    if field in item and item[field] is not None:
                        print(f"   {field}: {item[field]}")
                
                # Show status fields
                status_fields = [k for k in item.keys() if 'status' in k.lower()]
                if status_fields:
                    print("   📊 Status Fields:")
                    for status_field in status_fields:
                        print(f"      {status_field}: {item[status_field]}")

def main():
    """Main function with corrected password"""
    
    invoice_number = "1023456"
    
    print("🔍 SAP Invoice Status Checker (Corrected Password)")
    print("=" * 70)
    
    checker = InvoiceStatusChecker()
    results = checker.check_invoice_status(invoice_number)
    checker.display_results(results, invoice_number)
    
    return results

if __name__ == "__main__":
    main()
