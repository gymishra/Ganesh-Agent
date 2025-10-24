import json
import urllib.request
import urllib.error
import logging
import base64

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    # SAP token endpoint (your internal SAP system)
    sap_token_url = "https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token"
    
    # Extract request body and handle base64 encoding
    body = event.get('body', '')
    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body).decode('utf-8')
    
    body_bytes = body.encode('utf-8') if body else b''
    headers = event.get('headers', {})
    
    logger.info(f"Forwarding request to SAP: {sap_token_url}")
    logger.info(f"Request body: {body}")
    logger.info(f"Request headers: {headers}")
    
    try:
        # Create request
        req = urllib.request.Request(
            sap_token_url,
            data=body_bytes,
            headers={
                'Content-Type': headers.get('content-type', 'application/x-www-form-urlencoded'),
                'Authorization': headers.get('authorization', '')
            },
            method='POST'
        )
        
        # Make request to SAP
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            logger.info(f"SAP response status: {response.status}")
            logger.info(f"SAP response body: {response_body}")
            
        return {
            'statusCode': response.status,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': response_body
        }
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"HTTP error from SAP: {e.code} - {e.reason}")
        logger.error(f"SAP error response: {error_body}")
        return {
            'statusCode': e.code,
            'headers': {'Content-Type': 'application/json'},
            'body': error_body
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Token proxy error: {str(e)}'})
        }
