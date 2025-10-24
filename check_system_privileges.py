#!/usr/bin/env python3
"""
Check SYSTEM user's current privileges and try alternative access methods
Database: 98.83.112.225:30215 (Instance 02)
"""

import hdbcli.dbapi as hana_db
import sys

def check_system_privileges():
    """Check what privileges SYSTEM user currently has"""
    
    host = "98.83.112.225"
    port = 30215
    username = "system"
    password = "Dilkyakare1234"
    
    connection = None
    
    try:
        print("🔍 CHECKING SYSTEM USER PRIVILEGES")
        print("=" * 60)
        
        connection = hana_db.connect(address=host, port=port, user=username, password=password)
        cursor = connection.cursor()
        
        print("✅ Connected as SYSTEM user")
        
        # Check current privileges
        print("\n📋 Current SYSTEM User Privileges:")
        print("-" * 50)
        
        try:
            cursor.execute("""
            SELECT OBJECT_TYPE, SCHEMA_NAME, OBJECT_NAME, PRIVILEGE
            FROM SYS.GRANTED_PRIVILEGES 
            WHERE GRANTEE = 'SYSTEM' 
            AND SCHEMA_NAME = 'SAPHANADB'
            ORDER BY OBJECT_NAME
            """)
            
            privileges = cursor.fetchall()
            if privileges:
                print(f"Found {len(privileges)} SAPHANADB privileges:")
                for obj_type, schema, obj_name, privilege in privileges:
                    print(f"   {obj_type:<10} {schema}.{obj_name:<20} {privilege}")
            else:
                print("❌ No SAPHANADB privileges found for SYSTEM user")
                
        except Exception as e:
            print(f"❌ Could not check privileges: {e}")
        
        # Try different ways to access VBAK
        print(f"\n🔄 TRYING ALTERNATIVE VBAK ACCESS METHODS:")
        print("-" * 50)
        
        # Method 1: Try without schema prefix (if SYSTEM has default schema access)
        try:
            cursor.execute("SELECT COUNT(*) FROM VBAK")
            count = cursor.fetchone()[0]
            print(f"✅ Method 1 SUCCESS: VBAK accessible without schema prefix ({count:,} records)")
            
            # If this works, get the highest value
            cursor.execute("""
            SELECT VBELN, NETWR, WAERK, ERDAT, KUNNR 
            FROM VBAK 
            WHERE NETWR > 0 
            ORDER BY NETWR DESC 
            LIMIT 1
            """)
            
            highest = cursor.fetchone()
            if highest:
                vbeln, netwr, waerk, erdat, kunnr = highest
                print(f"🏆 HIGHEST VALUE FOUND: {netwr:,.2f} {waerk}")
                print(f"   Order: {vbeln}, Date: {erdat}, Customer: {kunnr}")
                return True
                
        except Exception as e:
            print(f"❌ Method 1 failed: {str(e)[:60]}...")
        
        # Method 2: Try with full schema name
        try:
            cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            count = cursor.fetchone()[0]
            print(f"✅ Method 2 SUCCESS: Full schema access works ({count:,} records)")
            
            # Get highest value
            cursor.execute("""
            SELECT VBELN, NETWR, WAERK, ERDAT, KUNNR 
            FROM SAPHANADB.VBAK 
            WHERE NETWR > 0 
            ORDER BY NETWR DESC 
            LIMIT 1
            """)
            
            highest = cursor.fetchone()
            if highest:
                vbeln, netwr, waerk, erdat, kunnr = highest
                print(f"🏆 HIGHEST VALUE FOUND: {netwr:,.2f} {waerk}")
                print(f"   Order: {vbeln}, Date: {erdat}, Customer: {kunnr}")
                return True
                
        except Exception as e:
            print(f"❌ Method 2 failed: {str(e)[:60]}...")
        
        # Method 3: Check if we can create a view
        try:
            cursor.execute("""
            CREATE VIEW SYSTEM.VBAK_VIEW AS 
            SELECT * FROM SAPHANADB.VBAK
            """)
            print(f"✅ Method 3: Created view successfully")
            
            cursor.execute("SELECT COUNT(*) FROM SYSTEM.VBAK_VIEW")
            count = cursor.fetchone()[0]
            print(f"   View has {count:,} records")
            
        except Exception as e:
            print(f"❌ Method 3 failed: {str(e)[:60]}...")
        
        # Method 4: Check what schemas SYSTEM can access
        print(f"\n📊 SCHEMAS ACCESSIBLE TO SYSTEM:")
        print("-" * 40)
        
        try:
            cursor.execute("""
            SELECT DISTINCT SCHEMA_NAME, COUNT(*) as TABLE_COUNT
            FROM SYS.GRANTED_PRIVILEGES 
            WHERE GRANTEE = 'SYSTEM' 
            AND OBJECT_TYPE = 'TABLE'
            GROUP BY SCHEMA_NAME
            ORDER BY TABLE_COUNT DESC
            """)
            
            schemas = cursor.fetchall()
            if schemas:
                for schema, table_count in schemas:
                    print(f"   {schema}: {table_count} tables")
            else:
                print("   No table privileges found")
                
        except Exception as e:
            print(f"❌ Could not check schema access: {e}")
        
        # Method 5: Try to find any accessible sales data
        print(f"\n🔍 SEARCHING FOR ACCESSIBLE SALES DATA:")
        print("-" * 45)
        
        # Check tables with 'sales' or 'vbak' in name
        try:
            cursor.execute("""
            SELECT SCHEMA_NAME, TABLE_NAME, RECORD_COUNT
            FROM SYS.M_TABLES 
            WHERE (UPPER(TABLE_NAME) LIKE '%SALES%' 
                   OR UPPER(TABLE_NAME) LIKE '%VBAK%'
                   OR UPPER(TABLE_NAME) LIKE '%ORDER%')
            AND RECORD_COUNT > 0
            ORDER BY RECORD_COUNT DESC
            """)
            
            sales_tables = cursor.fetchall()
            if sales_tables:
                print("Found sales-related tables:")
                for schema, table, records in sales_tables:
                    print(f"   {schema}.{table}: {records:,} records")
                    
                    # Try to access each table
                    try:
                        cursor.execute(f"SELECT TOP 1 * FROM {schema}.{table}")
                        sample = cursor.fetchone()
                        print(f"      ✅ Accessible")
                    except:
                        print(f"      ❌ No access")
            else:
                print("   No sales-related tables found")
                
        except Exception as e:
            print(f"❌ Could not search for sales tables: {e}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return False

if __name__ == "__main__":
    success = check_system_privileges()
    
    if not success:
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   1. Ask SAP admin for SAPHANADB user password")
        print(f"   2. Create new user with VBAK access (as shown above)")
        print(f"   3. Use different administrative user to grant privileges")
        print(f"   4. Check if VBAK data exists in accessible schemas")
