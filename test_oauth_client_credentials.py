#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/gyanmis')

def test_oauth_client_credentials():
    try:
        from token_handler import TokenHandler
        
        print("🔑 Testing OAuth2 Client Credentials Grant Type")
        print("=" * 50)
        
        # Initialize with OAuth2 endpoint
        handler = TokenHandler(
            "AW07241704C", 
            "Welcome1234$",
            "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token?sap-client=100"
        )
        
        print("📤 Attempting OAuth2 client credentials...")
        print("Grant Type: client_credentials")
        print("Client ID: AW07241704C")
        print("Scope: ZORDER_SRV_0001")
        
        try:
            headers = handler.get_auth_header("ZORDER_SRV_0001")
            print(f"✅ OAuth2 Token obtained!")
            print(f"Headers: {headers}")
        except Exception as e:
            print(f"❌ OAuth2 failed: {str(e)}")
            print("This confirms SAP OAuth2 endpoint is not configured")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_oauth_client_credentials()
