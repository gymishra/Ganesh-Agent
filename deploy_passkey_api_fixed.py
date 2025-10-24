import boto3
import json
import zipfile
import time

def deploy_passkey_api():
    # Create clients
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    apigateway_client = boto3.client('apigateway', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    # Get existing role
    try:
        role_arn = iam_client.get_role(RoleName='PasskeyLambdaRole')['Role']['Arn']
        print("Using existing IAM role")
    except:
        print("Role not found")
        return
    
    # Get existing function ARN
    function_arn = lambda_client.get_function(FunctionName='passkey-checker')['Configuration']['FunctionArn']
    
    # Delete existing API if it exists
    try:
        apis = apigateway_client.get_rest_apis()
        for api in apis['items']:
            if api['name'] == 'passkey-api':
                apigateway_client.delete_rest_api(restApiId=api['id'])
                print("Deleted existing API")
                time.sleep(5)
                break
    except Exception:
        pass
    
    # Create new API Gateway
    api_response = apigateway_client.create_rest_api(
        name='passkey-api',
        description='API for passkey validation'
    )
    api_id = api_response['id']
    print(f"Created API Gateway: {api_id}")
    
    # Get root resource
    resources = apigateway_client.get_resources(restApiId=api_id)
    root_id = resources['items'][0]['id']
    
    # Create resource
    resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='check'
    )
    resource_id = resource_response['id']
    
    # Create POST method
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        authorizationType='NONE'
    )
    
    # Set up integration
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations'
    )
    
    # Add method response
    apigateway_client.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        statusCode='200'
    )
    
    # Add integration response
    apigateway_client.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        statusCode='200'
    )
    
    # Add Lambda permission for API Gateway
    try:
        lambda_client.remove_permission(
            FunctionName='passkey-checker',
            StatementId='api-gateway-invoke'
        )
    except:
        pass
        
    lambda_client.add_permission(
        FunctionName='passkey-checker',
        StatementId='api-gateway-invoke',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:us-east-1:*:{api_id}/*/*'
    )
    
    # Deploy API
    apigateway_client.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )
    
    api_url = f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/check'
    
    print(f"\nAPI deployed successfully!")
    print(f"API URL: {api_url}")
    print(f"\nTest with curl:")
    print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"passkey": "2025"}}\'')
    print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"passkey": "wrong"}}\'')
    
    return api_url

if __name__ == "__main__":
    deploy_passkey_api()
