#!/usr/bin/env python3
"""
Custom OData MCP Integration Script

This script demonstrates how to integrate your custom OData metadata
with the MCP server for your AI classifier project.
"""

import json
import subprocess
import os
from typing import Dict, List, Optional

class CustomODataMCPIntegrator:
    def __init__(self, config_file: str = "custom_odata_mcp_config.json"):
        """Initialize with your custom OData configuration"""
        self.config_file = config_file
        self.mcp_binary = "/home/gyanmis/bin/odata-mcp"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load your custom OData service configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file {self.config_file} not found!")
            return {"mcp_servers": {}}
    
    def get_available_services(self) -> List[str]:
        """Get list of configured OData services"""
        return list(self.config.get("mcp_servers", {}).keys())
    
    def get_service_metadata(self, service_name: str) -> Optional[Dict]:
        """Get metadata for a specific service"""
        return self.config.get("mcp_servers", {}).get(service_name)
    
    def test_service_connection(self, service_name: str) -> bool:
        """Test connection to a specific OData service"""
        service_config = self.get_service_metadata(service_name)
        if not service_config:
            print(f"Service {service_name} not found in configuration")
            return False
        
        # Build command from configuration
        cmd = [self.mcp_binary, "--trace"] + service_config["args"]
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env.update(service_config.get("environment", {}))
            
            # Execute with timeout
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=15,
                env=env
            )
            
            if result.returncode == 0:
                print(f"✅ {service_name}: Connection successful!")
                return True
            else:
                print(f"❌ {service_name}: Connection failed")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {service_name}: Connection timed out")
            return False
        except Exception as e:
            print(f"💥 {service_name}: Error - {str(e)}")
            return False
    
    def get_service_tools(self, service_name: str) -> Optional[Dict]:
        """Get available MCP tools for a service"""
        service_config = self.get_service_metadata(service_name)
        if not service_config:
            return None
        
        # Build command
        cmd = [self.mcp_binary, "--trace"] + service_config["args"]
        
        try:
            env = os.environ.copy()
            env.update(service_config.get("environment", {}))
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                env=env
            )
            
            if result.returncode == 0:
                # Parse the JSON output
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    print(f"Failed to parse tools output for {service_name}")
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"Error getting tools for {service_name}: {str(e)}")
            return None
    
    def execute_odata_operation(self, service_name: str, operation: str, parameters: Dict) -> Optional[Dict]:
        """Execute an OData operation using the MCP server"""
        # This would be implemented to actually execute operations
        # For now, it's a placeholder showing the structure
        print(f"Would execute: {operation} on {service_name} with {parameters}")
        return {"status": "placeholder", "operation": operation, "parameters": parameters}
    
    def integrate_with_ai_classifier(self, user_question: str) -> Dict:
        """
        Integration point with your AI classifier
        
        This is where your AI classifier would:
        1. Analyze the user question
        2. Determine which OData service to use
        3. Execute the appropriate operation
        """
        
        # Placeholder for your AI classifier logic
        # Replace this with your actual classifier
        
        if "customer" in user_question.lower():
            service_name = "customer-service"
        elif "order" in user_question.lower():
            service_name = "sales-order-service"
        elif "product" in user_question.lower() or "inventory" in user_question.lower():
            service_name = "inventory-service"
        else:
            service_name = None
        
        if service_name:
            service_config = self.get_service_metadata(service_name)
            return {
                "selected_service": service_name,
                "service_description": service_config.get("description", ""),
                "use_cases": service_config.get("use_cases", []),
                "user_question": user_question
            }
        else:
            return {
                "selected_service": None,
                "error": "Could not determine appropriate service for question",
                "user_question": user_question
            }

def main():
    """Main function to demonstrate the integration"""
    print("🚀 Custom OData MCP Integration Demo")
    print("=" * 50)
    
    # Initialize the integrator
    integrator = CustomODataMCPIntegrator()
    
    # Show available services
    services = integrator.get_available_services()
    print(f"Available services: {services}")
    print()
    
    # Test each service connection
    print("Testing service connections...")
    for service in services:
        integrator.test_service_connection(service)
    print()
    
    # Demo AI classifier integration
    test_questions = [
        "What is the credit limit for customer ABC123?",
        "Show me recent sales orders",
        "Check product inventory levels",
        "Find customer contact information"
    ]
    
    print("AI Classifier Integration Demo:")
    for question in test_questions:
        result = integrator.integrate_with_ai_classifier(question)
        print(f"Q: {question}")
        print(f"Selected Service: {result.get('selected_service', 'None')}")
        print(f"Description: {result.get('service_description', 'N/A')}")
        print("-" * 30)

if __name__ == "__main__":
    main()
