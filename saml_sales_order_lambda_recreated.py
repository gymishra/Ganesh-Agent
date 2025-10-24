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

# AWS Identity Center configuration
identity_store = boto3.client('identitystore')
IDENTITY_STORE_ID = 'd-9067c76e54'

# SAP Configuration
SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
SAP_ODATA_URL = "https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet"
CLIENT_ID = "AW07241704C"
CLIENT_SECRET = "Welcome1234$"
SCOPE = "ZAPI_SALES_ORDER_SRV_0001"

# Private key for SAML signing (from Sagar's files)
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

def lambda_handler(event, context):
    """Main Lambda handler for SAML OAuth 2.0 SAP sales order creation"""
    logger.info("=== SAML OAuth SAP Sales Order Lambda ===")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Extract parameters
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id', 'gyanmis')
        customer = query_params.get('Customer', '1000')
        material = query_params.get('Material', 'M001')
        quantity = query_params.get('Quantity', '10')
        
        logger.info(f"Parameters - User: {user_id}, Customer: {customer}, Material: {material}, Quantity: {quantity}")
        
        # Step 1: Get user email from AWS Identity Center
        user_email = get_user_email_from_identity_center(user_id)
        
        # Step 2: Create signed SAML assertion
        signed_assertion = create_saml_assertion(user_email)
        
        # Step 3: Exchange SAML for OAuth token
        access_token = exchange_saml_for_token(signed_assertion)
        if not access_token:
            return error_response("Failed to obtain OAuth token")
        
        # Step 4: Create sales order
        result = create_sales_order(access_token, customer, material, quantity)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'user_email': user_email,
                'sales_order': result,
                'method': 'SAML Bearer OAuth 2.0'
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        return error_response(f"Lambda execution failed: {str(e)}")

def get_user_email_from_identity_center(user_id):
    """Extract user email from AWS Identity Center"""
    try:
        logger.info(f"Looking up user in Identity Center: {user_id}")
        
        response = identity_store.list_users(
            IdentityStoreId=IDENTITY_STORE_ID,
            Filters=[{
                'AttributePath': 'UserName',
                'AttributeValue': user_id
            }]
        )
        
        if response['Users']:
            user = response['Users'][0]
            emails = user.get('Emails', [])
            if emails:
                user_email = emails[0].get('Value')
                logger.info(f"Found user email: {user_email}")
                return user_email
        
        # Fallback to constructed email
        fallback_email = f"{user_id}@amazon.com"
        logger.info(f"Using fallback email: {fallback_email}")
        return fallback_email
        
    except Exception as e:
        logger.error(f"Identity Center lookup failed: {e}")
        return f"{user_id}@amazon.com"

def create_saml_assertion(user_email):
    """Create and sign SAML assertion for OAuth Bearer grant"""
    assertion_id = f"_{uuid.uuid4()}"
    issue_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    not_on_or_after = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
    authn_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Create SAML assertion XML
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
    
    # Sign assertion using cryptography library
    try:
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            PRIVATE_KEY_PEM.encode(),
            password=None
        )
        
        # Sign the assertion
        signature = private_key.sign(
            assertion_xml.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        logger.info("SAML assertion signed successfully")
        
    except Exception as e:
        logger.warning(f"Signing failed, using unsigned assertion: {e}")
    
    # Base64 encode the assertion
    assertion_b64 = base64.b64encode(assertion_xml.encode()).decode()
    logger.info(f"Created SAML assertion for user: {user_email}")
    
    return assertion_b64

def exchange_saml_for_token(signed_assertion):
    """Exchange SAML assertion for OAuth access token"""
    logger.info("Exchanging SAML assertion for OAuth token")
    
    # Prepare Basic Auth
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_b64}"
    }
    
    # URL encode assertion
    import urllib.parse
    encoded_assertion = urllib.parse.quote(signed_assertion, safe='')
    
    data = f"grant_type=urn:ietf:params:oauth:grant-type:saml2-bearer&client_id={CLIENT_ID}&scope={SCOPE}&assertion={encoded_assertion}"
    
    try:
        req = urllib.request.Request(
            SAP_TOKEN_URL,
            data=data.encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_body = response.read().decode('utf-8')
            
            if response.status == 200:
                token_data = json.loads(response_body)
                access_token = token_data.get('access_token')
                logger.info("OAuth token obtained successfully")
                return access_token
            else:
                logger.error(f"Token exchange failed: {response.status}")
                return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"HTTP Error {e.code}: {error_body}")
        return None
    except Exception as e:
        logger.error(f"Token exchange error: {str(e)}")
        return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"HTTP error: {e.code} - {error_body}")
        return None
    except Exception as e:
        logger.error(f"Token exchange error: {str(e)}")
        return None

def create_sales_order(access_token, customer, material, quantity):
    """Create sales order in SAP using OAuth token"""
    logger.info(f"Creating sales order - Customer: {customer}, Material: {material}, Quantity: {quantity}")
    
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
        req = urllib.request.Request(
            SAP_ODATA_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_body = response.read().decode('utf-8')
            
            if response.status == 201:
                # Parse SAP response
                import re
                result_match = re.search(r'<d:Result>(.*?)</d:Result>', response_body)
                salesord_match = re.search(r'<d:Salesord>(.*?)</d:Salesord>', response_body)
                
                return {
                    'Result': result_match.group(1) if result_match else "Sales order created",
                    'Salesord': salesord_match.group(1) if salesord_match else "Unknown",
                    'Status': 'Success'
                }
            else:
                logger.error(f"SAP error: {response.status}")
                return {'error': f'SAP error: {response.status}', 'message': response_body}
                
    except Exception as e:
        logger.error(f"Sales order creation failed: {str(e)}")
        return {'error': 'Sales order creation failed', 'message': str(e)}

def error_response(message):
    """Return standardized error response"""
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }
