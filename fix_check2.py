import boto3

apigateway_client = boto3.client('apigateway', region_name='us-east-1')

api_id = 'af940tfknk'
resource_id = 'rmg46g'  # check2 resource

# Add method response
try:
    apigateway_client.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        statusCode='200'
    )
    print("Added method response")
except Exception as e:
    print(f"Method response might exist: {e}")

# Add integration response
try:
    apigateway_client.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        statusCode='200'
    )
    print("Added integration response")
except Exception as e:
    print(f"Integration response might exist: {e}")

# Deploy API
apigateway_client.create_deployment(
    restApiId=api_id,
    stageName='prod'
)

print("Deployed API with fixes")
print("Test URL: https://af940tfknk.execute-api.us-east-1.amazonaws.com/prod/check2")
