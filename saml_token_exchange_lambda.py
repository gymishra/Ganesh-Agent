import json
import urllib.request
import urllib.error
import urllib.parse
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"=== SAML TOKEN EXCHANGE START ===")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Extract SAML assertion from request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse form data
        form_data = urllib.parse.parse_qs(body)
        saml_assertion = form_data.get('assertion', [None])[0]
        scope = form_data.get('scope', ['ZORDER_SRV_0001'])[0]
        
        logger.info(f"SAML assertion received: {saml_assertion[:50] if saml_assertion else 'None'}...")
        logger.info(f"Scope: {scope}")
        
        if not saml_assertion:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing SAML assertion'})
            }
        
        # Exchange SAML assertion for OAuth2 token with SAP
        access_token = exchange_saml_for_token(saml_assertion, scope)
        
        if access_token:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600,
                    'scope': scope
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Failed to exchange SAML assertion for token'})
            }
            
    except Exception as e:
        logger.error(f"Error in SAML token exchange: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Token exchange error: {str(e)}'})
        }

def exchange_saml_for_token(saml_assertion, scope):
    """Exchange SAML assertion for OAuth2 access token from SAP"""
    
    # SAP OAuth2 token endpoint
    token_url = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
    
    # Prepare SAML Bearer grant request with actual client credentials
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:saml2-bearer',
        'assertion': saml_assertion,
        'scope': scope,
        'client_id': 'AW06923421C',
        'client_secret': 'Welcome1234$'
    }
    
    # Encode form data
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    
    # Add Basic Authentication header
    import base64
    credentials = base64.b64encode(f"AW06923421C:Welcome1234$".encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'Basic {credentials}'
    }
    
    logger.info(f"Making SAML Bearer grant request to: {token_url}")
    logger.info(f"Request data: {data}")
    logger.info(f"Request headers: {headers}")
    
    try:
        # Create request
        req = urllib.request.Request(token_url, data=encoded_data, headers=headers, method='POST')
        
        # Make request to SAP
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            logger.info(f"SAP token response status: {response.status}")
            logger.info(f"SAP token response: {response_body}")
            
            if response.status == 200:
                token_data = json.loads(response_body)
                return token_data.get('access_token')
            else:
                logger.error(f"SAP token request failed: {response.status}")
                return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"HTTP error from SAP: {e.code} - {error_body}")
        return None
    except Exception as e:
        logger.error(f"Exception during token exchange: {str(e)}")
        return None
