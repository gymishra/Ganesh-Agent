#!/usr/bin/env python3
"""
Get VBAK table information using system tables accessible to SYSTEM user
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def get_vbak_info():
    """Get VBAK table information from system tables"""
    
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
        
        print("\n📊 Getting VBAK table information from system tables...")
        
        # Query 1: Get table information from M_TABLES
        try:
            cursor.execute("""
            SELECT 
                SCHEMA_NAME,
                TABLE_NAME,
                TABLE_TYPE,
                RECORD_COUNT,
                MEMORY_SIZE_IN_TOTAL,
                DISK_SIZE,
                LAST_COMPRESSED_RECORD_COUNT
            FROM SYS.M_TABLES 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            """)
            
            table_info = cursor.fetchone()
            if table_info:
                schema, table_name, table_type, record_count, memory_size, disk_size, compressed_count = table_info
                
                print(f"✅ VBAK Table Information:")
                print("-" * 60)
                print(f"Schema:           {schema}")
                print(f"Table Name:       {table_name}")
                print(f"Table Type:       {table_type}")
                print(f"Record Count:     {record_count:,}" if record_count else "Record Count:     N/A")
                print(f"Memory Size:      {memory_size:,} bytes" if memory_size else "Memory Size:      N/A")
                print(f"Disk Size:        {disk_size:,} bytes" if disk_size else "Disk Size:        N/A")
                print(f"Compressed Count: {compressed_count:,}" if compressed_count else "Compressed Count: N/A")
                
                # Convert memory size to MB if available
                if memory_size:
                    memory_mb = memory_size / (1024 * 1024)
                    print(f"Memory Size (MB): {memory_mb:.2f} MB")
                
                # Convert disk size to MB if available
                if disk_size:
                    disk_mb = disk_size / (1024 * 1024)
                    print(f"Disk Size (MB):   {disk_mb:.2f} MB")
                    
            else:
                print("❌ VBAK table not found in M_TABLES")
                
        except Exception as e:
            print(f"❌ Error getting table info from M_TABLES: {e}")
        
        # Query 2: Try alternative system table
        try:
            print(f"\n🔍 Checking alternative system tables...")
            cursor.execute("""
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            """)
            
            alt_info = cursor.fetchone()
            if alt_info:
                print(f"✅ Found in INFORMATION_SCHEMA.TABLES:")
                print(f"   Schema: {alt_info[0]}")
                print(f"   Table:  {alt_info[1]}")
                print(f"   Type:   {alt_info[2]}")
            else:
                print("❌ VBAK not found in INFORMATION_SCHEMA.TABLES")
                
        except Exception as e:
            print(f"❌ Error checking INFORMATION_SCHEMA: {e}")
        
        # Query 3: Get column information
        try:
            print(f"\n📋 VBAK Column Information:")
            cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE_NAME,
                LENGTH,
                SCALE,
                IS_NULLABLE,
                DEFAULT_VALUE,
                POSITION
            FROM TABLE_COLUMNS 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            ORDER BY POSITION
            """)
            
            columns = cursor.fetchall()
            if columns:
                print(f"✅ Found {len(columns)} columns in VBAK:")
                print("-" * 90)
                print(f"{'POS':<4} {'COLUMN_NAME':<20} {'DATA_TYPE':<15} {'LENGTH':<8} {'NULLABLE':<8}")
                print("-" * 90)
                
                for col_name, data_type, length, scale, nullable, default_val, position in columns[:20]:  # Show first 20 columns
                    length_str = str(length) if length else 'N/A'
                    nullable_str = 'YES' if nullable == 'TRUE' else 'NO'
                    print(f"{position:<4} {col_name:<20} {data_type:<15} {length_str:<8} {nullable_str:<8}")
                
                if len(columns) > 20:
                    print(f"... and {len(columns) - 20} more columns")
                    
            else:
                print("❌ No column information found")
                
        except Exception as e:
            print(f"❌ Error getting column info: {e}")
        
        # Query 4: Check table statistics
        try:
            print(f"\n📈 Checking table statistics...")
            cursor.execute("""
            SELECT 
                SCHEMA_NAME,
                TABLE_NAME,
                PART_ID,
                RECORD_COUNT,
                RAW_RECORD_COUNT_IN_MAIN,
                RAW_RECORD_COUNT_IN_DELTA,
                MEMORY_SIZE_IN_MAIN,
                MEMORY_SIZE_IN_DELTA
            FROM SYS.M_CS_TABLES 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            """)
            
            stats = cursor.fetchall()
            if stats:
                print(f"✅ Column Store Statistics:")
                total_records = 0
                total_main_records = 0
                total_delta_records = 0
                
                for stat in stats:
                    schema, table, part_id, records, main_records, delta_records, main_mem, delta_mem = stat
                    if records:
                        total_records += records
                    if main_records:
                        total_main_records += main_records
                    if delta_records:
                        total_delta_records += delta_records
                
                print("-" * 60)
                print(f"Total Records:        {total_records:,}")
                print(f"Main Store Records:   {total_main_records:,}")
                print(f"Delta Store Records:  {total_delta_records:,}")
                print(f"Number of Partitions: {len(stats)}")
                
            else:
                print("❌ No column store statistics found")
                
        except Exception as e:
            print(f"❌ Error getting column store stats: {e}")
        
        # Query 5: Try to get record count estimate
        try:
            print(f"\n🔢 Attempting to get record count estimate...")
            cursor.execute("""
            SELECT 
                SCHEMA_NAME,
                TABLE_NAME,
                ESTIMATED_MAX_MEMORY_SIZE_IN_TOTAL,
                LAST_COMPRESSED_RECORD_COUNT,
                RECORD_COUNT
            FROM SYS.M_TABLES 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            """)
            
            estimate = cursor.fetchone()
            if estimate:
                schema, table, est_memory, compressed_count, record_count = estimate
                print(f"✅ Record Count Estimates:")
                print("-" * 40)
                if record_count:
                    print(f"Current Record Count: {record_count:,}")
                if compressed_count:
                    print(f"Compressed Count:     {compressed_count:,}")
                if est_memory:
                    print(f"Estimated Memory:     {est_memory:,} bytes")
                    
        except Exception as e:
            print(f"❌ Error getting estimates: {e}")
        
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
    print("SAP HANA VBAK Table System Information")
    print("=" * 70)
    get_vbak_info()
