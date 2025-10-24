#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')

def test_saml_assertion():
    try:
        from saml_sales_order_lambda_final import create_saml_assertion, get_user_email
        import base64
        
        print("🔐 Testing SAML Assertion Generation")
        print("=" * 40)
        
        # Test user email lookup
        user_email = get_user_email("test-user-123")
        print(f"📧 User Email: {user_email}")
        
        # Generate SAML assertion
        assertion = create_saml_assertion(user_email)
        print(f"\n🎫 SAML Assertion (Base64): {assertion[:100]}...")
        
        # Decode and show XML
        decoded_xml = base64.b64decode(assertion).decode()
        print(f"\n📄 SAML Assertion XML:")
        print(decoded_xml)
        
        # Check for SAML bearer elements
        if "urn:oasis:names:tc:SAML:2.0:cm:bearer" in decoded_xml:
            print("\n✅ SAML Bearer confirmation method found")
        else:
            print("\n❌ SAML Bearer confirmation method missing")
            
        print("\n🔍 Key SAML Elements:")
        print(f"- Issuer: {'cognito-identity-provider' in decoded_xml}")
        print(f"- Subject: {'Subject>' in decoded_xml}")
        print(f"- Bearer Method: {'cm:bearer' in decoded_xml}")
        print(f"- Audience: {'AudienceRestriction' in decoded_xml}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_saml_assertion()
