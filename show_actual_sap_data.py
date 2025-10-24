#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urljoin

def show_actual_sap_data():
    """Show actual data from SAP system to help user find real document numbers"""
    
    # Working credentials
    sap_url = "https://vhcals4hci.awspoc.club/"
    username = "bpinst"
    password = "Welcome1"
    
    # Setup session
    session = requests.Session()
    auth_string = f"{username}:{password}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    
    session.headers.update({
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json'
    })
    
    requests.packages.urllib3.disable_warnings()
    
    print("📊 Actual Data in Your SAP System")
    print("=" * 60)
    
    # Show actual sales orders
    print("\n🎯 ACTUAL SALES ORDERS:")
    print("-" * 30)
    
    try:
        sales_url = f"{sap_url}sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder?$top=10"
        response = session.get(sales_url, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'd' in data and 'results' in data['d']:
                orders = data['d']['results']
                print(f"Found {len(orders)} sales orders:")
                
                for i, order in enumerate(orders, 1):
                    sales_order = order.get('SalesOrder', 'N/A')
                    order_type = order.get('SalesOrderType', 'N/A')
                    customer = order.get('SoldToParty', 'N/A')
                    date = order.get('SalesOrderDate', 'N/A')
                    amount = order.get('TotalNetAmount', 'N/A')
                    currency = order.get('TransactionCurrency', 'N/A')
                    
                    print(f"  {i:2d}. Sales Order: {sales_order}")
                    print(f"      Type: {order_type} | Customer: {customer}")
                    print(f"      Date: {date} | Amount: {amount} {currency}")
                    print()
        else:
            print(f"❌ Could not fetch sales orders: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error fetching sales orders: {str(e)}")
    
    # Show actual customers
    print("\n👤 ACTUAL CUSTOMERS:")
    print("-" * 30)
    
    try:
        customer_url = f"{sap_url}sap/opu/odata/sap/API_BUSINESS_PARTNER/A_Customer?$top=10"
        response = session.get(customer_url, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'd' in data and 'results' in data['d']:
                customers = data['d']['results']
                print(f"Found {len(customers)} customers:")
                
                for i, customer in enumerate(customers, 1):
                    customer_id = customer.get('Customer', 'N/A')
                    customer_name = customer.get('CustomerName', 'N/A')
                    country = customer.get('Country', 'N/A')
                    
                    print(f"  {i:2d}. Customer: {customer_id}")
                    print(f"      Name: {customer_name}")
                    print(f"      Country: {country}")
                    print()
        else:
            print(f"❌ Could not fetch customers: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error fetching customers: {str(e)}")
    
    print("\n💡 WHAT YOU CAN DO:")
    print("=" * 60)
    print("1. 🔍 Pick a real Sales Order number from above")
    print("2. 🎯 Ask me to check its status")
    print("3. 📝 Try creating a new sales order")
    print("4. 👤 Search for customer information")
    print()
    print("Example questions you can ask:")
    print('• "Check status of sales order 0000012345"')
    print('• "Create a sales order for customer 1000001"')
    print('• "Show me details of customer 1000001"')

if __name__ == "__main__":
    show_actual_sap_data()
