#!/usr/bin/env python3
"""
SAP Full MCP Client for Q CLI
Connects to ECS-based SAP MCP server with all 128 tools via TCP
"""

import json
import sys
import asyncio
import socket
from typing import Any, Dict, Optional

# ECS MCP Server Configuration
# These will be updated after deployment with actual task IPs
MCP_SERVERS = [
    # Will be populated with actual ECS task IPs after deployment
    # Format: ("ip_address", 9000)
]

class SAPFullMCPClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.current_server = None
    
    async def connect(self):
        """Connect to available MCP server"""
        for server_ip, port in MCP_SERVERS:
            try:
                print(f"Attempting to connect to {server_ip}:{port}...", file=sys.stderr)
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10)
                self.socket.connect((server_ip, port))
                self.connected = True
                self.current_server = (server_ip, port)
                print(f"Connected to SAP MCP server at {server_ip}:{port}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"Failed to connect to {server_ip}:{port}: {e}", file=sys.stderr)
                if self.socket:
                    self.socket.close()
                continue
        
        print("Failed to connect to any MCP server", file=sys.stderr)
        return False
    
    def disconnect(self):
        """Disconnect from MCP server"""
        if self.socket:
            self.socket.close()
            self.connected = False
            self.current_server = None
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send MCP request and get response"""
        if not self.connected:
            if not await self.connect():
                return {"error": {"code": -32603, "message": "Failed to connect to MCP server"}}
        
        try:
            # Send request
            request_json = json.dumps(request) + '\n'
            self.socket.send(request_json.encode('utf-8'))
            
            # Receive response
            response_data = b''
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break
            
            # Parse response
            response_str = response_data.decode('utf-8').strip()
            if response_str:
                return json.loads(response_str)
            else:
                return {"error": {"code": -32603, "message": "Empty response from server"}}
        
        except Exception as e:
            print(f"Communication error: {e}", file=sys.stderr)
            self.disconnect()
            return {"error": {"code": -32603, "message": f"Communication error: {str(e)}"}}

# Global client instance
client = SAPFullMCPClient()

async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    
    method = request.get("method")
    
    if method == "initialize":
        # Initialize connection
        if await client.connect():
            # Forward initialize request to actual MCP server
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": request.get("id", 1),
                "params": request.get("params", {})
            }
            response = await client.send_request(init_request)
            return response
        else:
            return {
                "error": {
                    "code": -32603,
                    "message": "Failed to connect to SAP MCP server"
                }
            }
    
    elif method in ["tools/list", "tools/call"]:
        # Forward request to MCP server
        mcp_request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request.get("id", 1),
            "params": request.get("params", {})
        }
        response = await client.send_request(mcp_request)
        return response
    
    else:
        return {
            "error": {
                "code": -32601,
                "message": f"Unknown method: {method}"
            }
        }

async def main():
    """Main MCP client loop"""
    print("SAP Full MCP Client starting...", file=sys.stderr)
    
    # Check if we have server configurations
    if not MCP_SERVERS:
        print("No MCP servers configured. Please update MCP_SERVERS list with ECS task IPs.", file=sys.stderr)
        sys.exit(1)
    
    try:
        while True:
            try:
                line = input()
                if not line:
                    break
                
                request = json.loads(line)
                response = await handle_mcp_request(request)
                
                if "id" in request:
                    response["id"] = request["id"]
                
                print(json.dumps(response))
                sys.stdout.flush()
            
            except EOFError:
                break
            except Exception as e:
                error_response = {
                    "error": {"code": -32603, "message": f"Parse error: {str(e)}"}
                }
                if "id" in locals() and "request" in locals() and "id" in request:
                    error_response["id"] = request["id"]
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
