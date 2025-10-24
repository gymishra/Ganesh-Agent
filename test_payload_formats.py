import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Test different payload formats
test_payloads = [
    # Format 1: Simple string
    "List all people from TripPin service",
    
    # Format 2: Direct JSON bytes
    json.dumps({"prompt": "List all people from TripPin service"}).encode('utf-8'),
    
    # Format 3: Input wrapper
    json.dumps({"input": "List all people from TripPin service"}).encode('utf-8'),
    
    # Format 4: Message format
    json.dumps({"message": "List all people from TripPin service"}).encode('utf-8')
]

for i, payload in enumerate(test_payloads, 1):
    print(f"\n🧪 Testing payload format {i}...")
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
            runtimeSessionId=f'test-session-{i:02d}234567890123456789012345678901234',
            payload=payload,
            qualifier="DEFAULT"
        )
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        print(f"✅ Success with format {i}:", response_data)
        break
    except Exception as e:
        print(f"❌ Format {i} failed: {e}")

print("\n💡 The AgentCore container may need a specific JSON format or have configuration issues.")
