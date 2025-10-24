#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')

def test_saml_functions():
    try:
        from saml_sales_order_lambda_final import create_saml_assertion, get_user_email_from_identity_center
        import base64
        
        print("🔐 Testing SAML Bearer Grant Type Implementation")
        print("=" * 50)
        
        # Test user email
        test_email = "test@amazon.com"
        print(f"📧 Test Email: {test_email}")
        
        # Generate SAML assertion
        assertion = create_saml_assertion(test_email)
        print(f"\n🎫 SAML Assertion Generated: ✅")
        print(f"   Length: {len(assertion)} characters")
        
        # Decode and analyze XML
        decoded_xml = base64.b64decode(assertion).decode()
        print(f"\n📄 SAML Assertion XML Structure:")
        print("-" * 30)
        print(decoded_xml)
        
        # Verify SAML Bearer elements
        print(f"\n🔍 SAML Bearer Grant Type Verification:")
        print(f"✅ Bearer Method: {'urn:oasis:names:tc:SAML:2.0:cm:bearer' in decoded_xml}")
        print(f"✅ Subject Confirmation: {'SubjectConfirmation' in decoded_xml}")
        print(f"✅ Audience Restriction: {'AudienceRestriction' in decoded_xml}")
        print(f"✅ Client ID in Audience: {'AW07241704C' in decoded_xml}")
        print(f"✅ Email NameID: {test_email in decoded_xml}")
        
        print(f"\n🎯 Grant Type: urn:ietf:params:oauth:grant-type:saml2-bearer")
        print(f"🎯 This assertion will be used for OAuth2 token exchange")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_saml_functions()
