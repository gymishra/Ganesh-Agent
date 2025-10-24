#!/usr/bin/env python3
"""
Local test script for SAML OAuth 2.0 flow with SAP - CORRECTED SCOPE
"""

import base64
import requests
import json
import uuid
from datetime import datetime, timedelta, timezone

# Configuration - CORRECTED
SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
SAP_ODATA_URL = "https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet"
CLIENT_ID = "AW07241704C"
CLIENT_SECRET = "Welcome1234$"
SCOPE = "zorder_srv_001"
USER_EMAIL = "gyanmis@amazon.com"

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
    
    data = {"grant_type": "client_credentials", "scope": SCOPE}
    
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
    
    signed_assertion = create_saml_assertion(USER_EMAIL)
    
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

def main():
    """Main test function"""
    print("=== SAML OAuth 2.0 SAP Integration Test ===")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Scope: {SCOPE}")
    print(f"User Email: {USER_EMAIL}")
    print("-" * 50)
    
    # Test both flows
    client_token = test_client_credentials()
    saml_token = test_saml_oauth()
    
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Client Credentials OAuth: {'✓ SUCCESS' if client_token else '✗ FAILED'}")
    print(f"SAML Bearer OAuth: {'✓ SUCCESS' if saml_token else '✗ FAILED'}")

if __name__ == "__main__":
    main()
