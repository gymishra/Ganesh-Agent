import boto3
import json
import zipfile

def deploy_second_lambda():
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    apigateway_client = boto3.client('apigateway', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    # Get existing role
    role_arn = iam_client.get_role(RoleName='PasskeyLambdaRole')['Role']['Arn']
    
    # Create deployment package
    with zipfile.ZipFile('passkey_lambda2.zip', 'w') as zip_file:
        zip_file.write('passkey_lambda2.py')
    
    # Deploy second Lambda function
    with open('passkey_lambda2.zip', 'rb') as zip_file:
        try:
            lambda_response = lambda_client.create_function(
                FunctionName='passkey-checker-2',
                Runtime='python3.9',
                Role=role_arn,
                Handler='passkey_lambda2.lambda_handler',
                Code={'ZipFile': zip_file.read()}
            )
            function_arn = lambda_response['FunctionArn']
            print(f"Created second Lambda function: {function_arn}")
        except lambda_client.exceptions.ResourceConflictException:
            zip_file.seek(0)
            lambda_client.update_function_code(
                FunctionName='passkey-checker-2',
                ZipFile=zip_file.read()
            )
            function_arn = lambda_client.get_function(FunctionName='passkey-checker-2')['Configuration']['FunctionArn']
            print("Updated existing second Lambda function")
    
    # Use existing API Gateway
    api_id = 'af940tfknk'
    
    # Get root resource
    resources = apigateway_client.get_resources(restApiId=api_id)
    root_id = None
    for resource in resources['items']:
        if resource['path'] == '/':
            root_id = resource['id']
            break
    
    # Create new resource for second function
    try:
        resource_response = apigateway_client.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='check2'
        )
        resource_id = resource_response['id']
        print("Created new resource /check2")
    except:
        # Get existing resource
        for resource in resources['items']:
            if resource.get('pathPart') == 'check2':
                resource_id = resource['id']
                break
        print("Using existing resource /check2")
    
    # Create POST method
    try:
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
        print("Created method and integration")
    except Exception as e:
        print(f"Method might already exist: {e}")
    
    # Add Lambda permission
    try:
        lambda_client.remove_permission(
            FunctionName='passkey-checker-2',
            StatementId='api-gateway-invoke'
        )
    except:
        pass
        
    lambda_client.add_permission(
        FunctionName='passkey-checker-2',
        StatementId='api-gateway-invoke',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:us-east-1:057052272841:{api_id}/*/*'
    )
    
    # Deploy API
    apigateway_client.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )
    
    api_url = f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/check2'
    
    print(f"\nSecond Lambda deployed successfully!")
    print(f"API URL: {api_url}")
    print(f"\nTest with curl:")
    print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"passkey": "2025"}}\'')

if __name__ == "__main__":
    deploy_second_lambda()
