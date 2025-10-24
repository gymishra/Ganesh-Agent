import boto3
import json
import zipfile
import time

def deploy_passkey_api():
    # Create clients
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    apigateway_client = boto3.client('apigateway', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    # Create Lambda execution role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName='PasskeyLambdaRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        role_arn = role_response['Role']['Arn']
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName='PasskeyLambdaRole',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print("Created IAM role")
        time.sleep(10)  # Wait for role propagation
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        role_arn = iam_client.get_role(RoleName='PasskeyLambdaRole')['Role']['Arn']
        print("Using existing IAM role")
    
    # Create deployment package
    with zipfile.ZipFile('passkey_lambda.zip', 'w') as zip_file:
        zip_file.write('passkey_lambda.py')
    
    # Deploy Lambda function
    with open('passkey_lambda.zip', 'rb') as zip_file:
        try:
            lambda_response = lambda_client.create_function(
                FunctionName='passkey-checker',
                Runtime='python3.9',
                Role=role_arn,
                Handler='passkey_lambda.lambda_handler',
                Code={'ZipFile': zip_file.read()}
            )
            function_arn = lambda_response['FunctionArn']
            print(f"Created Lambda function: {function_arn}")
            
        except lambda_client.exceptions.ResourceConflictException:
            # Update existing function
            zip_file.seek(0)
            lambda_client.update_function_code(
                FunctionName='passkey-checker',
                ZipFile=zip_file.read()
            )
            function_arn = lambda_client.get_function(FunctionName='passkey-checker')['Configuration']['FunctionArn']
            print("Updated existing Lambda function")
    
    # Create API Gateway
    try:
        api_response = apigateway_client.create_rest_api(
            name='passkey-api',
            description='API for passkey validation'
        )
        api_id = api_response['id']
        print(f"Created API Gateway: {api_id}")
        
    except Exception as e:
        # Get existing API
        apis = apigateway_client.get_rest_apis()
        api_id = None
        for api in apis['items']:
            if api['name'] == 'passkey-api':
                api_id = api['id']
                break
        if not api_id:
            raise e
        print(f"Using existing API Gateway: {api_id}")
    
    # Get root resource
    resources = apigateway_client.get_resources(restApiId=api_id)
    root_id = None
    for resource in resources['items']:
        if resource['path'] == '/':
            root_id = resource['id']
            break
    
    # Create resource
    try:
        resource_response = apigateway_client.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='check'
        )
        resource_id = resource_response['id']
        
    except Exception:
        # Get existing resource
        for resource in resources['items']:
            if resource.get('pathPart') == 'check':
                resource_id = resource['id']
                break
    
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
        
    except Exception as e:
        print(f"Method might already exist: {e}")
    
    # Add Lambda permission for API Gateway
    try:
        lambda_client.add_permission(
            FunctionName='passkey-checker',
            StatementId='api-gateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:us-east-1:*:{api_id}/*/*'
        )
    except Exception:
        pass  # Permission might already exist
    
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
