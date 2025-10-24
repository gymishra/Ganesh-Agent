# 3PL to SAP S/4HANA Inventory Adjustment Integration

## Overview

This integration solution transforms 3PL (Third-Party Logistics) inventory adjustment data from Radial system to SAP S/4HANA IDOC format (FSHGMCR01) using SAP BTP Integration Suite.

## Architecture

```
3PL System (Radial) → SAP BTP Integration Suite → SAP S/4HANA
                           │
                           ├── Message Mapping
                           ├── Groovy Transformation
                           ├── Validation & Error Handling
                           └── Monitoring & Logging
```

## Components

### 1. XSD Schemas

#### Source Schema: `3PL_Inventory_Source.xsd`
- **Purpose**: Defines the structure for incoming 3PL inventory adjustment data
- **Root Element**: `InventoryAdjustments`
- **Key Fields**:
  - TransactionReference1 (Primary mapping key)
  - MaterialNumber
  - Plant/StorageLocation
  - Quantity/UnitOfMeasure
  - MovementType

#### Target Schema: `SAP_FSHGMCR01_Target.xsd`
- **Purpose**: Defines SAP IDOC FSHGMCR01 structure
- **IDOC Type**: FSHGMCR01 (Fashion Goods Movement Create)
- **Message Type**: FSHGMCR
- **Key Segments**:
  - EDI_DC40 (Control Record)
  - E1MBGMCR (Main segment)
  - E1BP2017_GM_HEAD_01 (Header)
  - E1BP2017_GM_CODE (GM Code)
  - E1BP2017_GM_ITEM_CREATE (Item details)

### 2. Message Mapping: `3PL_to_SAP_MessageMapping.xml`

#### Mapping Logic
The mapping follows the original Boomi interface logic where `TransactionReference1` contains encoded information:

**Format**: `PLANT-STLOC-GMCODE-MATERIAL-MOVETYPE-QTY-UOM-EAN-MOVEPLANT-MOVESTLOC`

**Example**: `1000-0001-01-MAT001-301-10-EA-1234567890123-2000-0002`

#### Key Mappings
- **Header Level**:
  - TransactionReference1 → REF_DOC_NO
  - Current Date → DOC_DATE, PSTNG_DATE
  - Generated Doc Number → DOCNUM

- **Item Level**:
  - MaterialNumber → MATERIAL
  - Parsed Plant → PLANT
  - Parsed Storage Location → STGE_LOC
  - Parsed Movement Type → MOVE_TYPE
  - Quantity → ENTRY_QNT
  - UOM → ENTRY_UOM
  - EAN_UPC → EAN_UPC

### 3. Groovy Script: `InventoryAdjustmentMapping.groovy`

#### Key Functions
- **processData()**: Main transformation function
- **mapTransactionReference()**: Parses transaction reference string
- **Validation Functions**: Validates material, plant, quantity, movement type
- **Formatting Functions**: Formats quantity, dates, document numbers

#### Business Logic
- Generates unique IDOC document numbers
- Maps UOM codes to SAP format
- Handles optional fields (MovePlant, MoveStorageLocation)
- Implements error handling and logging

### 4. iFlow Configuration: `3PL_Inventory_iFlow.json`

#### Processing Steps
1. **Receive 3PL Data**: HTTPS endpoint for incoming data
2. **Log Incoming Message**: Audit trail
3. **Validate Input Data**: Business rule validation
4. **Transform to SAP IDOC**: Message mapping
5. **Apply Business Logic**: Groovy script processing
6. **Enrich IDOC Header**: Additional header information
7. **Log Transformed Message**: Audit trail
8. **Send to SAP S/4HANA**: IDOC transmission
9. **Process Response**: Create acknowledgment

#### Error Handling
- **Validation Errors**: Stop processing, send error response
- **Mapping Errors**: Retry with exponential backoff
- **Connection Errors**: Retry with increased intervals
- **Global Error Handler**: Email notifications, error logging

#### Monitoring & Alerting
- Message processing logs (30-day retention)
- Performance metrics (processing time, throughput, error rates)
- Automated alerts for high error rates and processing delays

## Movement Types Supported

| Movement Type | Description | Use Case |
|---------------|-------------|----------|
| 301 | Transfer Posting | Plant to plant transfer |
| 302 | Transfer Posting Reversal | Reverse plant transfer |
| 311 | Transfer to Storage Location | Within plant transfer |
| 312 | Transfer from Storage Location | Reverse storage transfer |
| 701 | Inventory Adjustment (+) | Positive adjustment |
| 702 | Inventory Adjustment (-) | Negative adjustment |

## Data Flow

### Input Format (3PL)
```xml
<InventoryAdjustments>
  <Header>
    <MessageId>3PL-INV-ADJ-20250729-001</MessageId>
    <RecordCount>1</RecordCount>
  </Header>
  <Records>
    <Record>
      <Elements>
        <TransactionReference1>1000-0001-01-MAT001-301-10-EA-1234567890123-2000-0002</TransactionReference1>
        <MaterialNumber>MAT001</MaterialNumber>
        <Quantity>10.000</Quantity>
        <UnitOfMeasure>EA</UnitOfMeasure>
        <!-- Additional fields -->
      </Elements>
    </Record>
  </Records>
</InventoryAdjustments>
```

### Output Format (SAP IDOC)
```xml
<FSHGMCR01>
  <IDOC>
    <EDI_DC40>
      <IDOCTYP>FSHGMCR01</IDOCTYP>
      <MESTYP>FSHGMCR</MESTYP>
      <!-- Control record fields -->
    </EDI_DC40>
    <E1MBGMCR>
      <E1BP2017_GM_HEAD_01>
        <REF_DOC_NO>1000-0001-01-MAT001-301-10-EA-1234567890123-2000-0002</REF_DOC_NO>
        <!-- Header fields -->
      </E1BP2017_GM_HEAD_01>
      <E1BP2017_GM_CODE>
        <GM_CODE>01</GM_CODE>
      </E1BP2017_GM_CODE>
      <E1BP2017_GM_ITEM_CREATE>
        <MATERIAL>MAT001</MATERIAL>
        <PLANT>1000</PLANT>
        <STGE_LOC>0001</STGE_LOC>
        <MOVE_TYPE>301</MOVE_TYPE>
        <ENTRY_QNT>10.000</ENTRY_QNT>
        <ENTRY_UOM>EA</ENTRY_UOM>
        <MOVE_PLANT>2000</MOVE_PLANT>
        <MOVE_STLOC>0002</MOVE_STLOC>
        <!-- Item fields -->
      </E1BP2017_GM_ITEM_CREATE>
    </E1MBGMCR>
  </IDOC>
</FSHGMCR01>
```

## Configuration Parameters

### SAP Connection
- **sap.host**: SAP S/4HANA hostname
- **sap.port**: SAP port (default: 8000)
- **sap.client**: SAP client (default: 100)
- **sap.systemNumber**: SAP system number
- **sap.username**: SAP username (secure)
- **sap.password**: SAP password (secure)

### Processing
- **processing.batchSize**: Records per batch (default: 100)
- **retry.maxAttempts**: Maximum retry attempts (default: 3)

## Security

### Authentication
- **Inbound**: Basic authentication with role-based authorization
- **Outbound**: Basic authentication to SAP using secure credentials

### Encryption
- **In Transit**: TLS 1.2
- **At Rest**: AES-256

### Data Privacy
- **Data Retention**: 90 days
- **Data Classification**: Internal
- **PII Fields**: None identified

## Testing

### Test Cases
1. **Single Record Processing**: Validates single inventory adjustment
2. **Multiple Records Processing**: Validates batch processing
3. **Error Handling**: Tests validation and error scenarios

### Sample Test Data
See `Sample_Test_Data.xml` for comprehensive test scenarios including:
- Plant-to-plant transfers (Movement Type 301)
- Positive inventory adjustments (Movement Type 701)
- Negative inventory adjustments (Movement Type 702)

## Deployment

### Environments
- **Development**: dev-colehaan tenant
- **Test**: test-colehaan tenant  
- **Production**: prod-colehaan tenant

### Deployment Steps
1. Import XSD schemas to Integration Suite
2. Deploy message mapping
3. Upload Groovy script
4. Configure iFlow with environment-specific parameters
5. Deploy and activate iFlow
6. Configure monitoring and alerting
7. Execute test scenarios

## Monitoring & Operations

### Key Metrics
- **Processing Time**: Average time per message
- **Throughput**: Messages processed per hour
- **Success Rate**: Percentage of successful processing
- **Error Rate**: Percentage of failed messages

### Alerts
- High error rate (>10%)
- Processing delays (>300 seconds)
- Connection failures
- Validation failures

### Troubleshooting

#### Common Issues
1. **Validation Errors**: Check input data format and required fields
2. **Mapping Errors**: Verify TransactionReference1 format
3. **Connection Errors**: Check SAP system availability and credentials
4. **IDOC Errors**: Verify SAP IDOC configuration and authorizations

#### Log Analysis
- Check message processing logs in Integration Suite
- Review error attachments for detailed error information
- Monitor SAP IDOC status in SAP system (WE02, WE05)

## References

### SAP Documentation
- [SAP Integration Suite Documentation](https://help.sap.com/docs/SAP_INTEGRATION_SUITE)
- [IDOC FSHGMCR01 Documentation](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE)
- [Groovy Script Development Guide](https://help.sap.com/docs/SAP_INTEGRATION_SUITE/51ab953548be4459bfe8539ecaeee98d/e9fa19e4b8b14b4b9b6b7b5b5b5b5b5b.html)

### Community Resources
- [SAP Community Integration Blog](https://community.sap.com/t5/integration-blog-posts/automating-iflow-documentation-with-sap-integration-suite-and-gemini-ai/ba-p/14153802)
- [SAP Integration Suite Best Practices](https://community.sap.com/topics/integration-suite)

---

**Author**: Q CLI SAP Integration  
**Version**: 1.0  
**Date**: 2025-07-29  
**Status**: Ready for Implementation
