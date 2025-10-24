#!/usr/bin/env python3
"""
Enhanced SAP HANA Database Connection Script
Tries multiple connection approaches for SAP HANA
Database: 98.83.112.225:30215 (Instance 02)
User: gyabmis
"""

import hdbcli.dbapi as hana_db
import sys

def test_connection_variants():
    """Test different connection parameter combinations"""
    
    host = "98.83.112.225"
    username = "gyabmis"
    password = "Pass2025$"
    
    # Different port and connection combinations to try
    connection_attempts = [
        # Standard instance 02 ports
        {"port": 30215, "database": None, "description": "Instance 02 - Default port"},
        {"port": 30213, "database": None, "description": "Instance 02 - SQL port"},
        {"port": 30241, "database": None, "description": "Instance 02 - XS port"},
        
        # Try with specific database names
        {"port": 30215, "database": "SYSTEMDB", "description": "Instance 02 - SYSTEMDB"},
        {"port": 30215, "database": "HDB", "description": "Instance 02 - HDB database"},
        {"port": 30215, "database": "PRD", "description": "Instance 02 - PRD database"},
        
        # Try tenant database ports (if multi-tenant)
        {"port": 30241, "database": "SYSTEMDB", "description": "Tenant - SYSTEMDB"},
        {"port": 30244, "database": None, "description": "Tenant database port"},
    ]
    
    print("SAP HANA Enhanced Connection Test")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"User: {username}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    successful_connections = []
    
    for i, attempt in enumerate(connection_attempts, 1):
        port = attempt["port"]
        database = attempt["database"]
        description = attempt["description"]
        
        print(f"🔄 Attempt {i}: {description}")
        print(f"   Port: {port}")
        print(f"   Database: {database or 'Default'}")
        
        try:
            # Build connection parameters
            conn_params = {
                "address": host,
                "port": port,
                "user": username,
                "password": password
            }
            
            if database:
                conn_params["database"] = database
            
            # Attempt connection
            connection = hana_db.connect(**conn_params)
            
            # Test the connection with a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
            server_time = cursor.fetchone()[0]
            
            print(f"   ✅ SUCCESS!")
            print(f"   Server Time: {server_time}")
            
            # Try to get basic system info
            try:
                cursor.execute("SELECT DATABASE_NAME, SQL_PORT FROM SYS.M_DATABASES")
                db_info = cursor.fetchall()
                if db_info:
                    print(f"   Database Info:")
                    for db_name, sql_port in db_info:
                        print(f"     - {db_name}: Port {sql_port}")
            except Exception as e:
                print(f"   Note: Could not retrieve database info: {e}")
            
            successful_connections.append({
                "port": port,
                "database": database,
                "description": description,
                "connection": connection
            })
            
            cursor.close()
            connection.close()
            print()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            print()
            continue
    
    return successful_connections

def list_tables_with_connection(host, port, username, password, database=None):
    """List tables using successful connection parameters"""
    
    try:
        print(f"🔌 Connecting to list tables...")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {database or 'Default'}")
        
        # Build connection parameters
        conn_params = {
            "address": host,
            "port": port,
            "user": username,
            "password": password
        }
        
        if database:
            conn_params["database"] = database
        
        connection = hana_db.connect(**conn_params)
        cursor = connection.cursor()
        
        print("✅ Connected successfully!")
        
        # Get current user and database info
        cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
        user_info = cursor.fetchone()
        print(f"   Current User: {user_info[0]}")
        print(f"   Current Schema: {user_info[1]}")
        
        print(f"\n📋 Listing accessible tables...")
        
        # Try comprehensive table query
        table_queries = [
            # Query 1: All tables with detailed info
            """
            SELECT 
                SCHEMA_NAME,
                TABLE_NAME,
                TABLE_TYPE,
                RECORD_COUNT,
                MEMORY_SIZE_IN_TOTAL
            FROM SYS.M_TABLES 
            WHERE SCHEMA_NAME NOT IN ('SYS', '_SYS_STATISTICS', '_SYS_REPO', '_SYS_BI')
            ORDER BY SCHEMA_NAME, TABLE_NAME
            """,
            
            # Query 2: Basic table listing
            """
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA NOT LIKE 'SYS%' 
            AND TABLE_SCHEMA NOT LIKE '_SYS%'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """,
            
            # Query 3: User tables only
            """
            SELECT SCHEMA_NAME, TABLE_NAME, TABLE_TYPE
            FROM TABLES
            WHERE SCHEMA_NAME = CURRENT_SCHEMA
            ORDER BY TABLE_NAME
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
                    print("-" * 100)
                    
                    if len(tables[0]) == 5:  # Detailed query
                        print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<10} {'RECORDS':<12} {'SIZE_MB':<10}")
                        print("-" * 100)
                        for schema, table_name, table_type, record_count, memory_size in tables:
                            size_mb = round(memory_size / (1024 * 1024), 2) if memory_size else 0
                            records = record_count if record_count else 0
                            print(f"{schema:<20} {table_name:<40} {table_type:<10} {records:<12} {size_mb:<10}")
                    else:  # Basic query
                        print(f"{'SCHEMA':<20} {'TABLE_NAME':<40} {'TYPE':<15}")
                        print("-" * 80)
                        for row in tables:
                            schema, table_name, table_type = row[:3]
                            print(f"{schema:<20} {table_name:<40} {table_type:<15}")
                    
                    break  # Success, no need to try other queries
                    
            except Exception as e:
                print(f"❌ Query {i} failed: {e}")
                continue
        
        if not tables_found:
            print("❌ No tables found with any query method")
            
            # Try to check user privileges
            try:
                print(f"\n🔍 Checking user privileges...")
                cursor.execute("""
                SELECT PRIVILEGE, OBJECT_TYPE, OBJECT_NAME 
                FROM EFFECTIVE_PRIVILEGES 
                WHERE GRANTEE = CURRENT_USER
                AND PRIVILEGE IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE')
                ORDER BY OBJECT_NAME
                """)
                privileges = cursor.fetchall()
                
                if privileges:
                    print(f"User privileges found:")
                    for privilege, obj_type, obj_name in privileges[:10]:  # Show first 10
                        print(f"   {privilege} on {obj_type}: {obj_name}")
                    if len(privileges) > 10:
                        print(f"   ... and {len(privileges) - 10} more")
                else:
                    print("No specific privileges found")
                    
            except Exception as e:
                print(f"Could not check privileges: {e}")
        
        # Check for common SAP tables
        print(f"\n🔍 Checking for common SAP tables...")
        common_sap_tables = [
            'VBAK', 'VBAP', 'KNA1', 'MARA', 'BKPF', 'EKKO', 'T001', 'MAKT',
            'MSEG', 'BSEG', 'LIPS', 'VBRP', 'MARC', 'KNVV', 'EKPO'
        ]
        
        found_sap_tables = []
        for table in common_sap_tables:
            try:
                # Try different schema combinations
                for schema in [user_info[1], 'SAPABAP1', 'SAP', username.upper()]:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                        count = cursor.fetchone()[0]
                        found_sap_tables.append(f"{schema}.{table} ({count} records)")
                        break
                    except:
                        continue
            except:
                continue
        
        if found_sap_tables:
            print("✅ Found SAP tables:")
            for table_info in found_sap_tables:
                print(f"   {table_info}")
        else:
            print("❌ No common SAP tables found")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list tables: {e}")
        return False

def main():
    """Main function to test connections and list tables"""
    
    # First, test different connection variants
    successful_connections = test_connection_variants()
    
    if successful_connections:
        print(f"\n🎉 Found {len(successful_connections)} successful connection(s)!")
        
        # Use the first successful connection to list tables
        best_connection = successful_connections[0]
        print(f"\n📊 Using connection: {best_connection['description']}")
        
        list_tables_with_connection(
            host="98.83.112.225",
            port=best_connection["port"],
            username="gyabmis",
            password="Pass2025$",
            database=best_connection["database"]
        )
        
    else:
        print("\n❌ No successful connections found")
        print("\n🔧 Additional troubleshooting steps:")
        print("   1. Verify the username 'gyabmis' exists in SAP HANA")
        print("   2. Check if the password 'Pass2025$' is correct")
        print("   3. Confirm the user has database access permissions")
        print("   4. Check if the SAP HANA instance is running")
        print("   5. Verify the instance number (02) is correct")

if __name__ == "__main__":
    main()
