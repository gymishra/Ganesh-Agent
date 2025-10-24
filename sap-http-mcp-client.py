#!/usr/bin/env python3
"""
SAP HTTP MCP Client
Connects Q chat to your ECS-based SAP HTTP wrapper service
"""

import json
import sys
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional

# MCP Server Configuration
MCP_SERVER_URL = "http://sap-http-wrapper-alb-1924887880.us-east-1.elb.amazonaws.com"

class SAPHttpMCPClient:
    def __init__(self):
        self.base_url = MCP_SERVER_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_objects(self, query: str, objType: Optional[str] = None, max: int = 50) -> Dict[str, Any]:
        """Search for SAP objects"""
        payload = {"query": query, "max": max}
        if objType:
            payload["objType"] = objType
        
        async with self.session.post(f"{self.base_url}/api/search-objects", json=payload) as response:
            return await response.json()
    
    async def get_object_source(self, object_source_url: str) -> Dict[str, Any]:
        """Get source code of an object"""
        payload = {"objectSourceUrl": object_source_url}
        
        async with self.session.post(f"{self.base_url}/api/get-object-source", json=payload) as response:
            return await response.json()
    
    async def get_object_types(self) -> Dict[str, Any]:
        """Get available object types"""
        async with self.session.get(f"{self.base_url}/api/object-types") as response:
            return await response.json()
    
    async def syntax_check(self, code: str, **kwargs) -> Dict[str, Any]:
        """Perform syntax check on ABAP code"""
        payload = {"code": code, **kwargs}
        
        async with self.session.post(f"{self.base_url}/api/syntax-check", json=payload) as response:
            return await response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()

# MCP Protocol Implementation
async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    
    method = request.get("method")
    params = request.get("params", {})
    
    async with SAPHttpMCPClient() as client:
        try:
            if method == "tools/list":
                return {
                    "tools": [
                        {
                            "name": "searchObject",
                            "description": "Search for SAP objects by name pattern and type",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search pattern (e.g., 'Z*')"},
                                    "objType": {"type": "string", "description": "Object type (e.g., 'PROG', 'CLAS')"},
                                    "max": {"type": "number", "description": "Maximum results", "default": 50}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "getObjectSource",
                            "description": "Get source code of a SAP object",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "objectSourceUrl": {"type": "string", "description": "Object source URL"}
                                },
                                "required": ["objectSourceUrl"]
                            }
                        },
                        {
                            "name": "objectTypes",
                            "description": "Get available SAP object types",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "syntaxCheckCode",
                            "description": "Perform syntax check on ABAP code",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "description": "ABAP source code"},
                                    "url": {"type": "string", "description": "Object URL"},
                                    "mainUrl": {"type": "string", "description": "Main URL"},
                                    "mainProgram": {"type": "string", "description": "Main program"},
                                    "version": {"type": "string", "description": "Version"}
                                },
                                "required": ["code"]
                            }
                        }
                    ]
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "searchObject":
                    result = await client.search_objects(**arguments)
                elif tool_name == "getObjectSource":
                    result = await client.get_object_source(**arguments)
                elif tool_name == "objectTypes":
                    result = await client.get_object_types()
                elif tool_name == "syntaxCheckCode":
                    result = await client.syntax_check(**arguments)
                else:
                    return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
                
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            elif method == "initialize":
                return {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "sap-http-mcp-client",
                        "version": "1.0.0"
                    }
                }
            
            else:
                return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}
        
        except Exception as e:
            return {"error": {"code": -32603, "message": f"Internal error: {str(e)}"}}

async def main():
    """Main MCP server loop"""
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

if __name__ == "__main__":
    asyncio.run(main())
