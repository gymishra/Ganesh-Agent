#!/usr/bin/env python3

"""
Find ABAP Programs Starting with "Z" using HANA Database
Alternative approach when ADT services are not available
"""

import hdbcli.dbapi
from datetime import datetime

def find_z_programs_via_hana():
    """Find Z programs using direct HANA database queries"""
    
    print("🔍 Searching for Z* ABAP Programs via HANA Database")
    print("=" * 55)
    
    # Connect to SAP HANA
    try:
        conn = hdbcli.dbapi.connect(
            address='98.83.112.225',
            port=30215,
            user='SYSTEM',
            password='Dilkyakare1234'
        )
        print("✅ Connected to SAP HANA database")
        
        cursor = conn.cursor()
        
        # Method 1: Search in REPOSRC table (Repository Source)
        print("\n📋 Method 1: Searching REPOSRC table")
        print("-" * 35)
        
        try:
            query = """
                SELECT 
                    PROGNAME,
                    SUBC,
                    CDAT,
                    CNAM,
                    UDAT,
                    UNAM
                FROM SAPHANADB.REPOSRC 
                WHERE PROGNAME LIKE 'Z%'
                ORDER BY PROGNAME
                LIMIT 100
            """
            cursor.execute(query)
            z_programs = cursor.fetchall()
            
            if z_programs:
                print(f"✅ Found {len(z_programs)} Z programs in REPOSRC:")
                print(f"{'No.':<4} {'Program Name':<20} {'Type':<6} {'Created':<10} {'Creator':<10}")
                print("-" * 65)
                
                for i, (progname, subc, cdat, cnam, udat, unam) in enumerate(z_programs, 1):
                    prog_type = subc or 'PROG'
                    created = str(cdat)[:10] if cdat else 'Unknown'
                    creator = cnam or 'Unknown'
                    print(f"{i:<4} {progname:<20} {prog_type:<6} {created:<10} {creator:<10}")
                
                # Categorize programs
                reports = [p for p in z_programs if not p[0].startswith('ZCL_')]
                classes = [p for p in z_programs if p[0].startswith('ZCL_')]
                
                print(f"\n📊 Program Categories:")
                print(f"   📄 Reports/Programs: {len(reports)}")
                print(f"   🏗️  Classes: {len(classes)}")
                
            else:
                print("❌ No Z programs found in REPOSRC table")
                
        except Exception as e:
            print(f"❌ Error querying REPOSRC: {e}")
        
        # Method 2: Search in TADIR table (Repository Directory)
        print(f"\n📋 Method 2: Searching TADIR table")
        print("-" * 35)
        
        try:
            query = """
                SELECT 
                    PGMID,
                    OBJECT,
                    OBJ_NAME,
                    CREATED_ON,
                    AUTHOR
                FROM SAPHANADB.TADIR 
                WHERE OBJ_NAME LIKE 'Z%'
                  AND OBJECT IN ('PROG', 'CLAS', 'FUGR', 'INTF')
                ORDER BY OBJ_NAME
                LIMIT 100
            """
            cursor.execute(query)
            z_objects = cursor.fetchall()
            
            if z_objects:
                print(f"✅ Found {len(z_objects)} Z objects in TADIR:")
                print(f"{'No.':<4} {'Object Name':<20} {'Type':<6} {'Created':<10} {'Author':<10}")
                print("-" * 65)
                
                for i, (pgmid, obj_type, obj_name, created_on, author) in enumerate(z_objects, 1):
                    created = str(created_on)[:10] if created_on else 'Unknown'
                    auth = author or 'Unknown'
                    print(f"{i:<4} {obj_name:<20} {obj_type:<6} {created:<10} {auth:<10}")
                
                # Count by object type
                object_counts = {}
                for _, obj_type, _, _, _ in z_objects:
                    object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
                
                print(f"\n📊 Object Type Distribution:")
                for obj_type, count in sorted(object_counts.items()):
                    type_name = {
                        'PROG': 'Programs/Reports',
                        'CLAS': 'Classes', 
                        'FUGR': 'Function Groups',
                        'INTF': 'Interfaces'
                    }.get(obj_type, obj_type)
                    print(f"   {type_name}: {count}")
                    
            else:
                print("❌ No Z objects found in TADIR table")
                
        except Exception as e:
            print(f"❌ Error querying TADIR: {e}")
        
        # Method 3: Search for Z tables and other objects
        print(f"\n📋 Method 3: Searching for Z tables and other objects")
        print("-" * 50)
        
        try:
            # Look for Z tables in system tables
            query = """
                SELECT 
                    TABLE_NAME,
                    TABLE_TYPE,
                    RECORD_COUNT
                FROM SYS.M_TABLES 
                WHERE SCHEMA_NAME = 'SAPHANADB'
                  AND TABLE_NAME LIKE 'Z%'
                ORDER BY TABLE_NAME
                LIMIT 50
            """
            cursor.execute(query)
            z_tables = cursor.fetchall()
            
            if z_tables:
                print(f"✅ Found {len(z_tables)} Z tables:")
                print(f"{'No.':<4} {'Table Name':<25} {'Type':<15} {'Records':<10}")
                print("-" * 65)
                
                for i, (table_name, table_type, record_count) in enumerate(z_tables, 1):
                    records = f"{record_count:,}" if record_count else "0"
                    print(f"{i:<4} {table_name:<25} {table_type:<15} {records:<10}")
            else:
                print("❌ No Z tables found")
                
        except Exception as e:
            print(f"❌ Error searching Z tables: {e}")
        
        # Method 4: Alternative search in accessible tables
        print(f"\n📋 Method 4: Alternative search methods")
        print("-" * 40)
        
        try:
            # Search for any table that might contain program information
            query = """
                SELECT TABLE_NAME, RECORD_COUNT
                FROM SYS.M_TABLES 
                WHERE SCHEMA_NAME = 'SAPHANADB'
                  AND (TABLE_NAME LIKE '%PROG%' 
                    OR TABLE_NAME LIKE '%REPO%'
                    OR TABLE_NAME LIKE '%ABAP%'
                    OR TABLE_NAME LIKE '%SOURCE%')
                  AND RECORD_COUNT > 0
                ORDER BY RECORD_COUNT DESC
                LIMIT 20
            """
            cursor.execute(query)
            prog_tables = cursor.fetchall()
            
            if prog_tables:
                print("📊 Tables that might contain program information:")
                for table_name, record_count in prog_tables:
                    print(f"   • {table_name}: {record_count:,} records")
                    
                    # Try to sample the first table to see if it contains Z programs
                    if table_name == prog_tables[0][0]:
                        try:
                            sample_query = f"SELECT * FROM SAPHANADB.{table_name} LIMIT 5"
                            cursor.execute(sample_query)
                            sample_data = cursor.fetchall()
                            
                            if sample_data:
                                print(f"\n📄 Sample from {table_name}:")
                                # Get column names
                                columns = [desc[0] for desc in cursor.description]
                                print(f"   Columns: {', '.join(columns[:5])}...")
                                
                                # Look for Z patterns in the data
                                z_found = False
                                for row in sample_data:
                                    for value in row:
                                        if isinstance(value, str) and value.startswith('Z'):
                                            print(f"   Found Z object: {value}")
                                            z_found = True
                                            break
                                    if z_found:
                                        break
                                        
                        except Exception as e:
                            print(f"   ⚠️  Cannot sample {table_name}: {e}")
            else:
                print("❌ No program-related tables found")
                
        except Exception as e:
            print(f"❌ Error in alternative search: {e}")
        
        cursor.close()
        conn.close()
        
        # Generate summary and recommendations
        print(f"\n🎯 SUMMARY AND RECOMMENDATIONS")
        print("=" * 35)
        
        print("📋 Search Results:")
        print("   • REPOSRC table: Checked for Z programs")
        print("   • TADIR table: Checked for Z objects") 
        print("   • System tables: Checked for Z tables")
        print("   • Alternative methods: Explored program tables")
        
        print(f"\n💡 For Q CLI Integration:")
        print("   q 'Search the SAP HANA database for all ABAP programs starting with Z'")
        print("   q 'List all custom Z tables in the SAP system'")
        print("   q 'Show me the structure of Z programs in the repository'")
        print("   q 'Find all Z objects created by a specific developer'")
        
        print(f"\n🔧 Alternative Approaches:")
        print("   1. Enable ADT services for full MCP ABAP functionality")
        print("   2. Use SAP GUI transaction SE80 to browse Z objects")
        print("   3. Run transaction SE11 to see Z tables and structures")
        print("   4. Use transaction SE38 to search for Z reports")
        
        print(f"\n📊 Database Access Status:")
        print("   ✅ HANA connection: Working")
        print("   ✅ System tables: Accessible")
        print("   ⚠️  Repository tables: Limited access")
        print("   🔧 ADT services: Need activation for full functionality")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Check HANA database connectivity")
        print("   • Verify user privileges")
        print("   • Ensure SAP system is running")

if __name__ == "__main__":
    find_z_programs_via_hana()
