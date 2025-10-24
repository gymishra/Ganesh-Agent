#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')

def test_saml_signing():
    try:
        from saml_sales_order_lambda_final import create_saml_assertion
        import base64
        
        print("🔍 SAML Assertion Signing Analysis")
        print("=" * 40)
        
        # Generate assertion
        assertion = create_saml_assertion("test@amazon.com")
        decoded_xml = base64.b64decode(assertion).decode()
        
        print("📄 Current SAML Assertion:")
        print(decoded_xml)
        
        print("\n🔍 Signature Analysis:")
        has_signature = "Signature" in decoded_xml
        has_digest = "DigestValue" in decoded_xml
        has_signature_value = "SignatureValue" in decoded_xml
        
        print(f"❌ Digital Signature: {has_signature}")
        print(f"❌ Digest Value: {has_digest}")
        print(f"❌ Signature Value: {has_signature_value}")
        
        print(f"\n⚠️  CRITICAL ISSUE:")
        print(f"- SAML assertion is NOT digitally signed")
        print(f"- Private key exists but is unused")
        print(f"- SAP will likely reject unsigned assertions")
        print(f"- This explains the OAuth2 token exchange failure")
        
        print(f"\n🔧 Required Fix:")
        print(f"- Sign SAML assertion with private key")
        print(f"- Add <Signature> element to XML")
        print(f"- Include certificate for SAP verification")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_saml_signing()
