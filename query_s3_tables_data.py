#!/usr/bin/env python3
"""
Script to query AWS S3 Tables data using Amazon Athena
This script helps you access the inventory data from your S3 Tables
"""

import boto3
import json
import time
import pandas as pd
from datetime import datetime

class S3TablesDataExtractor:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.athena_client = boto3.client('athena', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.s3tables_client = boto3.client('s3tables', region_name=region)
        
        # Configuration
        self.table_arn = "arn:aws:s3tables:us-east-1:953841955037:bucket/aws-s3/table/734a81dd-4d68-47af-8081-fb474a486ddd"
        self.database_name = "s3_tables_db"
        self.table_name = "inventory_table"
        self.output_bucket = "aws-athena-query-results-953841955037-us-east-1"  # Update with your Athena results bucket
        
    def get_table_info(self):
        """Get detailed information about the S3 table"""
        try:
            response = self.s3tables_client.get_table(tableARN=self.table_arn)
            print("📊 Table Information:")
            print(f"   Name: {response['name']}")
            print(f"   Type: {response['type']}")
            print(f"   Format: {response['format']}")
            print(f"   Namespace: {response['namespace']}")
            print(f"   Warehouse Location: {response['warehouseLocation']}")
            print(f"   Metadata Location: {response['metadataLocation']}")
            print(f"   Created: {response['createdAt']}")
            print(f"   Modified: {response['modifiedAt']}")
            return response
        except Exception as e:
            print(f"❌ Error getting table info: {e}")
            return None
    
    def create_athena_database(self):
        """Create Athena database if it doesn't exist"""
        query = f"CREATE DATABASE IF NOT EXISTS {self.database_name}"
        return self.execute_athena_query(query)
    
    def create_external_table(self, table_info):
        """Create external table in Athena pointing to S3 Tables data"""
        warehouse_location = table_info['warehouseLocation']
        
        # Create table DDL based on the schema from metadata
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.database_name}.{self.table_name} (
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
        LOCATION '{warehouse_location}/data/'
        TBLPROPERTIES (
            'table_type'='ICEBERG',
            'metadata_location'='{table_info["metadataLocation"]}'
        )
        """
        
        return self.execute_athena_query(create_table_query)
    
    def execute_athena_query(self, query, wait_for_completion=True):
        """Execute Athena query and optionally wait for completion"""
        try:
            print(f"🔍 Executing query: {query[:100]}...")
            
            response = self.athena_client.start_query_execution(
                QueryString=query,
                ResultConfiguration={
                    'OutputLocation': f's3://{self.output_bucket}/'
                },
                WorkGroup='primary'
            )
            
            query_execution_id = response['QueryExecutionId']
            print(f"📋 Query Execution ID: {query_execution_id}")
            
            if wait_for_completion:
                return self.wait_for_query_completion(query_execution_id)
            
            return query_execution_id
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return None
    
    def wait_for_query_completion(self, query_execution_id):
        """Wait for Athena query to complete"""
        while True:
            response = self.athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            
            status = response['QueryExecution']['Status']['State']
            print(f"⏳ Query status: {status}")
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                if status == 'SUCCEEDED':
                    print("✅ Query completed successfully")
                    return response
                else:
                    error_message = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                    print(f"❌ Query failed: {error_message}")
                    return None
            
            time.sleep(2)
    
    def query_inventory_data(self, limit=100):
        """Query the inventory data"""
        query = f"""
        SELECT 
            bucket,
            key,
            size,
            last_modified_date,
            storage_class,
            encryption_status,
            object_tags,
            user_metadata
        FROM {self.database_name}.{self.table_name}
        ORDER BY last_modified_date DESC
        LIMIT {limit}
        """
        
        return self.execute_athena_query(query)
    
    def get_query_results(self, query_execution_id):
        """Get results from completed Athena query"""
        try:
            response = self.athena_client.get_query_results(
                QueryExecutionId=query_execution_id
            )
            
            # Extract column names
            columns = [col['Label'] for col in response['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            
            # Extract data rows
            rows = []
            for row in response['ResultSet']['Rows'][1:]:  # Skip header row
                row_data = [col.get('VarCharValue', '') for col in row['Data']]
                rows.append(row_data)
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=columns)
            return df
            
        except Exception as e:
            print(f"❌ Error getting query results: {e}")
            return None
    
    def export_to_json(self, df, filename='inventory_data.json'):
        """Export DataFrame to JSON"""
        try:
            # Convert DataFrame to JSON
            json_data = df.to_json(orient='records', indent=2, date_format='iso')
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(json_data)
            
            print(f"📁 Data exported to {filename}")
            print(f"📊 Total records: {len(df)}")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return None
    
    def download_manifest_files(self):
        """Download all manifest and metadata files"""
        try:
            table_info = self.get_table_info()
            if not table_info:
                return False
            
            warehouse_location = table_info['warehouseLocation']
            metadata_location = table_info['metadataLocation']
            
            # Parse S3 locations
            warehouse_bucket = warehouse_location.replace('s3://', '').split('/')[0]
            metadata_key = metadata_location.replace(f's3://{warehouse_bucket}/', '')
            
            print(f"📥 Downloading metadata from: {metadata_location}")
            
            # Download metadata file
            self.s3_client.download_file(
                warehouse_bucket, 
                metadata_key, 
                'inventory_metadata.json'
            )
            
            print("✅ Metadata downloaded successfully")
            
            # List and download manifest files
            manifest_prefix = 'metadata/'
            response = self.s3_client.list_objects_v2(
                Bucket=warehouse_bucket,
                Prefix=manifest_prefix
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    filename = key.split('/')[-1]
                    
                    if filename.endswith('.json'):
                        print(f"📥 Downloading: {filename}")
                        self.s3_client.download_file(warehouse_bucket, key, filename)
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading manifest files: {e}")
            return False

def main():
    """Main execution function"""
    print("🚀 S3 Tables Data Extractor")
    print("=" * 50)
    
    extractor = S3TablesDataExtractor()
    
    # Step 1: Get table information
    print("\n📊 Step 1: Getting table information...")
    table_info = extractor.get_table_info()
    
    if not table_info:
        print("❌ Failed to get table information")
        return
    
    # Step 2: Download manifest files
    print("\n📥 Step 2: Downloading manifest and metadata files...")
    extractor.download_manifest_files()
    
    # Step 3: Check if data is available (snapshots exist)
    with open('inventory_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    if not metadata.get('snapshots'):
        print("\n⚠️  Table is still backfilling. No data snapshots available yet.")
        print("   The table is being populated with inventory data.")
        print("   Please wait for the backfill process to complete.")
        print("   You can check back later or monitor the table status.")
        return
    
    # Step 4: Create Athena database and table (if snapshots exist)
    print("\n🏗️  Step 3: Setting up Athena database...")
    extractor.create_athena_database()
    extractor.create_external_table(table_info)
    
    # Step 5: Query the data
    print("\n🔍 Step 4: Querying inventory data...")
    query_result = extractor.query_inventory_data(limit=1000)
    
    if query_result:
        query_execution_id = query_result['QueryExecution']['QueryExecutionId']
        
        # Get results
        print("\n📊 Step 5: Retrieving query results...")
        df = extractor.get_query_results(query_execution_id)
        
        if df is not None and not df.empty:
            # Export to JSON
            print("\n💾 Step 6: Exporting data...")
            extractor.export_to_json(df, 'inventory_data.json')
            
            # Display sample data
            print("\n📋 Sample Data:")
            print(df.head().to_string())
        else:
            print("❌ No data retrieved from query")

if __name__ == "__main__":
    main()
