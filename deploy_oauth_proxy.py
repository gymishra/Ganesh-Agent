import boto3
import zipfile
import json

def deploy_oauth_proxy():
    # Create deployment package
    with zipfile.ZipFile('oauth_proxy.zip', 'w') as zip_file:
        zip_file.write('sap_oauth_proxy_lambda.py', 'lambda_function.py')
    
    # AWS clients
    lambda_client = boto3.client('lambda')
    apigateway = boto3.client('apigatewayv2')
    
    # Create/update Lambda function
    try:
        with open('oauth_proxy.zip', 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName='sap-oauth-proxy',
                ZipFile=zip_file.read()
            )
        print("Updated existing Lambda function")
    except lambda_client.exceptions.ResourceNotFoundException:
        with open('oauth_proxy.zip', 'rb') as zip_file:
            response = lambda_client.create_function(
                FunctionName='sap-oauth-proxy',
                Runtime='python3.9',
                Role='arn:aws:iam::YOUR_ACCOUNT:role/lambda-vpc-role',  # Replace with your VPC role
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_file.read()},
                VpcConfig={
                    'SubnetIds': ['subnet-xxxxx'],  # Replace with your VPC subnet
                    'SecurityGroupIds': ['sg-xxxxx']  # Replace with your security group
                },
                Timeout=30
            )
        print(f"Created Lambda function: {response['FunctionArn']}")
    
    print("Deploy complete. Update your YAML tokenUrl to:")
    print("https://YOUR_API_GATEWAY_ID.execute-api.YOUR_REGION.amazonaws.com/token")

if __name__ == "__main__":
    deploy_oauth_proxy()
