# Eclipse ECS MCP Testing Guide

## 🎯 Overview
Your Eclipse project is configured to connect to your **ECS-hosted MCP server** with **SAP client 100** using AWS Secrets Manager for authentication.

## 📋 Test Results Summary
✅ **Network Connectivity**: ECS server is reachable  
✅ **HTTPS Connection**: Working  
❌ **Authentication**: Needs SAP credentials (401 error)  
✅ **AWS Secrets Manager**: 9 SAP secrets found  
✅ **Eclipse Plugin**: Project structure is correct  
✅ **MCP Configuration**: Client 100 configured  

## 🚀 Step-by-Step Testing Process

### **Phase 1: Eclipse Setup**

#### 1. Open Eclipse
```bash
cd /home/gyanmis/eclipse
./eclipse
```

#### 2. Import Your Plugin Project
1. **File → Import → General → Existing Projects into Workspace**
2. **Browse** to: `/home/gyanmis/abap-remote-fs-plugin`
3. **Check** "Copy projects into workspace" (optional)
4. **Finish**

#### 3. Verify Project Structure
Your project should show:
```
abap-remote-fs-plugin/
├── src/com/example/abap/remotefs/
│   ├── Activator.java
│   └── views/
│       ├── AbapRemoteView.java (demo)
│       └── AbapRemoteViewECS.java (ECS integration)
├── META-INF/MANIFEST.MF
├── plugin.xml
└── build.properties
```

### **Phase 2: Configure ECS MCP Connection**

#### 1. Update MANIFEST.MF Dependencies
Add these to your `META-INF/MANIFEST.MF`:
```
Require-Bundle: org.eclipse.ui,
 org.eclipse.core.runtime,
 org.eclipse.core.jobs,
 org.eclipse.jface
Import-Package: org.eclipse.core.runtime.jobs
```

#### 2. Configure SAP Credentials
Your ECS MCP server uses these secrets (choose one):
- `sap-credentials` ✅ **Recommended**
- `saplogin`
- `qbusiness-saplogin`

#### 3. Test Secret Access
```bash
# Test if you can access the secret
aws secretsmanager get-secret-value --secret-id sap-credentials --region us-east-1
```

### **Phase 3: Eclipse Testing**

#### 1. **Recommended Perspective: Plug-in Development**
- **Window → Perspective → Open Perspective → Other... → Plug-in Development**

#### 2. **Essential Views Layout**
```
┌─────────────────┬─────────────────┬─────────────────┐
│ Package Explorer│ ABAP ECS MCP    │ Console         │
│                 │ Explorer        │                 │
├─────────────────┼─────────────────┼─────────────────┤
│ Problems        │ Error Log       │ Progress        │
├─────────────────┼─────────────────┼─────────────────┤
│ Variables       │ Properties      │ Debug           │
└─────────────────┴─────────────────┴─────────────────┘
```

#### 3. **Launch Test Instance**
1. **Right-click** your plugin project
2. **Run As → Eclipse Application**
3. New Eclipse instance opens for testing

#### 4. **Open Your ECS MCP View**
In the test Eclipse instance:
1. **Window → Show View → Other...**
2. **ABAP Tools → ABAP ECS MCP Explorer**
3. **OK**

### **Phase 4: Connection Testing**

#### 1. **Monitor Console Output**
Watch for these messages:
```
🌐 ECS ABAP Remote View created - connecting to client 100
🔐 Retrieving SAP credentials from Secrets Manager...
🔗 Testing connection to: https://vhcals4hci.awspoc.club/sap/opu/odata/sap/API_SALES_ORDER_SRV/
📡 Response code: 200 (success) or 401 (auth needed)
```

#### 2. **Expected Behavior**
- **Loading Message**: "Loading from ECS MCP Server..."
- **Progress Job**: Background job fetching data
- **Success**: Tree populated with SAP entities
- **Error**: Check Error Log view

#### 3. **Troubleshooting Common Issues**

| Issue | Solution |
|-------|----------|
| 401 Authentication | Update AWS credentials, check secret access |
| Connection timeout | Check network/firewall settings |
| ClassNotFoundException | Add missing dependencies to MANIFEST.MF |
| View not appearing | Check plugin.xml registration |

### **Phase 5: Advanced Testing**

#### 1. **Test Different Perspectives**
- **Java Perspective**: For debugging Java code
- **Debug Perspective**: For step-through debugging
- **Resource Perspective**: For file operations

#### 2. **Debug Mode Testing**
1. Set breakpoints in `AbapRemoteViewECS.java`
2. **Debug As → Eclipse Application**
3. Step through ECS connection code

#### 3. **Performance Testing**
- Monitor **Progress View** for long operations
- Check **Error Log** for performance warnings
- Test with different network conditions

## 🔧 Configuration Files

### **Eclipse MCP Configuration**
```properties
# /tmp/eclipse_mcp_config.properties
mcp.server.endpoint=https://vhcals4hci.awspoc.club
mcp.sap.client=100
mcp.service.path=/sap/opu/odata/sap/API_SALES_ORDER_SRV/
mcp.auth.type=secrets_manager
mcp.secrets.region=us-east-1
mcp.connection.timeout=30000
```

### **AWS Credentials Check**
```bash
# Verify AWS access
aws sts get-caller-identity
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `sap`)].Name'
```

## 🎯 Success Criteria

### **✅ Working Plugin Should Show:**
1. **ABAP ECS MCP Explorer** view opens without errors
2. **Console** shows successful connection messages
3. **Tree View** populates with SAP entities from client 100
4. **No errors** in Error Log view
5. **Background jobs** complete successfully

### **📊 Expected SAP Entities (Client 100):**
- A_SalesOrder
- A_SalesOrderItem
- A_SalesOrderHeaderPartner
- A_SalesOrderItemPartner
- A_SalesOrderScheduleLine
- A_SalesOrderHeaderPrElement
- A_SalesOrderItemPrElement

## 🚨 Troubleshooting

### **Authentication Issues (401)**
```bash
# Check secret content
aws secretsmanager get-secret-value --secret-id sap-credentials

# Test manual connection
curl -u "username:password" \
  -H "sap-client: 100" \
  "https://vhcals4hci.awspoc.club/sap/opu/odata/sap/API_SALES_ORDER_SRV/\$metadata"
```

### **Plugin Loading Issues**
1. Check **Help → About → Installation Details**
2. Verify plugin appears in list
3. Check **Error Log** for loading errors

### **Network Issues**
```bash
# Test connectivity
ping vhcals4hci.awspoc.club
curl -I https://vhcals4hci.awspoc.club
```

## 🏁 Next Steps After Successful Testing

1. **Implement AWS SDK Integration** for Secrets Manager
2. **Add Error Handling** for network failures
3. **Implement Caching** for better performance
4. **Add User Authentication** UI
5. **Extend to Other SAP Services** beyond Sales Orders

## 📞 Support

If you encounter issues:
1. Check **Console** and **Error Log** views
2. Verify **AWS credentials** and **secret access**
3. Test **network connectivity** to ECS server
4. Validate **SAP client 100** access permissions

---

**🎉 Your Eclipse project is ready to test against your ECS MCP server with SAP client 100!**
