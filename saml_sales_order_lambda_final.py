import json
import urllib.request
import urllib.error
import logging
import boto3
import base64
import uuid
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

identity_store = boto3.client('identitystore')
IDENTITY_STORE_ID = 'd-9067c76e54'

# SAP Configuration - FINAL CORRECT
SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
SAP_ODATA_URL = "https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet"
CLIENT_ID = "AW07241704C"
CLIENT_SECRET = "Welcome1234$"
SCOPE = "ZORDER_SRV_0001"

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
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id', 'gyanmis')
        customer = query_params.get('Customer', '1000')
        material = query_params.get('Material', 'M001')
        quantity = query_params.get('Quantity', '10')
        
        user_email = get_user_email_from_identity_center(user_id)
        signed_assertion = create_saml_assertion(user_email)
        access_token = exchange_saml_for_token(signed_assertion)
        
        if not access_token:
            return error_response("Failed to obtain OAuth token")
        
        result = create_sales_order(access_token, customer, material, quantity)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True, 'user_email': user_email, 'sales_order': result})
        }
        
    except Exception as e:
        return error_response(str(e))

def get_user_email_from_identity_center(user_id):
    try:
        response = identity_store.list_users(
            IdentityStoreId=IDENTITY_STORE_ID,
            Filters=[{'AttributePath': 'UserName', 'AttributeValue': user_id}]
        )
        if response['Users']:
            emails = response['Users'][0].get('Emails', [])
            if emails:
                return emails[0].get('Value')
        return f"{user_id}@amazon.com"
    except:
        return f"{user_id}@amazon.com"

def create_saml_assertion(user_email):
    assertion_id = f"_{uuid.uuid4()}"
    issue_instant = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    not_on_or_after = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
    
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
    <AuthnStatement AuthnInstant="{issue_instant}">
        <AuthnContext>
            <AuthnContextClassRef>urn:none</AuthnContextClassRef>
        </AuthnContext>
    </AuthnStatement>
</Assertion>"""
    
    return base64.b64encode(assertion_xml.encode()).decode()

def exchange_saml_for_token(signed_assertion):
    auth_b64 = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_b64}"
    }
    
    import urllib.parse
    data = f"grant_type=urn:ietf:params:oauth:grant-type:saml2-bearer&client_id={CLIENT_ID}&scope={SCOPE}&assertion={urllib.parse.quote(signed_assertion, safe='')}"
    
    try:
        req = urllib.request.Request(SAP_TOKEN_URL, data=data.encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8')).get('access_token')
        return None
    except:
        return None

def create_sales_order(access_token, customer, material, quantity):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {"Customer": customer, "Material": material, "Quantity": quantity}
    
    try:
        req = urllib.request.Request(SAP_ODATA_URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 201:
                return {'Status': 'Success', 'Message': 'Sales order created'}
            return {'Status': 'Failed', 'Code': response.status}
    except Exception as e:
        return {'Status': 'Error', 'Message': str(e)}

def error_response(message):
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'success': False, 'error': message})
    }
