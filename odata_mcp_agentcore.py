#!/usr/bin/env python3
import json
import subprocess
import sys
import platform
from bedrock_agentcore.runtime import app

def mcp_handler(payload):
    """Handle MCP requests for OData services"""
    try:
        # Parse the payload
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload
        
        # Extract the input/prompt
        prompt = data.get('input', {}).get('prompt', '') or data.get('input', '') or data.get('message', '')
        
        if not prompt:
            return {"error": "No prompt provided"}
        
        # Start OData MCP server if not running
        start_odata_server()
        
        # Process the request through MCP
        result = process_odata_request(prompt)
        
        return {"response": result}
        
    except Exception as e:
        return {"error": f"Handler error: {str(e)}"}

def start_odata_server():
    """Start the OData MCP server with ARM64 compatibility"""
    try:
        arch = platform.machine()
        print(f"Running on architecture: {arch}")
        
        # Use Python-based MCP server instead of binary
        # This avoids the ARM64 binary compatibility issue
        return start_python_mcp_server()
        
    except Exception as e:
        print(f"Failed to start OData server: {e}")
        raise

def start_python_mcp_server():
    """Start Python-based MCP server (ARM64 compatible)"""
    # Instead of using a binary, use our existing working MCP server
    return True

def process_odata_request(prompt):
    """Process OData request using our working MCP endpoint"""
    import requests
    
    try:
        # Call our working Strands OData Agent MCP server
        response = requests.post(
            'https://mqsmy963c0.execute-api.us-east-1.amazonaws.com/prod/chat',
            json={"message": prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response from MCP server')
        else:
            return f"MCP server returned status {response.status_code}"
            
    except Exception as e:
        return f"Error calling MCP server: {str(e)}"

# Register the handler with Bedrock AgentCore
app.register_handler(mcp_handler)

if __name__ == "__main__":
    print(f"Starting OData MCP AgentCore on {platform.machine()} architecture")
    app.run()
