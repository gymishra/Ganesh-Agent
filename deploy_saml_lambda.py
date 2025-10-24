#!/usr/bin/env python3
"""
Deploy SAML OAuth 2.0 Lambda function for SAP sales order creation
"""

import boto3
import json
import zipfile
import os
from pathlib import Path

# AWS clients
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')
apigateway_client = boto3.client('apigateway')

# Configuration
FUNCTION_NAME = 'saml-sap-sales-order'
ROLE_NAME = 'saml-lambda-execution-role'
API_NAME = 'saml-sap-api'

def create_lambda_role():
    """Create IAM role for Lambda function"""
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
        response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for SAML OAuth Lambda function'
        )
        role_arn = response['Role']['Arn']
        print(f"✓ Created IAM role: {role_arn}")
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AWSIdentityStoreReadOnlyAccess'
        ]
        
        for policy in policies:
            iam_client.attach_role_policy(RoleName=ROLE_NAME, PolicyArn=policy)
            print(f"✓ Attached policy: {policy}")
        
        return role_arn
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=ROLE_NAME)
        role_arn = response['Role']['Arn']
        print(f"✓ Using existing IAM role: {role_arn}")
        return role_arn

def create_deployment_package():
    """Create Lambda deployment package"""
    zip_path = '/home/gyanmis/saml_lambda_deployment.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main Lambda function
        zipf.write('/home/gyanmis/saml_sales_order_lambda_recreated.py', 'lambda_function.py')
        print(f"✓ Added lambda_function.py to deployment package")
    
    print(f"✓ Created deployment package: {zip_path}")
    return zip_path

def deploy_lambda_function(role_arn, zip_path):
    """Deploy Lambda function"""
    with open(zip_path, 'rb') as zip_file:
        zip_content = zip_file.read()
    
    try:
        response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='SAML OAuth 2.0 SAP Sales Order Creation',
            Timeout=30,
            MemorySize=256,
            Environment={
                'Variables': {
                    'SAP_TOKEN_URL': 'https://vhcals4hci.awspoc.club/sap/bc/sec/oauth2/token',
                    'SAP_ODATA_URL': 'https://vhcals4hci.awspoc.club/sap/opu/odata/SAP/ZORDER_SRV/sordSet',
                    'CLIENT_ID': 'AW07241704C',
                    'SCOPE': 'ZAPI_SALES_ORDER_SRV_0001'
                }
            }
        )
        function_arn = response['FunctionArn']
        print(f"✓ Created Lambda function: {function_arn}")
        return function_arn
        
    except lambda_client.exceptions.ResourceConflictException:
        # Update existing function
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )
        function_arn = response['FunctionArn']
        print(f"✓ Updated Lambda function: {function_arn}")
        return function_arn

def create_api_gateway(function_arn):
    """Create API Gateway for Lambda function"""
    try:
        # Create REST API
        api_response = apigateway_client.create_rest_api(
            name=API_NAME,
            description='SAML OAuth SAP Sales Order API',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = api_response['id']
        print(f"✓ Created API Gateway: {api_id}")
        
        # Get root resource
        resources = apigateway_client.get_resources(restApiId=api_id)
        root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
        
        # Create resource
        resource_response = apigateway_client.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='sales-order'
        )
        resource_id = resource_response['id']
        
        # Create GET method
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='GET',
            authorizationType='NONE',
            requestParameters={
                'method.request.querystring.user_id': False,
                'method.request.querystring.Customer': False,
                'method.request.querystring.Material': False,
                'method.request.querystring.Quantity': False
            }
        )
        
        # Set up Lambda integration
        account_id = boto3.client('sts').get_caller_identity()['Account']
        region = boto3.Session().region_name
        lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='GET',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        
        # Add Lambda permission for API Gateway
        try:
            lambda_client.add_permission(
                FunctionName=FUNCTION_NAME,
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*"
            )
        except lambda_client.exceptions.ResourceConflictException:
            pass  # Permission already exists
        
        # Deploy API
        apigateway_client.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod/sales-order"
        print(f"✓ API Gateway deployed: {api_url}")
        return api_url
        
    except Exception as e:
        print(f"✗ API Gateway creation failed: {e}")
        return None

def main():
    """Main deployment function"""
    print("=== SAML OAuth Lambda Deployment ===")
    
    try:
        # Step 1: Create IAM role
        print("\n1. Creating IAM role...")
        role_arn = create_lambda_role()
        
        # Step 2: Create deployment package
        print("\n2. Creating deployment package...")
        zip_path = create_deployment_package()
        
        # Step 3: Deploy Lambda function
        print("\n3. Deploying Lambda function...")
        function_arn = deploy_lambda_function(role_arn, zip_path)
        
        # Step 4: Create API Gateway
        print("\n4. Creating API Gateway...")
        api_url = create_api_gateway(function_arn)
        
        # Step 5: Summary
        print("\n" + "="*50)
        print("DEPLOYMENT COMPLETE!")
        print("="*50)
        print(f"Lambda Function: {FUNCTION_NAME}")
        print(f"Function ARN: {function_arn}")
        if api_url:
            print(f"API Endpoint: {api_url}")
            print("\nTest URL:")
            print(f"{api_url}?user_id=gyanmis&Customer=1000&Material=M001&Quantity=10")
        
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"✓ Cleaned up deployment package")
        
    except Exception as e:
        print(f"✗ Deployment failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
