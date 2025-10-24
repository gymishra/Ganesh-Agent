#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')
from datetime import datetime

def trace_lambda_flow():
    print("🔍 Lambda Token URL Call Flow Trace")
    print("=" * 50)
    
    # Simulate Lambda event
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'test-user-123',
                    'email': 'test@amazon.com'
                }
            }
        },
        'queryStringParameters': {
            'user_id': 'gyanmis',
            'Customer': '1000',
            'Material': 'M001',
            'Quantity': '10'
        }
    }
    
    print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Lambda handler starts")
    
    try:
        from saml_sales_order_lambda_final import get_user_email_from_identity_center, create_saml_assertion, exchange_saml_for_token
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Step 1: Extract parameters from event")
        user_id = event['queryStringParameters']['user_id']
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Step 2: Get user email from Identity Center")
        user_email = get_user_email_from_identity_center(user_id)
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Step 3: Create SAML assertion")
        signed_assertion = create_saml_assertion(user_email)
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Step 4: 🎯 TOKEN URL CALLED HERE!")
        print(f"                                    URL: https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token")
        print(f"                                    Grant Type: urn:ietf:params:oauth:grant-type:saml2-bearer")
        
        access_token = exchange_saml_for_token(signed_assertion)
        
        if access_token:
            print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Step 5: Token received, proceed to OData call")
        else:
            print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Step 5: ❌ Token exchange failed")
            print(f"                                    Lambda returns error response")
            
    except Exception as e:
        print(f"⏰ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} - Exception: {str(e)}")

if __name__ == "__main__":
    trace_lambda_flow()
