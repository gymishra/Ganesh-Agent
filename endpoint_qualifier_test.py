import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

payload = json.dumps({
    "input": {"prompt": "List all people from TripPin service"}
})

try:
    # Use the endpoint qualifier from the logs: endpoint_kl93e
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
        runtimeSessionId='endpoint-test-12345678901234567890123456789012345',
        payload=payload,
        qualifier="endpoint_kl93e"  # Use the endpoint from logs
    )
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("✅ Endpoint qualifier success:", response_data)
except Exception as e:
    print(f"❌ Endpoint qualifier error: {e}")
    
    # Also try without qualifier
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
            runtimeSessionId='no-qualifier-12345678901234567890123456789012345',
            payload=payload
            # No qualifier parameter
        )
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        print("✅ No qualifier success:", response_data)
    except Exception as e2:
        print(f"❌ No qualifier error: {e2}")
        print("Both approaches failed - container may have issues")
