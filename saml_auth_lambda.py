import json
import base64
import boto3
import logging
from datetime import datetime, timedelta
import uuid

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"=== SAML AUTH LAMBDA START ===")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Extract user info from Identity Center JWT (if available)
        headers = event.get('headers', {})
        auth_header = headers.get('authorization', '') or headers.get('Authorization', '')
        
        # For demo, extract user from query params or use default
        query_params = event.get('queryStringParameters', {}) or {}
        user_id = query_params.get('user_id', 'demo-user')
        
        logger.info(f"Generating SAML assertion for user: {user_id}")
        
        # Generate SAML assertion
        saml_assertion = generate_saml_assertion(user_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'saml_assertion': saml_assertion,
                'user_id': user_id,
                'expires_in': 3600
            })
        }
        
    except Exception as e:
        logger.error(f"Error generating SAML assertion: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'SAML generation error: {str(e)}'})
        }

def generate_saml_assertion(user_id):
    """Generate a basic SAML assertion for SAP OAuth"""
    
    # Generate unique IDs
    assertion_id = f"_{uuid.uuid4()}"
    issue_instant = datetime.utcnow().isoformat() + "Z"
    not_on_or_after = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    
    # Basic SAML assertion template
    saml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" 
                 ID="{assertion_id}" 
                 IssueInstant="{issue_instant}" 
                 Version="2.0">
    <saml2:Issuer>https://aws-lambda-saml-idp</saml2:Issuer>
    <saml2:Subject>
        <saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">{user_id}</saml2:NameID>
        <saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <saml2:SubjectConfirmationData NotOnOrAfter="{not_on_or_after}"/>
        </saml2:SubjectConfirmation>
    </saml2:Subject>
    <saml2:Conditions NotOnOrAfter="{not_on_or_after}">
        <saml2:AudienceRestriction>
            <saml2:Audience>https://vhcals4hci.awspoc.club</saml2:Audience>
        </saml2:AudienceRestriction>
    </saml2:Conditions>
    <saml2:AttributeStatement>
        <saml2:Attribute Name="scope">
            <saml2:AttributeValue>ZORDER_SRV_0001</saml2:AttributeValue>
        </saml2:Attribute>
        <saml2:Attribute Name="client_id">
            <saml2:AttributeValue>SYSTEM1</saml2:AttributeValue>
        </saml2:Attribute>
    </saml2:AttributeStatement>
</saml2:Assertion>"""
    
    # For now, return base64 encoded (in production, this should be signed)
    logger.info(f"Generated SAML assertion: {saml_template}")
    return base64.b64encode(saml_template.encode('utf-8')).decode('utf-8')
