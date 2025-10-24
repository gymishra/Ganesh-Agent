#!/usr/bin/env python3
"""
Simple test to check MCP server availability
"""
import subprocess
import json
import os

def test_mcp_server(server_name):
    """Test if an MCP server can be invoked"""
    try:
        # Try to run the server with a timeout
        result = subprocess.run([
            os.path.expanduser("~/.local/bin/uvx"), 
            f"{server_name}@latest", 
            "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return f"✅ {server_name}: Available"
        else:
            return f"❌ {server_name}: Error - {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return f"⏱️ {server_name}: Timeout (may be installing)"
    except Exception as e:
        return f"❌ {server_name}: Exception - {str(e)[:100]}"

def check_mcp_config():
    """Check if MCP configuration exists and is valid"""
    config_path = os.path.expanduser("~/.aws/amazonq/mcp.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return f"✅ MCP Config: Found with {len(config.get('mcpServers', {}))} servers"
        except Exception as e:
            return f"❌ MCP Config: Invalid JSON - {str(e)}"
    else:
        return "❌ MCP Config: Not found"

if __name__ == "__main__":
    print("🔍 Testing MCP Server Setup")
    print("=" * 50)
    
    # Check configuration
    print(check_mcp_config())
    print()
    
    # Test each server
    servers = [
        "awslabs.aws-documentation-mcp-server",
        "awslabs.aws-api-mcp-server", 
        "awslabs.aws-knowledge-mcp-server"
    ]
    
    for server in servers:
        print(test_mcp_server(server))
    
    print()
    print("💡 Note: Even if servers show timeout/error, they may work")
    print("   within Amazon Q CLI due to different invocation methods.")
