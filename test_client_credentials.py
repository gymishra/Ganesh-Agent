#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')

def test_client_credentials():
    try:
        from token_handler import TokenHandler
        
        print("🔑 Testing OAuth2 Client Credentials Grant Type")
        print("=" * 50)
        
        # Initialize handler without OAuth2 endpoint (will use basic auth)
        handler = TokenHandler("AW07241704C", "Welcome1234$")
        
        print("📤 Testing with Basic Auth fallback...")
        headers = handler.get_auth_header("ZORDER_SRV_0001")
        
        print(f"✅ Auth Headers: {headers}")
        print(f"🎯 Grant Type: client_credentials (fallback to basic auth)")
        
        # Test OData service call with basic auth
        import requests
        response = requests.get(
            "https://vhcals4hci.awspoc.club/sap/opu/odata/sap/ZORDER_SRV/?sap-client=100",
            headers=headers,
            timeout=10
        )
        
        print(f"\n📋 OData Service Response:")
        print(f"Status: {response.status_code}")
        print(f"Content: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_client_credentials()
