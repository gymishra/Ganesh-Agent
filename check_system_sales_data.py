#!/usr/bin/env python3
"""
Check accessible sales data in SYSTEM schema and other accessible tables
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def check_accessible_sales_data():
    """Check what sales data we can access with current privileges"""
    
    host = "98.83.112.225"
    port = 30215
    username = "system"
    password = "Dilkyakare1234"
    
    connection = None
    
    try:
        print("🔌 Connecting to SAP HANA...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {username}")
        
        # Establish connection
        connection = hana_db.connect(
            address=host,
            port=port,
            user=username,
            password=password
        )
        
        print("✅ Connection successful!")
        
        cursor = connection.cursor()
        
        # Get current timestamp
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        current_time = cursor.fetchone()[0]
        print(f"   Server Time: {current_time}")
        
        print("\n📊 Checking accessible sales-related tables...")
        
        # Check tables in SYSTEM schema that we saw earlier
        system_tables = [
            'SALES_DATA',
            'PRODUCT_DATA', 
            'STORE_DATA',
            'SUPPLIER_DATA',
            'INVENTORY_DATA',
            'AWSEMPLOYEE',
            'STUDENT'
        ]
        
        for table_name in system_tables:
            try:
                print(f"\n🔍 Analyzing {table_name} table:")
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM SYSTEM.{table_name}")
                count = cursor.fetchone()[0]
                print(f"   Record Count: {count:,}")
                
                # Get table structure
                cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH
                FROM TABLE_COLUMNS 
                WHERE SCHEMA_NAME = 'SYSTEM' AND TABLE_NAME = '{table_name}'
                ORDER BY POSITION
                """)
                
                columns = cursor.fetchall()
                if columns:
                    print(f"   Columns ({len(columns)}):")
                    for col_name, data_type, length in columns[:10]:  # Show first 10 columns
                        length_str = f"({length})" if length else ""
                        print(f"     - {col_name}: {data_type}{length_str}")
                    if len(columns) > 10:
                        print(f"     ... and {len(columns) - 10} more columns")
                
                # If this is SALES_DATA, get sample records and find highest value
                if table_name == 'SALES_DATA' and count > 0:
                    print(f"\n💰 Analyzing SALES_DATA for highest values:")
                    
                    # Get sample records to understand structure
                    cursor.execute(f"SELECT TOP 3 * FROM SYSTEM.{table_name}")
                    sample_records = cursor.fetchall()
                    
                    if sample_records:
                        print(f"   Sample records:")
                        for i, record in enumerate(sample_records, 1):
                            print(f"     Record {i}: {record}")
                    
                    # Try to find columns that might contain sales values
                    value_columns = []
                    for col_name, data_type, length in columns:
                        if any(keyword in col_name.upper() for keyword in ['AMOUNT', 'VALUE', 'PRICE', 'TOTAL', 'SALES', 'REVENUE']):
                            value_columns.append(col_name)
                        elif data_type in ['DECIMAL', 'NUMERIC', 'DOUBLE', 'REAL']:
                            value_columns.append(col_name)
                    
                    if value_columns:
                        print(f"   Potential value columns: {', '.join(value_columns)}")
                        
                        # Try to find highest values in each potential column
                        for col in value_columns[:3]:  # Check first 3 value columns
                            try:
                                cursor.execute(f"""
                                SELECT TOP 1 *, {col} as value_column
                                FROM SYSTEM.{table_name} 
                                WHERE {col} IS NOT NULL 
                                ORDER BY {col} DESC
                                """)
                                
                                highest_record = cursor.fetchone()
                                if highest_record:
                                    print(f"   Highest {col}: {highest_record[-1]}")
                                    
                            except Exception as e:
                                print(f"   Could not analyze {col}: {str(e)[:50]}...")
                
            except Exception as e:
                print(f"   ❌ Error accessing {table_name}: {e}")
        
        # Check the salesdata3 table we saw earlier in SAPHANADB
        print(f"\n🔍 Checking salesdata3 table (456,548 records):")
        try:
            # Get table structure first
            cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH
            FROM TABLE_COLUMNS 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'salesdata3'
            ORDER BY POSITION
            """)
            
            columns = cursor.fetchall()
            if columns:
                print(f"   salesdata3 columns ({len(columns)}):")
                for col_name, data_type, length in columns:
                    length_str = f"({length})" if length else ""
                    print(f"     - {col_name}: {data_type}{length_str}")
                
                # Try to access the data
                cursor.execute("SELECT TOP 1 * FROM SAPHANADB.salesdata3")
                sample = cursor.fetchone()
                if sample:
                    print(f"   Sample record: {sample}")
                    
                    # Look for value columns and find highest
                    value_columns = []
                    for col_name, data_type, length in columns:
                        if any(keyword in col_name.upper() for keyword in ['AMOUNT', 'VALUE', 'PRICE', 'TOTAL', 'SALES', 'REVENUE']):
                            value_columns.append(col_name)
                        elif data_type in ['DECIMAL', 'NUMERIC', 'DOUBLE', 'REAL']:
                            value_columns.append(col_name)
                    
                    if value_columns:
                        print(f"   Value columns found: {', '.join(value_columns)}")
                        
                        for col in value_columns[:2]:  # Check first 2 value columns
                            try:
                                cursor.execute(f"""
                                SELECT TOP 5 *, {col} as max_value
                                FROM SAPHANADB.salesdata3 
                                WHERE {col} IS NOT NULL 
                                ORDER BY {col} DESC
                                """)
                                
                                top_records = cursor.fetchall()
                                if top_records:
                                    print(f"\n   🏆 TOP 5 HIGHEST {col} VALUES:")
                                    print(f"   {'-' * 60}")
                                    for i, record in enumerate(top_records, 1):
                                        print(f"   {i}. Value: {record[-1]}")
                                        
                            except Exception as e:
                                print(f"   Could not analyze {col}: {str(e)[:50]}...")
                
        except Exception as e:
            print(f"   ❌ Error accessing salesdata3: {e}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return True

if __name__ == "__main__":
    print("SAP HANA - Accessible Sales Data Analysis")
    print("=" * 70)
    check_accessible_sales_data()
