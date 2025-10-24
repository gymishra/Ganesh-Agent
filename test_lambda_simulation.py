#!/usr/bin/env python3
import json
import sys
import os

# Add current directory to path to import the lambda function
sys.path.insert(0, '/home/gyanmis')

def simulate_lambda_event():
    """Simulate AWS Lambda event"""
    return {
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
        })
    }

def simulate_lambda_context():
    """Simulate AWS Lambda context"""
    class Context:
        def __init__(self):
            self.function_name = 'test-saml-lambda'
            self.aws_request_id = 'test-request-123'
    return Context()

def test_lambda():
    try:
        # Import your lambda function
        from saml_sales_order_lambda_final import lambda_handler
        
        # Create test event and context
        event = simulate_lambda_event()
        context = simulate_lambda_context()
        
        print("🧪 Testing SAML Lambda Function")
        print("=" * 40)
        print(f"Event: {json.dumps(event, indent=2)}")
        print("\n🚀 Executing lambda_handler...")
        
        # Execute the lambda
        result = lambda_handler(event, context)
        
        print("\n✅ Lambda Response:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lambda()
