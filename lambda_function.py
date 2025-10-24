import json
import urllib3

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        utterance = body.get('body', {}).get('utterance')
        
        if utterance:
            response = call_mcp_server(utterance)
        else:
            response = "Please provide an utterance."
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'response': response})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'response': f'Error: {str(e)}'})
        }

def call_mcp_server(utterance):
    """Call the Strands OData Agent MCP server"""
    try:
        http = urllib3.PoolManager()
        
        response = http.request(
            'POST',
            'https://mqsmy963c0.execute-api.us-east-1.amazonaws.com/prod/chat',
            body=json.dumps({"message": utterance}),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            return data.get('response', 'No response from MCP server')
        else:
            return f"MCP server returned status {response.status}"
            
    except Exception as e:
        return f"Error calling MCP server: {str(e)}"
