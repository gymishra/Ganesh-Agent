#!/usr/bin/env python3
"""
Local test script for SAML OAuth 2.0 flow with SAP
"""

import base64
import requests
import json
import uuid
from datetime import datetime, timedelta, timezone

# Configuration
SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
SAP_ODATA_URL = "https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet"
CLIENT_ID = "AW07241704C"
CLIENT_SECRET = "Welcome1234$"
SCOPE = "ZAPI_SALES_ORDER_SRV_0001"
USER_EMAIL = "gyanmis@amazon.com"

# Private key from Sagar's files
PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCeYYKvVFMd6fK3
uiMlHW2TT7sLF1E9McrX3u1GREaSHz+OzjOPRkorayI3sweUeDk17HkMFW2GjzqW
1SleMyz+1x55C0sGYzKXh18ZkxdL/xT7AeGlxNVG1DWUScd7e7L+R89SNNT3FuQJ
nHxVONQVRmEMfXjauQgjblxb3rmO9CDYz5q/0tCkwslJAXUp2Ey/yyzSZ6yy9d2u
4hIVnFkK62YqjpPlcJtzbf7RD4lb0tOSgz7q64l8vxT+wHVmPdcqMQKasJS7Nu+c
zZU3bjtGQ1PNC8qTsGuezPF+xk6pwx6CFgZD6317jX/i3d1xaj9eQRNSVC8T+quN
T4hfx+CTAgMBAAECggEACs77xKxcCcAT/N7alCdYeYOo755VQHhb7/R6O9/f8wvn
4f6HfUEeQa1LhgKVQ1gbC2eKcT0rHtI6fN2qN5AFg5S5sygGpDZz1ux5nHyxy9Fq
JKEhvZbbuTw1Ndv9HZu5AOp0pxcM65nn0RIZWBWLP7JwYBJWA5M6D3TyH6DpB+zc
rSD9nk4OIXRNKEfI+Lal1BwW8ag2q27wportlN4Rs0Fb7IxMsEbzXU1Eg09qaIJ/
AZHH9yI71omUEZvTwaFfFRvsOPcSf39bcCHUrBYHwLMJXMLrkXfZzXHcr4fZuea+
0ckP0QRm/94fjPKurs97e5kKlXfylV34hqunZ1yftQKBgQDOVY6SyXGnEDQyfixu
7KyHn8ikhnz9W4X/fsGFrMsxlKPXk19A+er58eVt1POGggtpNcrusANlA9+cuFO3
Z0fY79GsEnY23RB7Q6xNNTh0uCvdTjsRJkpw2pv2j65Q3Ls2atwDD0jPSwU1cjin
qGKPfSsx60hxatypWoqx6Ds5XwKBgQDEgQpwmz7hUOBKdbi0lorXT+xgwlWlM69l
5uLAkMojdyJ8FERnHvFnOPnS3LCBH52aCcsV7/hQYyfXkRk9GMv/DyDXz+cO0TGl
+YaphP0lrC7BZ1wjjeLNN1FIsue5eNzvs6Nav2XrrVWU/UR4IBSigmlLow8Ox0dl
9Q4oAKnBTQKBgQDEO/iJwA5YPf/2mas2n98CacOQPdv3tai+MlZpBMqHT/93ElEA
Ye/JYPa7u1EUdu/VUvS6hynjU4jC60erYQ2i04qM5U4Kpbp8EQN4tooH7/S/2Bwz
FkCsDi1QlJvLifJ/MagnPM0ZYRcGGqipQ2rhXsDLDCLswx4z7smDpANXbwKBgGVp
KxgeJn9lm7sRsfcQ0ip4RsdQw550ZAq080Tp9EgFTbi3RO3rHC5nSxa1ainZRR6f
+z0hEQd7hK5NZbcQOwcwqYR2+Qm+kF7VvddymKp+h8qsKvL2YJwD9mEMY2Zmp67V
CHLm4BSW6dnwMwvDkqKjpu+wAS9hTMmjhGDEptbpAoGBAJBcvzecOYwYKmo5gVWX
ykH09a5880mx3dDJ9hkxIczN2WQkTOAb0FnsUKGh0sZ6FiuAE2I8Q7Y7BIT1Ky/p
GHZrh9vsZg+q1KHWQGbENtOv2WOpKIKPMJNdPBosSzfjbcKmXpnxGyU+A2dfCCJW
8P+ExqFK2SiGjM2e3l+HpPs8
-----END PRIVATE KEY-----"""

def create_saml_assertion(user_email):
    """Create SAML assertion for OAuth Bearer grant"""
    assertion_id = f"_{uuid.uuid4()}"
    issue_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    not_on_or_after = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
    authn_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    assertion_xml = f"""<Assertion ID="{assertion_id}" IssueInstant="{issue_instant}" Version="2.0" xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    <Issuer>cognito-identity-provider</Issuer>
    <Subject>
        <NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">{user_email}</NameID>
        <SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <SubjectConfirmationData NotOnOrAfter="{not_on_or_after}" Recipient="{SAP_TOKEN_URL}"/>
        </SubjectConfirmation>
    </Subject>
    <Conditions>
        <AudienceRestriction>
            <Audience>{CLIENT_ID}</Audience>
        </AudienceRestriction>
    </Conditions>
    <AuthnStatement AuthnInstant="{authn_instant}">
        <AuthnContext>
            <AuthnContextClassRef>urn:none</AuthnContextClassRef>
        </AuthnContext>
    </AuthnStatement>
</Assertion>"""
    
    return base64.b64encode(assertion_xml.encode()).decode()

def test_client_credentials():
    """Test basic client credentials flow"""
    print("Testing Client Credentials OAuth...")
    
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_b64}"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": SCOPE
    }
    
    try:
        response = requests.post(SAP_TOKEN_URL, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✓ Client credentials OAuth successful!")
            print(f"  Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
            return token_data.get('access_token')
        else:
            print(f"✗ Client credentials failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Client credentials error: {e}")
        return None

def test_saml_oauth():
    """Test SAML Bearer OAuth flow"""
    print("Testing SAML Bearer OAuth...")
    
    # Create SAML assertion
    signed_assertion = create_saml_assertion(USER_EMAIL)
    
    # Prepare OAuth request
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_b64}"
    }
    
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:saml2-bearer",
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "assertion": signed_assertion
    }
    
    try:
        response = requests.post(SAP_TOKEN_URL, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✓ SAML Bearer OAuth successful!")
            print(f"  Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
            return token_data.get('access_token')
        else:
            print(f"✗ SAML Bearer OAuth failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ SAML Bearer OAuth error: {e}")
        return None

def test_sales_order_creation(access_token, customer="1000", material="M001", quantity="10"):
    """Test sales order creation with OAuth token"""
    print(f"Testing Sales Order Creation...")
    print(f"  Customer: {customer}, Material: {material}, Quantity: {quantity}")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    payload = {
        "Customer": customer,
        "Material": material,
        "Quantity": quantity
    }
    
    try:
        response = requests.post(SAP_ODATA_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            print("✓ Sales order created successfully!")
            
            # Parse response
            import re
            result_match = re.search(r'<d:Result>(.*?)</d:Result>', response.text)
            salesord_match = re.search(r'<d:Salesord>(.*?)</d:Salesord>', response.text)
            
            result = result_match.group(1) if result_match else "Sales order created"
            salesord = salesord_match.group(1) if salesord_match else "Unknown"
            
            print(f"  Result: {result}")
            print(f"  Sales Order: {salesord}")
            return True
        else:
            print(f"✗ Sales order creation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Sales order creation error: {e}")
        return False

def main():
    """Main test function"""
    print("=== SAML OAuth 2.0 SAP Integration Test ===")
    print(f"SAP System: {SAP_TOKEN_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"User Email: {USER_EMAIL}")
    print(f"Scope: {SCOPE}")
    print("-" * 50)
    
    # Test 1: Client Credentials OAuth
    print("\n1. Testing Client Credentials OAuth...")
    client_token = test_client_credentials()
    
    # Test 2: SAML Bearer OAuth
    print("\n2. Testing SAML Bearer OAuth...")
    saml_token = test_saml_oauth()
    
    # Test 3: Sales Order Creation
    if client_token:
        print("\n3. Testing Sales Order with Client Credentials Token...")
        test_sales_order_creation(client_token)
    
    if saml_token:
        print("\n4. Testing Sales Order with SAML Token...")
        test_sales_order_creation(saml_token)
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Client Credentials OAuth: {'✓ SUCCESS' if client_token else '✗ FAILED'}")
    print(f"SAML Bearer OAuth: {'✓ SUCCESS' if saml_token else '✗ FAILED'}")
    
    if not client_token and not saml_token:
        print("\nTroubleshooting:")
        print("- Check SAP system connectivity")
        print("- Verify OAuth client configuration in SAP")
        print("- Ensure SAML certificate is uploaded to SAP STRUST")
        print("- Check user exists in SAP system")

if __name__ == "__main__":
    main()
