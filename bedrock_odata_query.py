import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')
payload = json.dumps({
    "input": {"prompt": "List all people from the TripPin OData service"}
})

try:
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
        runtimeSessionId='dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshmt',
        payload=payload,
        qualifier="DEFAULT"
    )
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("Agent Response:", response_data)
except Exception as e:
    print(f"Error: {e}")
    print("The Bedrock AgentCore runtime appears to have an issue (500 error)")
    print("This could be due to:")
    print("- Runtime not properly deployed")
    print("- MCP server configuration issues") 
    print("- Service unavailable")
