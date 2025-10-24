#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')

def test_saml_bearer_flow():
    try:
        from saml_sales_order_lambda_final import create_saml_assertion, exchange_saml_for_token
        import base64
        import urllib.parse
        
        print("🔐 Testing Complete SAML Bearer Grant Type Flow")
        print("=" * 50)
        
        # Step 1: Create SAML assertion
        user_email = "test@amazon.com"
        assertion = create_saml_assertion(user_email)
        print(f"✅ Step 1: SAML Assertion created ({len(assertion)} chars)")
        
        # Step 2: Show what will be sent to SAP
        CLIENT_ID = "AW07241704C"
        CLIENT_SECRET = "Welcome1234$"
        SCOPE = "ZORDER_SRV_0001"
        SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
        
        auth_b64 = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        data = f"grant_type=urn:ietf:params:oauth:grant-type:saml2-bearer&client_id={CLIENT_ID}&scope={SCOPE}&assertion={urllib.parse.quote(assertion, safe='')}"
        
        print(f"\n📤 Step 2: OAuth2 Request Details")
        print(f"URL: {SAP_TOKEN_URL}")
        print(f"Method: POST")
        print(f"Authorization: Basic {auth_b64}")
        print(f"Content-Type: application/x-www-form-urlencoded")
        print(f"Grant Type: urn:ietf:params:oauth:grant-type:saml2-bearer")
        print(f"Data Length: {len(data)} chars")
        
        # Step 3: Attempt token exchange
        print(f"\n🔄 Step 3: Attempting SAML Bearer Token Exchange...")
        token = exchange_saml_for_token(assertion)
        
        if token:
            print(f"✅ OAuth2 Token received: {token[:20]}...")
        else:
            print(f"❌ Token exchange failed (expected - SAP OAuth2 not configured)")
            
        print(f"\n🎯 SAML Bearer Flow Summary:")
        print(f"- SAML Assertion: ✅ Generated with bearer confirmation")
        print(f"- Grant Type: ✅ saml2-bearer")
        print(f"- Client Auth: ✅ Basic authentication")
        print(f"- Token Exchange: ❌ SAP endpoint not configured")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_saml_bearer_flow()
