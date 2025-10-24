import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Load corrected JSON
with open('weather_request.json', 'r') as f:
    payload_data = json.load(f)

payload = json.dumps(payload_data)

try:
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
        runtimeSessionId='weather-test-12345678901234567890123456789012345',
        payload=payload,
        qualifier="DEFAULT"
    )
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("✅ Weather request success:", response_data)
except Exception as e:
    print(f"❌ Error: {e}")
    print("JSON payload was:", payload)
