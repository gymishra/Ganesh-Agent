# Adding Your Own OData Metadata - Complete Guide

## 🎯 Overview

You can absolutely add your own OData metadata to the MCP server! Here are several approaches, from simple to advanced:

## 📋 Method 1: Direct Service URL (Recommended)

The easiest way is to point the MCP server directly to your OData service:

```bash
# Basic usage with your service
odata-mcp --service "https://your-sap-system.com/sap/opu/odata/sap/YOUR_SERVICE/"

# With authentication
odata-mcp --user "your-username" --password "your-password" \
  --service "https://your-sap-system.com/sap/opu/odata/sap/YOUR_SERVICE/"

# With specific entities only
odata-mcp --entities "Customer,Order,Product" \
  --service "https://your-sap-system.com/sap/opu/odata/sap/YOUR_SERVICE/"
```

## 📋 Method 2: Using Your Existing Metadata Template

Your `odata_metadata_template.json` is perfect for the AI classifier, and now you can use it with the MCP server too!

### Step 1: Update Your Template with Real URLs

Edit `/home/gyanmis/odata_metadata_template.json`:

```json
{
  "CustomerService": {
    "endpoint": "https://your-actual-sap-system.com/sap/opu/odata/sap/CUSTOMER_SRV/",
    "oauth2_config": {
      "token_endpoint": "https://your-sap-system.com/oauth/token",
      "client_id": "your-real-client-id"
    },
    "purpose": "Manages customer master data, contact information, credit limits...",
    "entities": {
      "Customer": {
        "description": "Customer master data with business relationships...",
        "fields": {
          "CustomerID": "Unique customer identifier used across all systems...",
          "CompanyName": "Legal business name for contracts and billing..."
        }
      }
    }
  }
}
```

### Step 2: Use the Configuration Files

I've created several files to help you:

1. **`custom_odata_mcp_config.json`** - MCP server configurations
2. **`integrate_custom_odata.py`** - Python integration script
3. **`setup_custom_odata.sh`** - Bash setup script

## 📋 Method 3: Environment-Based Configuration

Set up environment variables for easy switching:

```bash
# Set your credentials
export ODATA_USERNAME="your-username"
export ODATA_PASSWORD="your-password"

# Set service URLs
export CUSTOMER_SERVICE_URL="https://your-sap-system.com/sap/opu/odata/sap/CUSTOMER_SRV/"
export SALES_SERVICE_URL="https://your-sap-system.com/sap/opu/odata/sap/SALES_SRV/"
export INVENTORY_SERVICE_URL="https://your-sap-system.com/sap/opu/odata/sap/INVENTORY_SRV/"

# Test each service
odata-mcp --trace --service "$CUSTOMER_SERVICE_URL" --entities "Customer,CustomerAddress"
odata-mcp --trace --service "$SALES_SERVICE_URL" --entities "SalesOrder,SalesOrderItem"
odata-mcp --trace --service "$INVENTORY_SERVICE_URL" --entities "Product,StockMovement"
```

## 📋 Method 4: Integration with Your AI Classifier

Perfect integration with your existing project:

```python
# In your existing odata_model_training.py or similar
class ODataMCPExecutor:
    def __init__(self):
        self.mcp_binary = "/home/gyanmis/bin/odata-mcp"
        self.service_configs = {
            "CustomerService": {
                "url": "https://your-sap-system.com/sap/opu/odata/sap/CUSTOMER_SRV/",
                "entities": ["Customer", "CustomerAddress"],
                "auth": {"user": "username", "password": "password"}
            },
            "SalesOrderService": {
                "url": "https://your-sap-system.com/sap/opu/odata/sap/SALES_SRV/",
                "entities": ["SalesOrder", "SalesOrderItem"],
                "auth": {"user": "username", "password": "password"}
            }
        }
    
    def execute_query(self, service_name, operation, parameters):
        """Execute OData query using MCP server"""
        config = self.service_configs[service_name]
        
        cmd = [
            self.mcp_binary,
            "--service", config["url"],
            "--user", config["auth"]["user"],
            "--password", config["auth"]["password"],
            "--entities", ",".join(config["entities"]),
            "--read-only"
        ]
        
        # Execute the operation
        # Implementation depends on your specific needs
        pass
```

## 🔧 Configuration Examples

### For SAP Systems

```bash
# SAP OData service with CSRF token support
odata-mcp --service "https://your-sap-system:8000/sap/opu/odata/sap/YOUR_SERVICE/" \
  --user "SAP_USER" \
  --password "SAP_PASSWORD" \
  --entities "Customer,Material,SalesOrder" \
  --read-only \
  --tool-shrink
```

### For Microsoft Dynamics

```bash
# Dynamics 365 OData service
odata-mcp --service "https://your-org.crm.dynamics.com/api/data/v9.2/" \
  --user "your-email@company.com" \
  --password "your-password" \
  --entities "account,contact,opportunity" \
  --read-only
```

### For Custom OData Services

```bash
# Your custom .NET/Java OData service
odata-mcp --service "https://api.yourcompany.com/odata/" \
  --user "api-user" \
  --password "api-key" \
  --entities "Product,Order,Customer" \
  --max-items 200
```

## 🚀 Quick Start with Your Services

1. **Update URLs**: Replace placeholder URLs in the config files with your actual endpoints
2. **Set Credentials**: Update username/password or use environment variables
3. **Test Connection**: Run the setup script to verify connectivity
4. **Integrate**: Use the Python script as a starting point for integration

```bash
# Quick test
cd /home/gyanmis
./setup_custom_odata.sh

# Python integration
python3 integrate_custom_odata.py
```

## 🔐 Security Best Practices

1. **Use Environment Variables**: Don't hardcode credentials
2. **Read-Only Mode**: Use `--read-only` for production safety
3. **Entity Filtering**: Limit entities with `--entities` parameter
4. **Network Security**: Ensure proper firewall and VPN setup
5. **Authentication**: Use OAuth2 when available

## 🎯 Integration with Your AI Classifier Workflow

Your complete workflow now looks like:

```
User Question → AI Classifier → Service Selection → MCP Server → OData Service → Response
```

1. **User asks**: "What's the credit limit for customer ABC123?"
2. **AI Classifier** (your existing model): Determines this needs "CustomerService"
3. **MCP Server**: Executes the appropriate OData query
4. **OData Service**: Returns customer data
5. **Response**: Formatted answer to user

## 📊 Monitoring and Debugging

Use these flags for troubleshooting:

```bash
# Debug mode with full trace
odata-mcp --trace --verbose --service "your-service-url"

# Test specific entities
odata-mcp --trace --entities "Customer" --service "your-service-url"

# Check available operations
odata-mcp --trace --read-only --service "your-service-url"
```

## 🎉 You're All Set!

The MCP server is now ready to work with your custom OData metadata. Simply:

1. Replace the placeholder URLs with your actual service endpoints
2. Configure authentication
3. Test the connections
4. Integrate with your existing AI classifier

Your OData AI Classifier project now has a powerful execution layer! 🚀
