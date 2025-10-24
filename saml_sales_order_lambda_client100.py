import json
import urllib.request
import boto3
import base64
import uuid
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SAP Configuration with client 100
SAP_TOKEN_URL = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token?sap-client=100"
SAP_ODATA_URL = "https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet?sap-client=100"
CLIENT_ID = "AW07241704C"
CLIENT_SECRET = "Welcome1234$"
SCOPE = "ZORDER_SRV_0001"

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id', 'gyanmis')
        
        user_email = f"{user_id}@amazon.com"
        signed_assertion = create_saml_assertion(user_email)
        access_token = exchange_saml_for_token(signed_assertion)
        
        if not access_token:
            return error_response("Failed to obtain OAuth token")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': True, 'user_email': user_email, 'token': access_token[:20] + '...'})
        }
        
    except Exception as e:
        return error_response(str(e))

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

def error_response(message):
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'success': False, 'error': message})
    }
