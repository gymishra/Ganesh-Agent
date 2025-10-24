#!/usr/bin/env python3
"""
SAP HANA Table Listing - Fixed Version
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def connect_and_list_tables():
    """Connect to SAP HANA and list all available tables with corrected queries"""
    
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
        
        # Get current timestamp and user info
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        current_time = cursor.fetchone()[0]
        print(f"   Server Time: {current_time}")
        
        cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
        user_info = cursor.fetchone()
        print(f"   Current User: {user_info[0]}")
        print(f"   Current Schema: {user_info[1]}")
        
        print("\n📋 Listing all available tables...")
        
        # Try multiple table queries with different column names
        table_queries = [
            # Query 1: Basic table information
            """
            SELECT 
                SCHEMA_NAME,
                TABLE_NAME,
                TABLE_TYPE,
                RECORD_COUNT
            FROM SYS.M_TABLES 
            WHERE SCHEMA_NAME NOT IN ('SYS', '_SYS_STATISTICS', '_SYS_REPO', '_SYS_BI', '_SYS_AFL', '_SYS_EPM')
            ORDER BY SCHEMA_NAME, TABLE_NAME
            """,
            
            # Query 2: Information schema approach
            """
            SELECT 
                TABLE_SCHEMA as SCHEMA_NAME,
                TABLE_NAME,
                TABLE_TYPE,
                NULL as RECORD_COUNT
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA NOT LIKE 'SYS%' 
            AND TABLE_SCHEMA NOT LIKE '_SYS%'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """,
            
            # Query 3: Simple table listing
            """
            SELECT 
                SCHEMA_NAME,
                TABLE_NAME,
                'TABLE' as TABLE_TYPE,
                NULL as RECORD_COUNT
            FROM TABLES
            WHERE SCHEMA_NAME NOT LIKE 'SYS%' 
            AND SCHEMA_NAME NOT LIKE '_SYS%'
            ORDER BY SCHEMA_NAME, TABLE_NAME
            """
        ]
        
        tables_found = False
        
        for i, query in enumerate(table_queries, 1):
            try:
                print(f"\n🔍 Trying table query {i}...")
                cursor.execute(query)
                tables = cursor.fetchall()
                
                if tables:
                    tables_found = True
                    print(f"✅ Found {len(tables)} tables:")
                    print("-" * 90)
                    print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<10} {'RECORDS':<15}")
                    print("-" * 90)
                    
                    for row in tables:
                        schema = row[0] if row[0] else 'N/A'
                        table_name = row[1] if row[1] else 'N/A'
                        table_type = row[2] if row[2] else 'N/A'
                        records = row[3] if len(row) > 3 and row[3] is not None else 'N/A'
                        
                        print(f"{schema:<20} {table_name:<40} {table_type:<10} {records:<15}")
                    
                    break  # Success, no need to try other queries
                    
            except Exception as e:
                print(f"❌ Query {i} failed: {e}")
                continue
        
        if not tables_found:
            print("❌ No tables found with any query method")
        
        # Get schema information
        print(f"\n🏗️  Available Schemas:")
        try:
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
            else:
                print("No schemas found")
                
        except Exception as e:
            print(f"Could not retrieve schema info: {e}")
        
        # Check for common SAP tables in different schemas
        print(f"\n🔍 Searching for common SAP tables...")
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
        
        # First, get all available schemas
        try:
            cursor.execute("""
            SELECT DISTINCT SCHEMA_NAME 
            FROM SYS.M_TABLES 
            WHERE SCHEMA_NAME NOT LIKE 'SYS%' 
            AND SCHEMA_NAME NOT LIKE '_SYS%'
            ORDER BY SCHEMA_NAME
            """)
            available_schemas = [row[0] for row in cursor.fetchall()]
            print(f"Available schemas to search: {', '.join(available_schemas)}")
        except:
            available_schemas = ['SAPABAP1', 'SAP', 'SYSTEM']
        
        found_sap_tables = []
        
        for table in common_sap_tables:
            for schema in available_schemas:
                try:
                    cursor.execute(f"""
                    SELECT COUNT(*) FROM SYS.M_TABLES 
                    WHERE SCHEMA_NAME = '{schema}' AND TABLE_NAME = '{table}'
                    """)
                    exists = cursor.fetchone()[0] > 0
                    if exists:
                        # Try to get record count
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                            count = cursor.fetchone()[0]
                            found_sap_tables.append(f"{schema}.{table} ({count:,} records)")
                        except Exception as e:
                            found_sap_tables.append(f"{schema}.{table} (exists, count failed: {str(e)[:30]}...)")
                        break
                except Exception as e:
                    continue
        
        if found_sap_tables:
            print("\n✅ Found SAP tables:")
            for table_info in found_sap_tables:
                print(f"   {table_info}")
        else:
            print("\n❌ No common SAP tables found in available schemas")
        
        # Get database and version information
        print(f"\n🗄️  Database Information:")
        try:
            # Database version
            cursor.execute("SELECT VERSION FROM SYS.M_DATABASE")
            version = cursor.fetchone()[0]
            print(f"   SAP HANA Version: {version}")
        except:
            print("   Could not retrieve version info")
        
        try:
            # Database name and ports
            cursor.execute("SELECT DATABASE_NAME, SQL_PORT FROM SYS.M_DATABASES")
            db_info = cursor.fetchall()
            if db_info:
                print("   Available databases:")
                for db_name, sql_port in db_info:
                    print(f"     - {db_name}: Port {sql_port}")
        except Exception as e:
            print(f"   Could not retrieve database info: {e}")
        
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
    print("SAP HANA Table Listing - Fixed Version")
    print("=" * 60)
    connect_and_list_tables()
