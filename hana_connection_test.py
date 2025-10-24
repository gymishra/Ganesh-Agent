#!/usr/bin/env python3
"""
SAP HANA Database Connection and Table Listing
Database: 98.83.112.225:30215 (Instance 02)
User: gyabmis
"""

import hdbcli.dbapi as hana_db
import sys

def connect_and_list_tables():
    """Connect to SAP HANA and list all available tables"""
    
    # Connection parameters
    host = "98.83.112.225"
    port = 30215  # Instance 02 -> 3<02>15
    username = "gyabmis"
    password = "Pass2025$"
    
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
        
        # Create cursor
        cursor = connection.cursor()
        
        # Get current timestamp to verify connection
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        current_time = cursor.fetchone()[0]
        print(f"   Server Time: {current_time}")
        
        print("\n📋 Listing all available tables...")
        
        # Query to get all tables accessible to the user
        table_query = """
        SELECT 
            SCHEMA_NAME,
            TABLE_NAME,
            TABLE_TYPE,
            RECORD_COUNT,
            MEMORY_SIZE_IN_TOTAL
        FROM SYS.M_TABLES 
        WHERE SCHEMA_NAME NOT IN ('SYS', '_SYS_STATISTICS', '_SYS_REPO', '_SYS_BI')
        ORDER BY SCHEMA_NAME, TABLE_NAME
        """
        
        cursor.execute(table_query)
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found or insufficient privileges")
            
            # Try alternative query for basic table listing
            print("\n🔍 Trying alternative table query...")
            cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA NOT LIKE 'SYS%' 
            AND TABLE_SCHEMA NOT LIKE '_SYS%'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            
            alt_tables = cursor.fetchall()
            if alt_tables:
                print(f"\n📊 Found {len(alt_tables)} tables:")
                print("-" * 80)
                print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<15}")
                print("-" * 80)
                
                for schema, table_name, table_type in alt_tables:
                    print(f"{schema:<20} {table_name:<40} {table_type:<15}")
            else:
                print("❌ No tables accessible with current user privileges")
        else:
            print(f"\n📊 Found {len(tables)} tables:")
            print("-" * 100)
            print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<10} {'RECORDS':<12} {'SIZE_MB':<10}")
            print("-" * 100)
            
            for schema, table_name, table_type, record_count, memory_size in tables:
                size_mb = round(memory_size / (1024 * 1024), 2) if memory_size else 0
                records = record_count if record_count else 0
                print(f"{schema:<20} {table_name:<40} {table_type:<10} {records:<12} {size_mb:<10}")
        
        # Get schema information
        print(f"\n🏗️  Available Schemas:")
        cursor.execute("""
        SELECT SCHEMA_NAME, COUNT(*) as TABLE_COUNT
        FROM SYS.M_TABLES 
        WHERE SCHEMA_NAME NOT IN ('SYS', '_SYS_STATISTICS', '_SYS_REPO', '_SYS_BI')
        GROUP BY SCHEMA_NAME
        ORDER BY TABLE_COUNT DESC, SCHEMA_NAME
        """)
        
        schemas = cursor.fetchall()
        if schemas:
            print("-" * 40)
            print(f"{'SCHEMA':<25} {'TABLE_COUNT':<15}")
            print("-" * 40)
            for schema_name, table_count in schemas:
                print(f"{schema_name:<25} {table_count:<15}")
        
        # Check for common SAP tables
        print(f"\n🔍 Checking for common SAP tables...")
        common_sap_tables = [
            'VBAK',  # Sales Document Header
            'VBAP',  # Sales Document Item  
            'KNA1',  # Customer Master
            'MARA',  # Material Master
            'BKPF',  # Accounting Document Header
            'EKKO',  # Purchase Document Header
            'T001',  # Company Codes
            'MAKT'   # Material Descriptions
        ]
        
        for table in common_sap_tables:
            cursor.execute(f"""
            SELECT COUNT(*) FROM SYS.M_TABLES 
            WHERE TABLE_NAME = '{table}'
            """)
            exists = cursor.fetchone()[0] > 0
            status = "✅ Found" if exists else "❌ Not found"
            print(f"   {table:<10} {status}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Common troubleshooting suggestions
        print(f"\n🔧 Troubleshooting suggestions:")
        print(f"   1. Verify HANA instance is running")
        print(f"   2. Check network connectivity: telnet {host} {port}")
        print(f"   3. Confirm user credentials and permissions")
        print(f"   4. Ensure HANA client is installed: pip install hdbcli")
        
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return True

if __name__ == "__main__":
    print("SAP HANA Database Connection Test")
    print("=" * 50)
    connect_and_list_tables()
