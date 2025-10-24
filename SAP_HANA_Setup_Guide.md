# SAP HANA + AWS Bedrock Integration Setup Guide
## For GenAI for SAP Curriculum Enhancement

This guide supports the practical integration examples we've developed for your SAP GenAI curriculum, building on our previous document analysis and AWS Bedrock model inventory.

## Database Connection Details

**Your SAP HANA Instance:**
- Host: `98.83.112.225`
- Instance: `02`
- Default Port: `30215` (calculated as 3<instance>15)
- Connection String: `98.83.112.225:30215`

## Required Python Dependencies

```bash
# Install SAP HANA database client
pip install hdbcli

# Install AWS SDK
pip install boto3

# Install data processing libraries
pip install pandas numpy

# Install additional utilities
pip install python-dotenv
```

## Environment Configuration

Create a `.env` file for secure credential management:

```bash
# SAP HANA Configuration
HANA_HOST=98.83.112.225
HANA_INSTANCE=02
HANA_PORT=30215
HANA_USERNAME=your_username
HANA_PASSWORD=your_password
HANA_DATABASE=SYSTEMDB

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model Configuration
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
```

## SAP HANA Connection Testing

```python
#!/usr/bin/env python3
"""
Quick SAP HANA connection test for curriculum setup
"""

import hdbcli.dbapi as hana_db
import os
from dotenv import load_dotenv

load_dotenv()

def test_hana_connection():
    try:
        connection = hana_db.connect(
            address=os.getenv('HANA_HOST'),
            port=int(os.getenv('HANA_PORT')),
            user=os.getenv('HANA_USERNAME'),
            password=os.getenv('HANA_PASSWORD'),
            database=os.getenv('HANA_DATABASE')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        result = cursor.fetchone()
        
        print(f"✅ SAP HANA Connection Successful!")
        print(f"   Server Time: {result[0]}")
        print(f"   Host: {os.getenv('HANA_HOST')}:{os.getenv('HANA_PORT')}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ SAP HANA Connection Failed: {e}")
        return False

if __name__ == "__main__":
    test_hana_connection()
```

## Common SAP Tables for AI Integration

Based on our curriculum enhancement work, these tables provide rich data for AI analysis:

### Sales & Distribution (SD)
- **VBAK** - Sales Document Header
- **VBAP** - Sales Document Item
- **KNA1** - Customer Master (General)
- **KNVV** - Customer Master (Sales)

### Materials Management (MM)
- **MARA** - Material Master (General)
- **MARC** - Material Master (Plant/Storage)
- **EKKO** - Purchase Document Header
- **EKPO** - Purchase Document Item

### Financial Accounting (FI)
- **BKPF** - Accounting Document Header
- **BSEG** - Accounting Document Segment
- **SKA1** - G/L Account Master
- **BSAK** - Vendor Line Items

## AWS Bedrock Models for SAP Integration

From our previous Bedrock model analysis, these models work well with SAP data:

### Text Analysis Models
```python
# For SAP document analysis and insights
MODELS = {
    "amazon.nova-pro-v1:0": "Best for complex SAP business logic",
    "amazon.nova-premier-v1:0": "Highest capability for SAP integration",
    "anthropic.claude-3-5-sonnet-20241022-v2:0": "Excellent for SAP process analysis",
    "amazon.titan-text-premier-v1:0": "Cost-effective for routine SAP queries"
}
```

### Multimodal Models
```python
# For SAP documents, images, and multimedia content
MULTIMODAL_MODELS = {
    "amazon.nova-pro-v1:0": "Text + Image + Video analysis",
    "amazon.nova-canvas-v1:0": "Generate SAP process diagrams",
    "anthropic.claude-3-opus-20240229-v1:0": "Advanced multimodal reasoning"
}
```

## Integration Scenarios for Curriculum

### Scenario 1: Sales Order Intelligence
```sql
-- Extract recent sales orders for AI analysis
SELECT 
    VBELN as order_number,
    ERDAT as creation_date,
    AUART as order_type,
    NETWR as net_value,
    WAERK as currency,
    VKORG as sales_org
FROM VBAK 
WHERE ERDAT >= ADD_DAYS(CURRENT_DATE, -30)
ORDER BY NETWR DESC;
```

### Scenario 2: Customer Behavior Analysis
```sql
-- Customer purchase patterns for AI insights
SELECT 
    k.KUNNR as customer_id,
    k.NAME1 as customer_name,
    k.LAND1 as country,
    COUNT(v.VBELN) as order_count,
    SUM(v.NETWR) as total_value
FROM KNA1 k
JOIN VBAK v ON k.KUNNR = v.KUNNR
WHERE v.ERDAT >= ADD_DAYS(CURRENT_DATE, -90)
GROUP BY k.KUNNR, k.NAME1, k.LAND1
ORDER BY total_value DESC;
```

### Scenario 3: Material Movement Analysis
```sql
-- Material consumption patterns
SELECT 
    m.MATNR as material_number,
    m.MAKTX as material_description,
    m.MTART as material_type,
    SUM(mseg.MENGE) as total_quantity,
    mseg.MEINS as unit
FROM MARA m
JOIN MSEG mseg ON m.MATNR = mseg.MATNR
WHERE mseg.BUDAT >= ADD_DAYS(CURRENT_DATE, -60)
GROUP BY m.MATNR, m.MAKTX, m.MTART, mseg.MEINS
ORDER BY total_quantity DESC;
```

## Security Best Practices

1. **Never hardcode credentials** - Use environment variables or AWS Secrets Manager
2. **Use least privilege access** - Grant minimal required SAP and AWS permissions
3. **Encrypt data in transit** - Use SSL/TLS for all connections
4. **Audit access logs** - Monitor both SAP and AWS access patterns
5. **Data masking** - Anonymize sensitive data before AI processing

## Troubleshooting Common Issues

### HANA Connection Issues
```bash
# Check network connectivity
telnet 98.83.112.225 30215

# Verify HANA client installation
python -c "import hdbcli.dbapi; print('HANA client OK')"
```

### AWS Bedrock Issues
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-east-1
```

## Next Steps for Curriculum Implementation

1. **Test the connection script** with your SAP HANA credentials
2. **Run sample queries** against your SAP tables
3. **Execute Bedrock integration** with sample SAP data
4. **Customize scenarios** based on your specific SAP modules
5. **Create student exercises** using the integration framework

This setup enables the practical, hands-on SAP-AI integration scenarios we identified in our curriculum enhancement work, supporting the 13 visual placeholders and professional specifications we developed previously.
