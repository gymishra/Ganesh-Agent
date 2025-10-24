# AWS S3 Tables Data Access Guide

## 🎯 **Current Status**

Your S3 Tables inventory table is currently **BACKFILLING**. This means:

- ✅ **Table exists and is configured correctly**
- ⏳ **Data is being populated from your S3 bucket `sapogrndata`**
- ❌ **No data snapshots available yet for querying**
- 🔄 **Backfill process is ongoing**

## 📊 **Table Information**

- **Table Name**: `inventory`
- **Table ID**: `734a81dd-4d68-47af-8081-fb474a486ddd`
- **Format**: Apache Iceberg
- **Source Bucket**: `sapogrndata`
- **Namespace**: `b_sapogrndata`
- **Status**: BACKFILLING

## ❌ **Why Your Original Command Didn't Work**

```bash
# ❌ This command doesn't exist
aws s3tables get-table-data --bucket aws-s3 --table-id 734a81dd-4d68-47af-8081-fb474a486ddd
```

**Issues:**
1. `get-table-data` is not a valid S3 Tables command
2. S3 Tables doesn't directly return data - it manages metadata
3. Data access requires analytics services like Athena

## ✅ **Correct Ways to Access Your Data**

### **Method 1: Wait for Backfill Completion**

The table is currently being populated. You need to wait for the backfill process to complete.

**Check Status:**
```bash
./check_s3_table_status.sh
```

**What to Look For:**
- Number of snapshots > 0
- Backfill status changes from "BACKFILLING" to "COMPLETED"
- Data files appear in the warehouse location

### **Method 2: Use Amazon Athena (Once Data is Available)**

Once backfill completes, you can query the data using Athena:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS s3_inventory_db;

-- Create external table pointing to S3 Tables
CREATE TABLE s3_inventory_db.inventory_table (
    bucket string,
    key string,
    sequence_number string,
    version_id string,
    is_delete_marker boolean,
    size bigint,
    last_modified_date timestamp,
    e_tag string,
    storage_class string,
    is_multipart boolean,
    encryption_status string,
    is_bucket_key_enabled boolean,
    kms_key_arn string,
    checksum_algorithm string,
    object_tags map<string,string>,
    user_metadata map<string,string>
)
STORED AS PARQUET
LOCATION 's3://734a81dd-4d68-47af-hgyt1by31wbnezdejhddi1uuo6bfquse1b--table-s3/data/'
TBLPROPERTIES (
    'table_type'='ICEBERG'
);

-- Query the data
SELECT 
    bucket,
    key,
    size,
    last_modified_date,
    storage_class
FROM s3_inventory_db.inventory_table
WHERE bucket = 'sapogrndata'
ORDER BY last_modified_date DESC
LIMIT 100;
```

### **Method 3: Direct S3 Access (Once Data is Available)**

Once backfill completes, you can access the Parquet files directly:

```bash
# List data files
aws s3 ls s3://734a81dd-4d68-47af-hgyt1by31wbnezdejhddi1uuo6bfquse1b--table-s3/data/ --recursive

# Download data files
aws s3 sync s3://734a81dd-4d68-47af-hgyt1by31wbnezdejhddi1uuo6bfquse1b--table-s3/data/ ./data/
```

### **Method 4: Python Script (Ready to Use)**

I've created a Python script for you:

```bash
# Install dependencies
pip install boto3 pandas

# Run the script (will check status and download data when available)
python3 query_s3_tables_data.py
```

## 📋 **Data Schema**

Your inventory table contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `bucket` | string | S3 bucket name |
| `key` | string | Object key/path |
| `sequence_number` | string | Ordering sequence |
| `version_id` | string | Object version ID |
| `is_delete_marker` | boolean | Delete marker status |
| `size` | long | Object size in bytes |
| `last_modified_date` | timestamp | Last modified date |
| `e_tag` | string | Object ETag |
| `storage_class` | string | S3 storage class |
| `is_multipart` | boolean | Multipart upload flag |
| `encryption_status` | string | Encryption status |
| `is_bucket_key_enabled` | boolean | S3 Bucket Key status |
| `kms_key_arn` | string | KMS key ARN |
| `checksum_algorithm` | string | Checksum algorithm |
| `object_tags` | map | Object tags |
| `user_metadata` | map | User metadata |

## 🔄 **Monitoring Backfill Progress**

### **Check Status Regularly:**
```bash
# Run this script periodically
./check_s3_table_status.sh
```

### **What Changes When Ready:**
- ✅ `snapshots` array will have entries
- ✅ `backfill-status` will change to "COMPLETED"
- ✅ Data files will appear in warehouse location
- ✅ You can start querying the data

## 📥 **Files Downloaded for You**

I've already downloaded these files:

1. **`table_info.json`** - Complete table metadata
2. **`inventory_metadata.json`** - Iceberg metadata with schema
3. **`data_files.txt`** - List of data files (empty until backfill completes)
4. **`check_s3_table_status.sh`** - Status checking script
5. **`query_s3_tables_data.py`** - Python data extraction script

## ⏰ **Timeline Expectations**

**Backfill Duration Depends On:**
- Size of your `sapogrndata` bucket
- Number of objects in the bucket
- AWS service load

**Typical Timeline:**
- Small buckets (< 1M objects): 1-6 hours
- Medium buckets (1M-10M objects): 6-24 hours
- Large buckets (> 10M objects): 1-3 days

## 🚨 **Troubleshooting**

### **If Backfill Takes Too Long:**
```bash
# Check if there are any issues
aws s3tables get-table --table-arn "arn:aws:s3tables:us-east-1:953841955037:bucket/aws-s3/table/734a81dd-4d68-47af-8081-fb474a486ddd" --region us-east-1
```

### **If You Need Data Immediately:**
You can access your original S3 bucket directly:
```bash
# List objects in your source bucket
aws s3 ls s3://sapogrndata/ --recursive

# Download specific files
aws s3 cp s3://sapogrndata/path/to/file.json ./
```

## 🎯 **Next Steps**

1. **Wait for Backfill**: Monitor using the status script
2. **Prepare Athena**: Set up Athena workgroup and result bucket
3. **Test Queries**: Once data is available, test with small queries
4. **Automate**: Use the Python script for regular data extraction

## 📞 **Need Help?**

If the backfill process seems stuck or you encounter issues:

1. Check AWS Service Health Dashboard
2. Contact AWS Support
3. Consider recreating the table if needed

---

**Status**: Table is backfilling - check back later for data availability  
**Last Checked**: $(date)  
**Next Check**: Run `./check_s3_table_status.sh`
