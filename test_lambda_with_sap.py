#!/usr/bin/env python3
import json
import sys
sys.path.insert(0, '/home/gyanmis')

def test_lambda_with_sap_details():
    try:
        from saml_sales_order_lambda_final import lambda_handler
        
        # Lambda event with SAP details
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': 'test-user-123',
                        'email': 'test@amazon.com'
                    }
                }
            },
            'body': json.dumps({
                'customer': 'CUST001',
                'material': 'MAT001', 
                'quantity': '10'
            }),
            'queryStringParameters': {
                'sap_host': 'vhcals4hci.awspoc.club',
                'client': '100',
                'client_id': 'AW07241704C',
                'scope': 'ZORDER_SRV_0001'
            }
        }
        
        class Context:
            function_name = 'saml-lambda-test'
            aws_request_id = 'test-123'
        
        print("🧪 Testing Lambda with SAP Connection Details")
        print("=" * 50)
        print(f"SAP Host: {event['queryStringParameters']['sap_host']}")
        print(f"Client: {event['queryStringParameters']['client']}")
        print(f"Client ID: {event['queryStringParameters']['client_id']}")
        print(f"Scope: {event['queryStringParameters']['scope']}")
        
        print("\n🚀 Executing Lambda...")
        result = lambda_handler(event, Context())
        
        print("\n📋 Lambda Response:")
        print(json.dumps(result, indent=2))
        
        # Check response
        if result['statusCode'] == 200:
            print("\n✅ Lambda executed successfully")
        else:
            print(f"\n⚠️  Lambda returned status: {result['statusCode']}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_lambda_with_sap_details()
