import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Try using default endpoint without specific runtime ARN
payload = json.dumps({
    "input": {"prompt": "List all people from TripPin service"}
})

try:
    # Use default endpoint approach
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore',  # Without specific ID
        runtimeSessionId='default-session-12345678901234567890123456789012345',
        payload=payload
    )
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("✅ Default endpoint success:", response_data)
except Exception as e:
    print(f"❌ Default endpoint error: {e}")
    
    # Try alternative default format
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn='odata_mcp_agentcore',  # Just the agent name
            runtimeSessionId='default-session-12345678901234567890123456789012345',
            payload=payload
        )
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        print("✅ Agent name format success:", response_data)
    except Exception as e2:
        print(f"❌ Agent name format error: {e2}")
        print("Both default endpoint approaches failed")
