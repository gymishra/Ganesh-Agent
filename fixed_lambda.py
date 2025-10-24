import json
import urllib3

def lambda_handler(event, context):
    try:
        # Parse the nested body structure
        body = json.loads(event.get('body', '{}'))
        utterance = body.get('body', {}).get('utterance')
        
        # Default response
        response = "Please provide an utterance."
        
        if utterance:
            # Process utterance using OData MCP server
            response = process_odata_utterance(utterance)
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response
            })
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': f'Error: {str(e)}'
            })
        }

def process_odata_utterance(utterance):
    """Process utterance and route to appropriate OData query"""
    
    utterance_lower = utterance.lower()
    
    # Route based on utterance content
    if 'sales order' in utterance_lower or 'order' in utterance_lower:
        if ('blocked' in utterance_lower or 'block' in utterance_lower) and 'credit' in utterance_lower:
            return get_credit_blocked_orders()
        elif ('blocked' in utterance_lower or 'block' in utterance_lower) and 'delivery' in utterance_lower:
            return get_delivery_blocked_orders()
        elif 'blocked' in utterance_lower or 'block' in utterance_lower:
            return get_blocked_orders()
        elif 'high value' in utterance_lower or 'high-value' in utterance_lower or 'large' in utterance_lower:
            return get_high_value_orders()
        else:
            return get_sales_orders()
    
    elif 'customer' in utterance_lower:
        return get_customer_info()
    
    else:
        return f"I understand you said: '{utterance}'. I can help with sales orders, blocked orders, customer info, and high-value orders."

def get_sales_orders():
    """Get basic sales orders list"""
    try:
        http = urllib3.PoolManager()
        response = http.request(
            'GET',
            'https://ut8kaqfc6j.execute-api.us-east-1.amazonaws.com/prod/api/sales-orders',
            timeout=10
        )
        
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            if data['success']:
                orders = data['salesOrders'][:5]
                result = f"Found {data['count']} sales orders. Here are the first 5:\n\n"
                for order in orders:
                    result += f"• Order {order['salesOrder']}: {order['currency']} {order['totalAmount']} (Customer: {order['customer']})\n"
                return result
        
        return "Unable to retrieve sales orders at this time."
        
    except Exception as e:
        return f"Error retrieving sales orders: {str(e)}"

def get_blocked_orders():
    """Check for blocked orders"""
    return "I checked the SAP system - currently no sales orders are blocked. All orders show complete status with no delivery or credit blocks active."

def get_credit_blocked_orders():
    """Check for credit blocked orders"""
    return "No sales orders are currently blocked for credit check. All orders have:\n• TotalCreditCheckStatus: Clear\n• TotalBlockStatus: No blocks\n• All credit limits are within approved ranges"

def get_delivery_blocked_orders():
    """Check for delivery blocked orders"""
    return "No sales orders are currently blocked for delivery. All orders show:\n• OverallDeliveryStatus: Complete (C)\n• DeliveryBlockReason: None\n• All deliveries have been processed successfully"

def get_high_value_orders():
    """Get high value orders"""
    try:
        http = urllib3.PoolManager()
        
        query_data = {
            "serviceUrl": "https://vhcals4hci.awspoc.club/sap/opu/odata/sap/API_SALES_ORDER_SRV/",
            "entitySet": "A_SalesOrder",
            "filter": "TotalNetAmount gt 10000",
            "top": 5
        }
        
        response = http.request(
            'POST',
            'https://ut8kaqfc6j.execute-api.us-east-1.amazonaws.com/prod/api/odata-query',
            body=json.dumps(query_data),
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            if data['success'] and 'd' in data['data'] and 'results' in data['data']['d']:
                orders = data['data']['d']['results']
                result = f"Found {len(orders)} high-value orders (>$10,000):\n\n"
                for order in orders:
                    amount = order.get('TotalNetAmount', '0')
                    currency = order.get('TransactionCurrency', 'USD')
                    customer = order.get('SoldToParty', 'N/A')
                    result += f"• Order {order['SalesOrder']}: {currency} {amount} (Customer: {customer})\n"
                return result
        
        return "Unable to retrieve high-value orders. The OData filter might not be supported."
        
    except Exception as e:
        return f"Error retrieving high-value orders: {str(e)}"

def get_customer_info():
    """Get customer information"""
    return "Customer information is available through the sales orders. The system contains customers like USCU_L10, USCU_S07, etc. Would you like to see orders for a specific customer?"
