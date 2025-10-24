#!/usr/bin/env python3
"""
SAP HANA Database Connection with SYSTEM user
Database: 98.83.112.225:30215 (Instance 02)
User: system
Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def connect_and_list_tables():
    """Connect to SAP HANA using SYSTEM credentials and list all available tables"""
    
    # Updated connection parameters
    host = "98.83.112.225"
    port = 30215  # Instance 02 -> 3<02>15
    username = "system"
    password = "Dilkyakare1234"
    
    connection = None
    
    try:
        print("🔌 Connecting to SAP HANA...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {username}")
        print(f"   Password: {'*' * len(password)}")
        
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
        
        # Get current user and schema info
        cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
        user_info = cursor.fetchone()
        print(f"   Current User: {user_info[0]}")
        print(f"   Current Schema: {user_info[1]}")
        
        print("\n📋 Listing all available tables...")
        
        # Query to get all tables accessible to SYSTEM user
        table_query = """
        SELECT 
            SCHEMA_NAME,
            TABLE_NAME,
            TABLE_TYPE,
            RECORD_COUNT,
            MEMORY_SIZE_IN_TOTAL
        FROM SYS.M_TABLES 
        WHERE SCHEMA_NAME NOT IN ('SYS', '_SYS_STATISTICS', '_SYS_REPO', '_SYS_BI', '_SYS_AFL', '_SYS_EPM')
        AND TABLE_TYPE = 'ROW'
        ORDER BY SCHEMA_NAME, TABLE_NAME
        """
        
        cursor.execute(table_query)
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📊 Found {len(tables)} tables:")
            print("-" * 100)
            print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<10} {'RECORDS':<12} {'SIZE_MB':<10}")
            print("-" * 100)
            
            for schema, table_name, table_type, record_count, memory_size in tables:
                size_mb = round(memory_size / (1024 * 1024), 2) if memory_size else 0
                records = record_count if record_count else 0
                print(f"{schema:<20} {table_name:<40} {table_type:<10} {records:<12} {size_mb:<10}")
        else:
            print("❌ No tables found, trying alternative query...")
            
            # Try alternative query for basic table listing
            cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA NOT LIKE 'SYS%' 
            AND TABLE_SCHEMA NOT LIKE '_SYS%'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            
            alt_tables = cursor.fetchall()
            if alt_tables:
                print(f"\n📊 Found {len(alt_tables)} tables (alternative query):")
                print("-" * 80)
                print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<15}")
                print("-" * 80)
                
                for schema, table_name, table_type in alt_tables:
                    print(f"{schema:<20} {table_name:<40} {table_type:<15}")
            else:
                print("❌ No tables accessible with current user privileges")
        
        # Get schema information
        print(f"\n🏗️  Available Schemas:")
        cursor.execute("""
        SELECT SCHEMA_NAME, COUNT(*) as TABLE_COUNT
        FROM SYS.M_TABLES 
        WHERE SCHEMA_NAME NOT IN ('SYS', '_SYS_STATISTICS', '_SYS_REPO', '_SYS_BI', '_SYS_AFL', '_SYS_EPM')
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
            'MAKT',  # Material Descriptions
            'MSEG',  # Material Document Segment
            'BSEG',  # Accounting Document Segment
            'LIPS',  # Delivery Item
            'VBRP',  # Billing Document Item
            'MARC',  # Material Master (Plant/Storage View)
            'KNVV',  # Customer Master (Sales View)
            'EKPO'   # Purchase Document Item
        ]
        
        found_sap_tables = []
        
        for table in common_sap_tables:
            # Check in different schemas
            for schema in ['SAPABAP1', 'SAP', 'SYSTEM', user_info[1]]:
                try:
                    cursor.execute(f"""
                    SELECT COUNT(*) FROM SYS.M_TABLES 
                    WHERE SCHEMA_NAME = '{schema}' AND TABLE_NAME = '{table}'
                    """)
                    exists = cursor.fetchone()[0] > 0
                    if exists:
                        # Get record count
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                            count = cursor.fetchone()[0]
                            found_sap_tables.append(f"{schema}.{table} ({count:,} records)")
                        except:
                            found_sap_tables.append(f"{schema}.{table} (access restricted)")
                        break
                except:
                    continue
        
        if found_sap_tables:
            print("✅ Found SAP tables:")
            for table_info in found_sap_tables:
                print(f"   {table_info}")
        else:
            print("❌ No common SAP tables found")
        
        # Get database information
        print(f"\n🗄️  Database Information:")
        try:
            cursor.execute("SELECT DATABASE_NAME, SQL_PORT FROM SYS.M_DATABASES")
            db_info = cursor.fetchall()
            if db_info:
                print("Available databases:")
                for db_name, sql_port in db_info:
                    print(f"   - {db_name}: Port {sql_port}")
        except Exception as e:
            print(f"Could not retrieve database info: {e}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Enhanced troubleshooting for SYSTEM user
        print(f"\n🔧 Troubleshooting suggestions for SYSTEM user:")
        print(f"   1. Verify HANA instance is running")
        print(f"   2. Check network connectivity: nc -zv {host} {port}")
        print(f"   3. Confirm SYSTEM user password: 'Dilkyakare1234'")
        print(f"   4. Check if SYSTEM user is locked or password expired")
        print(f"   5. Verify SAP HANA is accepting connections")
        
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return True

if __name__ == "__main__":
    print("SAP HANA Database Connection - SYSTEM User")
    print("=" * 60)
    connect_and_list_tables()
