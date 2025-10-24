#!/usr/bin/env python3
import base64
import requests
from datetime import datetime, timedelta, timezone
import uuid

def test_saml_acs_flow():
    print("🔐 Testing SAML Bearer with SAP ACS URL")
    print("=" * 50)
    
    # SAP Configuration with correct ACS URL
    SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
    SAP_ACS_URL = "https://vhcals4hci.awspoc.club/sap/saml2/sp/acs/100"
    CLIENT_ID = "AW07241704C"
    CLIENT_SECRET = "Welcome1234$"
    SCOPE = "ZORDER_SRV_0001"
    
    # Step 1: Create SAML Assertion with correct recipient
    assertion_id = f"_{uuid.uuid4()}"
    issue_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    not_on_or_after = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
    user_email = "gyanmis@amazon.com"
    
    assertion_xml = f"""<Assertion ID="{assertion_id}" IssueInstant="{issue_instant}" Version="2.0" xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    <Issuer>cognito-identity-provider</Issuer>
    <Subject>
        <NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">{user_email}</NameID>
        <SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <SubjectConfirmationData NotOnOrAfter="{not_on_or_after}" Recipient="{SAP_ACS_URL}"/>
        </SubjectConfirmation>
    </Subject>
    <Conditions>
        <AudienceRestriction>
            <Audience>local</Audience>
        </AudienceRestriction>
    </Conditions>
    <AuthnStatement AuthnInstant="{issue_instant}">
        <AuthnContext>
            <AuthnContextClassRef>urn:none</AuthnContextClassRef>
        </AuthnContext>
    </AuthnStatement>
</Assertion>"""
    
    signed_assertion = base64.b64encode(assertion_xml.encode()).decode()
    print(f"✅ SAML Assertion created with ACS recipient")
    print(f"📍 Recipient: {SAP_ACS_URL}")
    print(f"🎯 Audience: local")
    
    # Step 2: Test OAuth2 Token Exchange
    auth_b64 = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
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
    
    print(f"\n🔄 Testing token exchange...")
    
    try:
        response = requests.post(SAP_TOKEN_URL, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"🎉 SUCCESS! OAuth2 token received!")
            print(f"Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"Token Type: {token_data.get('token_type', 'N/A')}")
            return True
        else:
            print(f"❌ Status {response.status_code}: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_saml_acs_flow()
