# OData MCP Server Setup Guide

## Installation Complete! ✅

The OData MCP server has been successfully installed and is ready to use.

### Installation Summary

- **Repository**: Downloaded from https://github.com/oisee/odata_mcp_go
- **Location**: `/home/gyanmis/odata_mcp_go/` (source code)
- **Binary**: `/home/gyanmis/bin/odata-mcp` (executable)
- **Go Version**: 1.22.2
- **Status**: ✅ Tested and working with Northwind OData service

### Quick Test

The server was tested with the public Northwind OData service and successfully generated 157 MCP tools for various entities like:
- Customers, Orders, Products, Suppliers
- Categories, Employees, Shippers
- Various views and summary tables

### Usage Examples

#### 1. Basic Usage (Public OData Service)
```bash
# Test with Northwind v2 service
odata-mcp --trace https://services.odata.org/V2/Northwind/Northwind.svc/

# Test with Northwind v4 service  
odata-mcp --trace https://services.odata.org/V4/Northwind/Northwind.svc/
```

#### 2. With Authentication (SAP/Enterprise Services)
```bash
# Basic authentication
odata-mcp --user myusername --password mypassword --service https://my-sap-system.com/sap/opu/odata/sap/MY_SERVICE/

# Using environment variables (more secure)
export ODATA_USERNAME=myuser
export ODATA_PASSWORD=mypass
odata-mcp --service https://my-sap-system.com/sap/opu/odata/sap/MY_SERVICE/
```

#### 3. Read-Only Mode
```bash
# Read-only mode (no create/update/delete operations)
odata-mcp --read-only --service https://my-service.com/odata/

# Read-only but allow function imports
odata-mcp --read-only-but-functions --service https://my-service.com/odata/
```

#### 4. Filtered Entities
```bash
# Only generate tools for specific entities
odata-mcp --entities "Products,Orders,Customers" --service https://my-service.com/odata/

# Use wildcards
odata-mcp --entities "Product*,Order*" --service https://my-service.com/odata/
```

### Integration with Your OData AI Classifier Project

This MCP server complements your existing OData AI classifier project perfectly:

1. **Your AI Classifier**: Routes user questions to the appropriate OData service
2. **This MCP Server**: Provides the actual interface to interact with OData services
3. **Combined Power**: Natural language → Service selection → Direct OData operations

#### Integration Example

```python
# In your Lambda function or application
import subprocess
import json

def execute_odata_query(service_url, operation, parameters):
    """Execute OData operation using the MCP server"""
    
    # Build the command
    cmd = [
        "/home/gyanmis/bin/odata-mcp",
        "--service", service_url,
        "--read-only",  # For safety in production
        "--tool-shrink"  # Shorter tool names
    ]
    
    # Execute and get available tools
    result = subprocess.run(cmd + ["--trace"], 
                          capture_output=True, text=True)
    
    # Parse the tools and execute the appropriate one
    tools = json.loads(result.stdout)
    # ... implement your logic here
```

### Configuration for Claude Desktop

If you want to use this with Claude Desktop, add this to your configuration:

```json
{
    "mcpServers": {
        "northwind-demo": {
            "command": "/home/gyanmis/bin/odata-mcp",
            "args": [
                "--service",
                "https://services.odata.org/V2/Northwind/Northwind.svc/",
                "--tool-shrink",
                "--read-only"
            ]
        },
        "your-sap-service": {
            "command": "/home/gyanmis/bin/odata-mcp",
            "args": [
                "--service",
                "https://your-sap-system.com/sap/opu/odata/sap/YOUR_SERVICE/",
                "--user",
                "your-username",
                "--password",
                "your-password",
                "--tool-shrink",
                "--entities",
                "Products,Orders,Customers"
            ]
        }
    }
}
```

### Key Features Available

- ✅ **Universal OData Support**: Works with both OData v2 and v4
- ✅ **Dynamic Tool Generation**: Auto-creates MCP tools from metadata
- ✅ **Multiple Authentication**: Basic auth, cookies, anonymous
- ✅ **SAP OData Extensions**: Full SAP support including CSRF tokens
- ✅ **CRUD Operations**: Create, Read, Update, Delete operations
- ✅ **Advanced Queries**: $filter, $select, $expand, $orderby, etc.
- ✅ **Function Imports**: Call OData function imports as MCP tools
- ✅ **Security Options**: Read-only modes, operation filtering
- ✅ **Cross-Platform**: Native Go binary, works anywhere

### Next Steps

1. **Test with your OData services**: Replace the Northwind URL with your actual services
2. **Configure authentication**: Set up credentials for your SAP/enterprise systems
3. **Integrate with your AI classifier**: Use this as the execution layer
4. **Set up monitoring**: Add logging and error handling for production use

### Troubleshooting

- **Network issues**: Use `GOPROXY=direct` if you need to rebuild
- **Authentication**: Test credentials manually first
- **Permissions**: Ensure the binary has execute permissions
- **Path**: Make sure `/home/gyanmis/bin` is in your PATH

### Documentation

Full documentation is available in the repository:
- `/home/gyanmis/odata_mcp_go/README.md` - Complete usage guide
- `/home/gyanmis/odata_mcp_go/IMPLEMENTATION_GUIDE.md` - Technical details
- `/home/gyanmis/odata_mcp_go/examples/` - Configuration examples

The installation is complete and ready for use! 🎉
