#!/usr/bin/env python3
"""
Extract training data from OData MCP server for CodeBERT fine-tuning
"""

import json
import subprocess
import re
from typing import List, Dict, Any

class MCPTrainingDataExtractor:
    def __init__(self, odata_mcp_binary: str, service_url: str):
        self.odata_mcp_binary = odata_mcp_binary
        self.service_url = service_url
        
    def get_service_metadata(self) -> Dict[str, Any]:
        """Extract service metadata and available tools"""
        try:
            # Run the MCP server to get available tools
            cmd = [self.odata_mcp_binary, "--service", self.service_url, "--list-tools"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Error getting metadata: {result.stderr}")
                return {}
        except Exception as e:
            print(f"Error running MCP server: {e}")
            return {}
    
    def generate_code_examples(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate code examples from OData metadata"""
        examples = []
        
        # Extract entity sets and their operations
        for tool in metadata.get('tools', []):
            tool_name = tool.get('name', '')
            description = tool.get('description', '')
            
            # Generate natural language to code mappings
            if tool_name.startswith('filter_'):
                entity = tool_name.replace('filter_', '')
                examples.extend([
                    {
                        "natural_language": f"Get all {entity} records",
                        "code": f"{tool_name}({{}})",
                        "description": f"Retrieve all {entity} entities"
                    },
                    {
                        "natural_language": f"Find {entity} with specific criteria",
                        "code": f"{tool_name}({{'$filter': 'field eq value'}})",
                        "description": f"Filter {entity} entities with OData query"
                    }
                ])
            
            elif tool_name.startswith('get_'):
                entity = tool_name.replace('get_', '')
                examples.append({
                    "natural_language": f"Get specific {entity} by ID",
                    "code": f"{tool_name}({{'key': 'value'}})",
                    "description": f"Retrieve single {entity} entity by key"
                })
            
            elif tool_name.startswith('create_'):
                entity = tool_name.replace('create_', '')
                examples.append({
                    "natural_language": f"Create new {entity}",
                    "code": f"{tool_name}({{'field1': 'value1', 'field2': 'value2'}})",
                    "description": f"Create new {entity} entity"
                })
            
            elif tool_name.startswith('update_'):
                entity = tool_name.replace('update_', '')
                examples.append({
                    "natural_language": f"Update existing {entity}",
                    "code": f"{tool_name}({{'key': 'id', 'field1': 'new_value'}})",
                    "description": f"Update {entity} entity"
                })
        
        return examples
    
    def generate_odata_query_patterns(self) -> List[Dict[str, str]]:
        """Generate OData query pattern examples"""
        patterns = [
            {
                "natural_language": "Filter records where field equals value",
                "code": "{'$filter': 'FieldName eq \\'value\\''}",
                "description": "OData equality filter"
            },
            {
                "natural_language": "Get top 10 records ordered by field",
                "code": "{'$top': 10, '$orderby': 'FieldName desc'}",
                "description": "OData top and orderby"
            },
            {
                "natural_language": "Select specific fields only",
                "code": "{'$select': 'Field1,Field2,Field3'}",
                "description": "OData field selection"
            },
            {
                "natural_language": "Expand related entities",
                "code": "{'$expand': 'RelatedEntity'}",
                "description": "OData navigation property expansion"
            },
            {
                "natural_language": "Filter with multiple conditions",
                "code": "{'$filter': 'Field1 gt 100 and Field2 eq \\'active\\''}",
                "description": "OData complex filter with AND condition"
            }
        ]
        return patterns
    
    def save_training_data(self, examples: List[Dict[str, str]], filename: str):
        """Save training data in format suitable for CodeBERT"""
        training_data = {
            "version": "1.0",
            "source": "OData MCP Bridge",
            "service_url": self.service_url,
            "examples": examples
        }
        
        with open(filename, 'w') as f:
            json.dump(training_data, f, indent=2)
        
        print(f"Saved {len(examples)} training examples to {filename}")

def main():
    # Configuration
    odata_mcp_binary = "/home/gyanmis/odata_mcp_go/odata-mcp"
    service_url = "https://services.odata.org/V4/Northwind/Northwind.svc/"
    
    extractor = MCPTrainingDataExtractor(odata_mcp_binary, service_url)
    
    # Extract metadata (this would need to be adapted based on actual MCP server output)
    print("Extracting service metadata...")
    metadata = extractor.get_service_metadata()
    
    # Generate code examples
    print("Generating code examples...")
    examples = extractor.generate_code_examples(metadata)
    
    # Add OData query patterns
    examples.extend(extractor.generate_odata_query_patterns())
    
    # Save training data
    extractor.save_training_data(examples, "/home/gyanmis/codebert_odata_training_data.json")
    
    print(f"Generated {len(examples)} training examples for CodeBERT fine-tuning")

if __name__ == "__main__":
    main()
