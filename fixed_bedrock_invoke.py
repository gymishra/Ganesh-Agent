import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Fix: Send payload as bytes, not JSON string
payload = json.dumps({
    "input": {"prompt": "List all people from TripPin service"}
}).encode('utf-8')

try:
    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:057052272841:runtime/odata_mcp_agentcore-iRdgG87Rwb',
        runtimeSessionId='dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshmt',
        payload=payload,
        qualifier="DEFAULT"
    )
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    print("✅ Agent Response:", response_data)
except Exception as e:
    print(f"❌ Error: {e}")
    print("Checking latest logs...")
    
    # Check logs for more details
    import boto3
    logs = boto3.client('logs', region_name='us-east-1')
    try:
        streams = logs.describe_log_streams(
            logGroupName='/aws/bedrock-agentcore/runtimes/odata_mcp_agentcore-iRdgG87Rwb-endpoint_kl93e',
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        if streams['logStreams']:
            events = logs.get_log_events(
                logGroupName='/aws/bedrock-agentcore/runtimes/odata_mcp_agentcore-iRdgG87Rwb-endpoint_kl93e',
                logStreamName=streams['logStreams'][0]['logStreamName'],
                limit=3
            )
            print("Recent logs:")
            for event in events['events'][-3:]:
                print(f"  {event['message']}")
    except Exception as log_error:
        print(f"Could not fetch logs: {log_error}")
