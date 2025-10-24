import boto3

lambda_client = boto3.client('lambda', region_name='us-east-1')

# Remove existing permission
try:
    lambda_client.remove_permission(
        FunctionName='passkey-checker',
        StatementId='api-gateway-invoke'
    )
    print("Removed existing permission")
except:
    pass

# Add new permission with correct account ID
lambda_client.add_permission(
    FunctionName='passkey-checker',
    StatementId='api-gateway-invoke',
    Action='lambda:InvokeFunction',
    Principal='apigateway.amazonaws.com',
    SourceArn='arn:aws:execute-api:us-east-1:057052272841:af940tfknk/*/*'
)

print("Added Lambda permission for API Gateway")

# Test the API
api_url = 'https://af940tfknk.execute-api.us-east-1.amazonaws.com/prod/check'
print(f"\nAPI URL: {api_url}")
print(f"\nTest with curl:")
print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"passkey": "2025"}}\'')
print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"passkey": "wrong"}}\'')
