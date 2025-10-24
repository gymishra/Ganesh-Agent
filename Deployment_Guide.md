# SAP BTP Integration Suite Deployment Guide
## 3PL to SAP Inventory Adjustment Integration

### Prerequisites

#### SAP BTP Integration Suite
- [ ] Active SAP BTP Integration Suite tenant
- [ ] Integration Developer role assigned
- [ ] Access to Design and Monitor workspaces

#### SAP S/4HANA System
- [ ] SAP S/4HANA system accessible
- [ ] IDOC FSHGMCR01 configured and active
- [ ] User credentials with appropriate authorizations
- [ ] RFC/IDOC communication configured

#### Development Environment
- [ ] SAP Integration Suite SDK (if using local development)
- [ ] Access to source code repository
- [ ] Test data prepared

### Deployment Steps

#### Phase 1: Prepare Integration Artifacts

1. **Import XSD Schemas**
   ```bash
   # Upload to Integration Suite Resources
   - 3PL_Inventory_Source.xsd
   - SAP_FSHGMCR01_Target.xsd
   ```

2. **Upload Groovy Script**
   ```bash
   # Upload to Script Collection
   - InventoryAdjustmentMapping.groovy
   ```

3. **Import Message Mapping**
   ```bash
   # Import mapping artifact
   - 3PL_to_SAP_MessageMapping.xml
   ```

#### Phase 2: Configure Integration Flow

1. **Create New Integration Flow**
   - Name: `3PL_to_SAP_InventoryAdjustment_v1.0`
   - Package: `ColleHaan_Inventory_Integrations`

2. **Configure Sender Channel**
   ```json
   {
     "channelType": "HTTPS",
     "address": "/3pl/inventory/adjustments",
     "authentication": "Basic",
     "authorization": "RoleBased"
   }
   ```

3. **Configure Receiver Channel**
   ```json
   {
     "channelType": "IDOC",
     "system": "SAP_S4HANA",
     "idocType": "FSHGMCR01",
     "messageType": "FSHGMCR"
   }
   ```

4. **Add Processing Steps**
   - Start Event (HTTPS Receiver)
   - Content Modifier (Logging)
   - Script (Validation)
   - Message Mapping
   - Script (Business Logic)
   - Content Modifier (Header Enrichment)
   - Script (Response Logging)
   - End Event (IDOC Sender)

#### Phase 3: Environment Configuration

1. **Development Environment**
   ```properties
   # Configuration Parameters
   sap.host=dev-sap.colehaan.com
   sap.port=8000
   sap.client=100
   sap.systemNumber=00
   sap.username=${secure:dev_sap_user}
   sap.password=${secure:dev_sap_password}
   processing.batchSize=10
   retry.maxAttempts=3
   ```

2. **Test Environment**
   ```properties
   # Configuration Parameters
   sap.host=test-sap.colehaan.com
   sap.port=8000
   sap.client=100
   sap.systemNumber=00
   sap.username=${secure:test_sap_user}
   sap.password=${secure:test_sap_password}
   processing.batchSize=50
   retry.maxAttempts=3
   ```

3. **Production Environment**
   ```properties
   # Configuration Parameters
   sap.host=prod-sap.colehaan.com
   sap.port=8000
   sap.client=100
   sap.systemNumber=00
   sap.username=${secure:prod_sap_user}
   sap.password=${secure:prod_sap_password}
   processing.batchSize=100
   retry.maxAttempts=3
   ```

#### Phase 4: Security Configuration

1. **Create Secure Parameters**
   ```bash
   # In Integration Suite Security Material
   - dev_sap_user (User Credentials)
   - dev_sap_password (Secure Parameter)
   - test_sap_user (User Credentials)
   - test_sap_password (Secure Parameter)
   - prod_sap_user (User Credentials)
   - prod_sap_password (Secure Parameter)
   ```

2. **Configure OAuth/Basic Authentication**
   ```json
   {
     "inbound": {
       "type": "Basic",
       "users": ["3pl_system", "integration_user"],
       "roles": ["ESBMessaging.send"]
     },
     "outbound": {
       "type": "Basic",
       "credentialName": "SAP_S4HANA_Credentials"
     }
   }
   ```

#### Phase 5: Testing

1. **Unit Testing**
   ```bash
   # Test individual components
   - XSD validation
   - Groovy script execution
   - Message mapping transformation
   ```

2. **Integration Testing**
   ```bash
   # Test end-to-end flow
   curl -X POST \
     https://dev-colehaan.it-cpi.cfapps.eu10.hana.ondemand.com/http/3pl/inventory/adjustments \
     -H 'Authorization: Basic <base64-encoded-credentials>' \
     -H 'Content-Type: application/xml' \
     -d @Sample_Test_Data.xml
   ```

3. **SAP System Verification**
   ```bash
   # Check IDOC status in SAP
   - Transaction WE02 (IDOC List)
   - Transaction WE05 (IDOC Overview)
   - Transaction BD87 (Status Monitor)
   ```

#### Phase 6: Monitoring Setup

1. **Configure Message Processing Logs**
   ```json
   {
     "enabled": true,
     "logLevel": "INFO",
     "retentionPeriod": "30 days",
     "attachments": true
   }
   ```

2. **Setup Performance Monitoring**
   ```json
   {
     "metrics": [
       "ProcessingTime",
       "ThroughputPerHour", 
       "ErrorRate",
       "SuccessRate"
     ],
     "alertThresholds": {
       "errorRate": "10%",
       "processingTime": "300 seconds"
     }
   }
   ```

3. **Configure Alerting**
   ```json
   {
     "emailNotifications": {
       "recipients": ["integration-team@colehaan.com"],
       "conditions": [
         "ErrorRate > 10%",
         "ProcessingTime > 300s",
         "ConnectionFailure"
       ]
     }
   }
   ```

### Deployment Checklist

#### Pre-Deployment
- [ ] All artifacts uploaded to Integration Suite
- [ ] Environment parameters configured
- [ ] Security credentials created
- [ ] SAP system connectivity verified
- [ ] Test data prepared

#### Deployment
- [ ] Integration flow deployed to Development
- [ ] Unit tests executed successfully
- [ ] Integration tests passed
- [ ] Performance tests completed
- [ ] Security tests validated

#### Post-Deployment
- [ ] Monitoring configured and active
- [ ] Alerting rules setup
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Runbook created

#### Production Readiness
- [ ] Load testing completed
- [ ] Disaster recovery tested
- [ ] Backup procedures verified
- [ ] Support procedures documented
- [ ] Go-live approval obtained

### Rollback Plan

#### Immediate Rollback
1. **Stop Integration Flow**
   ```bash
   # In Integration Suite Monitor
   - Navigate to Manage Integration Content
   - Select integration flow
   - Click "Undeploy"
   ```

2. **Revert to Previous Version**
   ```bash
   # Deploy previous stable version
   - Select previous version from repository
   - Deploy with previous configuration
   - Verify functionality
   ```

#### Data Recovery
1. **Check Message Queues**
   ```bash
   # Verify no messages in processing
   - Check JMS queues
   - Verify IDOC status in SAP
   - Confirm no pending transactions
   ```

2. **Reprocess Failed Messages**
   ```bash
   # If needed, reprocess messages
   - Extract failed messages from logs
   - Correct data issues
   - Resubmit through integration flow
   ```

### Troubleshooting Guide

#### Common Issues

1. **Connection Errors**
   ```bash
   # Check SAP system connectivity
   - Verify host/port accessibility
   - Check credentials validity
   - Confirm SAP system availability
   ```

2. **Mapping Errors**
   ```bash
   # Debug message mapping
   - Check input data format
   - Verify XSD compliance
   - Test mapping with sample data
   ```

3. **IDOC Processing Errors**
   ```bash
   # SAP IDOC troubleshooting
   - Check IDOC configuration (WE30)
   - Verify partner profiles (WE20)
   - Check authorization objects
   ```

#### Log Analysis
```bash
# Key log locations
- Integration Suite Message Processing Logs
- SAP System Logs (SM21, ST22)
- IDOC Status Logs (WE02, WE05)
```

### Support Contacts

#### Technical Support
- **Integration Team**: integration-team@colehaan.com
- **SAP Basis Team**: sap-basis@colehaan.com
- **3PL Support**: radial-support@colehaan.com

#### Escalation
- **Level 1**: Integration Developer
- **Level 2**: Integration Architect
- **Level 3**: SAP Technical Lead

### Documentation References

- [Integration Documentation](Integration_Documentation.md)
- [SAP Integration Suite Help](https://help.sap.com/docs/SAP_INTEGRATION_SUITE)
- [IDOC Configuration Guide](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)

---

**Deployment Guide Version**: 1.0  
**Last Updated**: 2025-07-29  
**Next Review**: 2025-10-29
