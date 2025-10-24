#!/usr/bin/env python3
"""
Knowledge Distillation: Use MCP server responses to train CodeBERT
"""

import json
import subprocess
import time
from typing import List, Dict, Any
import requests
import asyncio

class MCPKnowledgeDistiller:
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        self.mcp_server_url = mcp_server_url
        self.knowledge_base = []
    
    async def query_mcp_server(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Query the MCP server and get response"""
        try:
            payload = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            response = requests.post(
                f"{self.mcp_server_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def generate_query_variations(self, entity_name: str) -> List[Dict[str, Any]]:
        """Generate various query patterns for an entity"""
        variations = [
            {
                "natural_language": f"Get all {entity_name} records",
                "tool_name": f"filter_{entity_name}",
                "parameters": {},
                "query_type": "list_all"
            },
            {
                "natural_language": f"Find {entity_name} with specific ID",
                "tool_name": f"get_{entity_name}",
                "parameters": {"key": "1"},
                "query_type": "get_by_id"
            },
            {
                "natural_language": f"Count total {entity_name} records",
                "tool_name": f"count_{entity_name}",
                "parameters": {},
                "query_type": "count"
            },
            {
                "natural_language": f"Filter {entity_name} by field value",
                "tool_name": f"filter_{entity_name}",
                "parameters": {"$filter": "field eq 'value'"},
                "query_type": "filter"
            },
            {
                "natural_language": f"Get top 10 {entity_name} ordered by field",
                "tool_name": f"filter_{entity_name}",
                "parameters": {"$top": 10, "$orderby": "field desc"},
                "query_type": "top_ordered"
            }
        ]
        return variations
    
    async def collect_knowledge_from_responses(self, entities: List[str]):
        """Collect knowledge by querying MCP server with various patterns"""
        
        for entity in entities:
            print(f"Collecting knowledge for entity: {entity}")
            
            variations = self.generate_query_variations(entity)
            
            for variation in variations:
                try:
                    # Query the MCP server
                    response = await self.query_mcp_server(
                        variation["tool_name"], 
                        variation["parameters"]
                    )
                    
                    # Extract knowledge from response
                    knowledge_entry = {
                        "natural_language": variation["natural_language"],
                        "tool_call": {
                            "name": variation["tool_name"],
                            "parameters": variation["parameters"]
                        },
                        "response": response,
                        "query_type": variation["query_type"],
                        "entity": entity,
                        "success": "error" not in response
                    }
                    
                    # Add patterns learned from successful responses
                    if knowledge_entry["success"]:
                        knowledge_entry["patterns"] = self.extract_patterns(response)
                    
                    self.knowledge_base.append(knowledge_entry)
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                
                except Exception as e:
                    print(f"Error querying {variation['tool_name']}: {e}")
    
    def extract_patterns(self, response: Dict[str, Any]) -> List[str]:
        """Extract useful patterns from MCP server responses"""
        patterns = []
        
        # Extract data structure patterns
        if "content" in response:
            content = response["content"]
            if isinstance(content, list) and content:
                # Pattern: List response structure
                patterns.append("returns_list_of_objects")
                
                # Pattern: Field types and names
                if isinstance(content[0], dict):
                    field_types = {}
                    for key, value in content[0].items():
                        field_types[key] = type(value).__name__
                    patterns.append(f"field_types: {json.dumps(field_types)}")
            
            elif isinstance(content, dict):
                patterns.append("returns_single_object")
                field_types = {k: type(v).__name__ for k, v in content.items()}
                patterns.append(f"field_types: {json.dumps(field_types)}")
        
        # Extract error patterns
        if "error" in response:
            patterns.append(f"error_pattern: {response['error']}")
        
        return patterns
    
    def generate_codebert_training_data(self) -> List[Dict[str, str]]:
        """Convert collected knowledge into CodeBERT training format"""
        training_data = []
        
        for entry in self.knowledge_base:
            if entry["success"]:
                # Create code representation
                code = f"{entry['tool_call']['name']}({json.dumps(entry['tool_call']['parameters'])})"
                
                training_example = {
                    "natural_language": entry["natural_language"],
                    "code": code,
                    "description": f"OData {entry['query_type']} operation on {entry['entity']}",
                    "patterns": entry.get("patterns", []),
                    "entity": entry["entity"],
                    "query_type": entry["query_type"]
                }
                
                training_data.append(training_example)
                
                # Generate variations based on patterns
                variations = self.generate_code_variations(training_example)
                training_data.extend(variations)
        
        return training_data
    
    def generate_code_variations(self, base_example: Dict[str, str]) -> List[Dict[str, str]]:
        """Generate code variations from base example"""
        variations = []
        
        # Parameter variations
        if "filter_" in base_example["code"]:
            # Different filter patterns
            filter_variations = [
                "field gt 100",
                "field lt 50", 
                "field eq 'active'",
                "field1 eq 'value' and field2 gt 10"
            ]
            
            for filter_expr in filter_variations:
                variation = base_example.copy()
                variation["natural_language"] = f"Filter {base_example['entity']} where {filter_expr}"
                variation["code"] = f"filter_{base_example['entity']}({{'$filter': '{filter_expr}'}})"
                variations.append(variation)
        
        return variations
    
    def save_knowledge_base(self, filename: str):
        """Save collected knowledge base"""
        with open(filename, 'w') as f:
            json.dump({
                "knowledge_base": self.knowledge_base,
                "summary": {
                    "total_entries": len(self.knowledge_base),
                    "successful_queries": len([e for e in self.knowledge_base if e["success"]]),
                    "entities_covered": list(set([e["entity"] for e in self.knowledge_base])),
                    "query_types": list(set([e["query_type"] for e in self.knowledge_base]))
                }
            }, f, indent=2)
    
    def save_training_data(self, filename: str):
        """Save CodeBERT training data"""
        training_data = self.generate_codebert_training_data()
        
        with open(filename, 'w') as f:
            json.dump({
                "version": "1.0",
                "source": "MCP Knowledge Distillation",
                "examples": training_data,
                "metadata": {
                    "total_examples": len(training_data),
                    "entities": list(set([e["entity"] for e in training_data])),
                    "query_types": list(set([e["query_type"] for e in training_data]))
                }
            }, f, indent=2)
        
        print(f"Generated {len(training_data)} training examples from knowledge distillation")

async def main():
    # Initialize distiller
    distiller = MCPKnowledgeDistiller()
    
    # Define entities to learn about (these would come from your OData service)
    entities = ["Products", "Customers", "Orders", "Categories", "Suppliers"]
    
    print("Starting knowledge distillation from MCP server...")
    
    # Collect knowledge
    await distiller.collect_knowledge_from_responses(entities)
    
    # Save knowledge base
    distiller.save_knowledge_base("/home/gyanmis/mcp_knowledge_base.json")
    
    # Generate and save training data
    distiller.save_training_data("/home/gyanmis/codebert_distilled_training_data.json")
    
    print("Knowledge distillation complete!")

if __name__ == "__main__":
    asyncio.run(main())
