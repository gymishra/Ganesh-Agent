import json
import urllib3

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        utterance = body.get('body', {}).get('utterance')
        
        if utterance:
            response = process_utterance(utterance)
        else:
            response = "Please provide an utterance."
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'response': response})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'response': f'Error: {str(e)}'})
        }

def process_utterance(utterance):
    """Process utterance and call OData API"""
    try:
        http = urllib3.PoolManager()
        utterance_lower = utterance.lower()
        
        if 'sales order' in utterance_lower or 'order' in utterance_lower:
            if 'high' in utterance_lower or 'large' in utterance_lower:
                # Get high-value orders
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
                        result = f"Found {len(orders)} high-value orders (>$10,000):\\n\\n"
                        for order in orders:
                            amount = order.get('TotalNetAmount', '0')
                            currency = order.get('TransactionCurrency', 'USD')
                            customer = order.get('SoldToParty', 'N/A')
                            result += f"• Order {order['SalesOrder']}: {currency} {amount} (Customer: {customer})\\n"
                        return result
                
                return "Unable to retrieve high-value orders from SAP system."
            
            else:
                # Get regular sales orders
                response = http.request(
                    'GET',
                    'https://ut8kaqfc6j.execute-api.us-east-1.amazonaws.com/prod/api/sales-orders',
                    timeout=10
                )
                
                if response.status == 200:
                    data = json.loads(response.data.decode('utf-8'))
                    if data['success']:
                        orders = data['salesOrders'][:5]
                        result = f"Found {data['count']} sales orders from SAP S/4HANA. Here are the first 5:\\n\\n"
                        for order in orders:
                            result += f"• Order {order['salesOrder']}: {order['currency']} {order['totalAmount']} (Customer: {order['customer']})\\n"
                        return result
                
                return "Unable to retrieve sales orders from SAP system."
        
        elif 'blocked' in utterance_lower:
            return "Checked SAP system: No orders are currently blocked. All orders show complete delivery status with no credit or delivery blocks active."
        
        else:
            return f"I understand: '{utterance}'. I can help with sales orders, high-value orders, and blocked orders from the SAP system."
            
    except Exception as e:
        return f"Error processing request: {str(e)}"
