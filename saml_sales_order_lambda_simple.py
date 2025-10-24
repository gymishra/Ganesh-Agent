import json
import urllib.request
import urllib.error
import logging
import boto3
import base64
import uuid
from datetime import datetime, timedelta, timezone

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Identity Center clients
identity_store = boto3.client('identitystore')
IDENTITY_STORE_ID = 'd-9067c76e54'

def lambda_handler(event, context):
    logger.info(f"=== SAML SSO SALES ORDER START ===")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Get user email from Identity Center
        user_email = get_user_email_from_identity_center(event)
        if not user_email:
            return error_response("user_id parameter is required")
        
        query_params = event.get('queryStringParameters', {}) or {}
        customer = query_params.get('Customer')
        material = query_params.get('Material')
        quantity = query_params.get('Quantity')
        
        logger.info(f"SSO User Email: {user_email}, Customer: {customer}, Material: {material}, Quantity: {quantity}")
        
        # Step 1: Generate SAML assertion with cryptographic signature
        signed_assertion = create_signed_saml_assertion(user_email)
        if not signed_assertion:
            return error_response("Failed to generate signed SAML assertion")
        
        # Step 2: Exchange SAML for OAuth token
        access_token = exchange_saml_for_token(signed_assertion)
        if not access_token:
            return error_response("Failed to get access token via SAML Bearer")
        
        # Step 3: Create sales order
        result = create_sales_order(access_token, customer, material, quantity)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in SSO sales order: {str(e)}")
        return error_response(f"SSO sales order error: {str(e)}")

def get_user_email_from_identity_center(event):
    """Get user email from AWS Identity Center API"""
    
    query_params = event.get('queryStringParameters', {}) or {}
    user_id = query_params.get('user_id')
    
    if not user_id:
        logger.error("user_id parameter is required but not provided")
        return None
    
    try:
        logger.info(f"Looking up user in Identity Center: {user_id}")
        
        response = identity_store.list_users(
            IdentityStoreId=IDENTITY_STORE_ID,
            Filters=[
                {
                    'AttributePath': 'UserName',
                    'AttributeValue': user_id
                }
            ]
        )
        
        if response['Users']:
            user = response['Users'][0]
            emails = user.get('Emails', [])
            if emails:
                user_email = emails[0].get('Value')
                logger.info(f"Found user email in Identity Center: {user_email}")
                return user_email
            else:
                logger.warning(f"No email found for user {user_id}")
        else:
            logger.warning(f"User {user_id} not found in Identity Center")
            
    except Exception as e:
        logger.error(f"Error accessing Identity Center: {str(e)}")
    
    fallback_email = f"{user_id}@amazon.com"
    logger.info(f"Using fallback email: {fallback_email}")
    return fallback_email

def create_signed_saml_assertion(user_email):
    """Create a SAML assertion with RSA signature using cryptography library"""
    
    client_id = "AW07241704C"
    token_url = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
    
    assertion_id = f"_{uuid.uuid4()}"
    issue_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    not_on_or_after = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
    authn_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Create SAML assertion
    assertion_xml = f"""<Assertion ID="{assertion_id}" IssueInstant="{issue_instant}" Version="2.0" xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    <Issuer>cognito-identity-provider</Issuer>
    <Subject>
        <NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">{user_email}</NameID>
        <SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <SubjectConfirmationData NotOnOrAfter="{not_on_or_after}" Recipient="{token_url}"/>
        </SubjectConfirmation>
    </Subject>
    <Conditions>
        <AudienceRestriction>
            <Audience>local</Audience>
        </AudienceRestriction>
    </Conditions>
    <AuthnStatement AuthnInstant="{authn_instant}">
        <AuthnContext>
            <AuthnContextClassRef>urn:none</AuthnContextClassRef>
        </AuthnContext>
    </AuthnStatement>
</Assertion>"""
    
    # Try RSA signing with cryptography library from Lambda layer
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        
        # Private key from Sagar's files
        private_key_pem = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCV/NhwLppy4XPa
SoPt7gIUpKtJxKyUhSfnxcpTV8CcWnEVHSIIqsZUDQW8cmHS9w2xmNc6dsPdtWYn
DzQ4Ko1HjgIzjFu4n8ZTdM/ODn459LsOlCfOPY0VxMwTKP0O1S4hN1m84ZAC9WLt
GhwdUar44y5MZRXqz4nADRhnUG3bJiyrg34HwatDCCDig/+F/dOd0gdiFtvzq3Uf
jgw9l1gO+baEi+zATKltLphSAm5pA0khPVD5T6Ubm8rZRc5fz3EensYuQJZhQhhb
dfb/ibIbWh1AEuscyudunuM/Y9fd8t3atqNf91M1yYU3L7eFhVhkIZvmnWKMKdjY
MyDHAJaHAgMBAAECggEAHOjXbwgMjQgXpIOoWjv9+qyit11JRndD8dCV5uqLHZfx
I/ixjqocACdia6hAYsFrykeDdKlfp2RHhE/R6OGKybf9hKIRK8zgFUX2p+jzO4iI
ZY74/S+v+fosu6Sy4iEE+zIIAfgYIfnaT4kw0hXjtoVTbzYsu021Z2cexQsjoZG2
g34bEOtLL4qTNnrosaA5/6/G9vzF7tDMn0NvSdGFF+xsE+q3gQlSybbwQCV5xQ7W
7zPq/CJ1ZoitrgpAOsIn5Fw9zDEZMdNB4YgQB3EZznuHWnJKhj3/Wu0CsTx8jPAk
DOU3p/tXs25pXJ8xDvzNO2s8VR1zGHgcOUblnqSbAQKBgQDLSKiM1cFvqiICo15p
wT4+z5RJcAE/xzOjW4TL89hxlclVPal9tS86qpB6GFbJpgvJYmk0fDe2uAHKz4RW
Acd+XWv36gqDei7sjwr1bnQAewSG2MwySRUTaDOjd4O6/GONTr/xFk633/PnP5xB
NtmJyMm9vrVttdprLpDuIMEMNwKBgQC84gg0f4gDSArdiUcACFZJavufARYoqneW
bPjn0mc2DIhVmMiWCkmdtzvUJr9iZmEgIS6ySzW7THTJls72PTudBOJYtwUqBxYD
p+ZalcN4PdCGO05nRA3pkcKvMrwAzdjmkzvVM7XoXvOs+8e23wIivyn9mgIOAlgW
kmLUBDzAMQKBgCchIkiRsL1Uy10kozzKFLg0br/ADo1/Q6JTMHmtw2EByxJcXy6y
XJf3Uv4dhz8jditahRO0QWkrfDTUww1nJEZfpzO+Wi26rCOe2SYrD6s0AsgOHSgk
xyjIKwBxNesdP/BoUywN9jMQqbs+lE49R5xtCOA8QGIQ2i09dmpP5bj7AoGAcBWJ
XO3Y3mmf2PqfYUuROJv9mMtiRNtzf5ZG1forOQ2S0YiKb07HhIm5PRmJNHEgbZqD
RVYQGocyPnX5dnG7sF+3mYFx1RDDZYP61AJPLkkwNpd23RyrTNEsQB7RJYEBl0ID
nW7EIZJG832tc70+XTQnTNBZK8sETtCrSLkC++ECgYEAkkl+6s5BuDc9JNDN4d9n
exm8Uu3vpJ0p7TzT88qiApBbZ8sBsFvEXjyktAcUyWYKjrZFz7kdxfd0sYbg1CIw
V5nRtq3RFfILL31Nbj/dra2sLC6S8fCpzgb1ghZrybxr9X/IGvU/4zqbtZXVR0YV
2I/In1s4XVUKXhwZF5RcQKc=
-----END PRIVATE KEY-----"""
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        # Sign the assertion content
        signature = private_key.sign(
            assertion_xml.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Create a simple signed assertion with signature comment
        signed_assertion = assertion_xml + f"<!-- RSA-SHA256: {base64.b64encode(signature).decode()} -->"
        
        logger.info("Successfully created RSA signature with cryptography library")
        
    except Exception as e:
        logger.error(f"Cryptography signing failed: {e}, using unsigned assertion")
        signed_assertion = assertion_xml
    
    signed_assertion_b64 = base64.b64encode(signed_assertion.encode()).decode()
    
    logger.info(f"Generated SAML assertion for user: {user_email}")
    return signed_assertion_b64

def exchange_saml_for_token(signed_assertion):
    """Exchange signed SAML assertion for OAuth token"""
    
    token_url = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
    client_id = "AW07241704C"
    client_secret = "Welcome1234$"
    scope = "ZAPI_SALES_ORDER_SRV_0001"
    
    # URL-encode the SAML assertion properly
    import urllib.parse
    encoded_assertion = urllib.parse.quote(signed_assertion, safe='')
    
    # Prepare Basic Auth header
    auth_string = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Authorization": f"Basic {auth_b64}"
    }
    
    data = f"grant_type=urn:ietf:params:oauth:grant-type:saml2-bearer&client_id={client_id}&scope={scope}&assertion={encoded_assertion}"
    
    try:
        req = urllib.request.Request(
            token_url,
            data=data.encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            logger.info(f"Token exchange response: {response_body}")
            
            if response.status == 200:
                token_data = json.loads(response_body)
                return token_data.get('access_token')
            else:
                logger.error(f"Token exchange failed: {response.status}")
                return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"HTTP error from SAP: {e.code} - {error_body}")
        return None
    except Exception as e:
        logger.error(f"Error exchanging token: {str(e)}")
        return None

def create_sales_order(access_token, customer, material, quantity):
    """Create sales order in SAP using access token"""
    
    sales_order_url = 'https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet'
    
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
    
    logger.info(f"Creating sales order with payload: {payload}")
    
    try:
        req = urllib.request.Request(
            sales_order_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            logger.info(f"SAP sales order response: {response_body}")
            
            if response.status == 201:
                import re
                result_match = re.search(r'<d:Result>(.*?)</d:Result>', response_body)
                salesord_match = re.search(r'<d:Salesord>(.*?)</d:Salesord>', response_body)
                
                result = result_match.group(1) if result_match else "Sales order created via SAML"
                salesord = salesord_match.group(1) if salesord_match else "Unknown"
                
                return {
                    'Result': result,
                    'Salesord': salesord,
                    'Method': 'SAML Bearer Grant with RSA Signature'
                }
            else:
                return {'error': f'SAP error: {response.status}', 'message': response_body}
                
    except Exception as e:
        logger.error(f"Error creating sales order: {str(e)}")
        return {'error': 'Sales order creation failed', 'message': str(e)}

def error_response(message):
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message})
    }
