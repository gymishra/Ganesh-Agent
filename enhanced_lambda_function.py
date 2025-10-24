import json
import urllib.parse
import requests
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"=== LAMBDA INVOCATION START ===")
    logger.info(f"Full event received from Q Business: {json.dumps(event, indent=2)}")
    logger.info(f"Context: {context}")
    
    client_id = 'SYSTEM1'
    client_secret = 'your_client_secret'
    authorization_url = 'https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/authorize'
    token_url = 'https://klipah5pok.execute-api.us-east-1.amazonaws.com/token'  # Using proxy
    redirect_uri = 'https://vveu05y6.chat.qbusiness.us-east-1.on.aws/oauth/callback'
    scope = 'ZORDER_SRV_0001'

    # Access query parameters from the event
    query_params = event.get('queryStringParameters', {}) or {}
    logger.info(f"Query parameters received: {query_params}")
    
    customer = query_params.get('Customer')
    material = query_params.get('Material') 
    quantity = query_params.get('Quantity')
    
    logger.info(f"Extracted parameters - Customer: {customer}, Material: {material}, Quantity: {quantity}")

    if 'queryStringParameters' in event and query_params and 'code' in query_params:
        logger.info("=== AUTHORIZATION CODE FLOW DETECTED ===")
        # Step 4: Exchange authorization code for access token
        auth_code = query_params['code']
        logger.info(f"Authorization code received: {auth_code}")
        
        access_token = exchange_auth_code_for_token(auth_code, client_id, client_secret, token_url, redirect_uri)
        
        # Use the access token to create the sales order in SAP
        if access_token:
            logger.info(f"Access token obtained successfully: {access_token[:20]}...")
            response = create_sales_order(access_token, customer, material, quantity)
            logger.info(f"Sales order creation response: {response}")
            return {
                'statusCode': 200,
                'body': json.dumps(response)
            }
        else:
            logger.error("Failed to obtain access token")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Failed to get access token'})
            }
    else:
        logger.info("=== INITIATING OAUTH FLOW ===")
        # Step 2: Initiate OAuth flow by redirecting user to SAP authorization URL
        oauth_url = initiate_oauth_flow(authorization_url, client_id, redirect_uri, scope)
        logger.info(f"Generated OAuth URL: {oauth_url}")
        return {
            'statusCode': 302,
            'headers': {
                'Location': oauth_url
            },
            'body': 'Redirecting to SAP OAuth authorization...'
        }

# Function to initiate OAuth flow
def initiate_oauth_flow(authorization_url, client_id, redirect_uri, scope):
    logger.info(f"Initiating OAuth flow with client_id: {client_id}, redirect_uri: {redirect_uri}, scope: {scope}")
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope
    }
    oauth_url = f"{authorization_url}?{urllib.parse.urlencode(params)}"
    logger.info(f"OAuth URL generated: {oauth_url}")
    return oauth_url

# Function to exchange the authorization code for access token
def exchange_auth_code_for_token(auth_code, client_id, client_secret, token_url, redirect_uri):
    logger.info(f"=== EXCHANGING AUTH CODE FOR TOKEN ===")
    logger.info(f"Token URL: {token_url}")
    logger.info(f"Auth code: {auth_code}")
    logger.info(f"Client ID: {client_id}")
    logger.info(f"Redirect URI: {redirect_uri}")
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    logger.info(f"Request data: {data}")
    logger.info(f"Request headers: {headers}")

    try:
        # Make the request to exchange authorization code for access token
        logger.info("Making POST request to token endpoint...")
        response = requests.post(token_url, data=data, headers=headers)
        
        logger.info(f"Token response status: {response.status_code}")
        logger.info(f"Token response headers: {dict(response.headers)}")
        logger.info(f"Token response body: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            logger.info(f"Access token extracted: {access_token[:20] if access_token else 'None'}...")
            logger.info(f"Token type: {token_data.get('token_type')}")
            logger.info(f"Expires in: {token_data.get('expires_in')}")
            logger.info(f"Scope: {token_data.get('scope')}")
            return access_token
        else:
            logger.error(f"Failed to exchange auth code for token: Status {response.status_code}, Body: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception during token exchange: {str(e)}")
        return None

# Function to create a sales order using SAP OData Service
def create_sales_order(access_token, customer, material, quantity):
    logger.info(f"=== CREATING SALES ORDER ===")
    sales_order_url = 'https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet'
    logger.info(f"SAP OData URL: {sales_order_url}")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Data to send to the OData service
    payload = {
        "Customer": customer,
        "Material": material,
        "Quantity": quantity
    }
    
    logger.info(f"Request headers: {headers}")
    logger.info(f"Request payload: {payload}")

    try:
        # Make the request to create the sales order
        logger.info("Making POST request to SAP OData service...")
        response = requests.post(sales_order_url, headers=headers, json=payload)
        
        logger.info(f"SAP OData response status: {response.status_code}")
        logger.info(f"SAP OData response headers: {dict(response.headers)}")
        logger.info(f"SAP OData response body: {response.text}")

        if response.status_code == 201:
            result = response.json()
            logger.info(f"Sales order created successfully: {result}")
            return result
        else:
            logger.error(f"Failed to create sales order: Status {response.status_code}, Body: {response.text}")
            return {
                'error': f'SAP OData error: {response.status_code}',
                'message': response.text
            }
    except Exception as e:
        logger.error(f"Exception during sales order creation: {str(e)}")
        return {
            'error': 'Exception occurred',
            'message': str(e)
        }
