import boto3
import json

try:
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')
    
    payload = json.dumps({
        "input": {"prompt": "Hello, can you help me?"}
    })
    
    print("Invoking Bedrock AgentCore...")
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
        runtimeSessionId='test-session-12345678901234567890123456789012345',
        payload=payload
    )
    
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("Success! Agent Response:", response_data)
    
except Exception as e:
    print(f"Error: {e}")
    print("Checking if AgentCore service exists...")
    
    # Try listing available services
    session = boto3.Session()
    available_services = session.get_available_services()
    bedrock_services = [s for s in available_services if 'bedrock' in s]
    print("Available Bedrock services:", bedrock_services)
