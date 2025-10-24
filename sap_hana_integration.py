#!/usr/bin/env python3

"""
SAP HANA Integration for Q CLI
Working solution using direct HANA database access
"""

import hdbcli.dbapi
import json
import sys
from datetime import datetime

class SAPHanaIntegration:
    def __init__(self):
        self.connection = None
        self.host = "98.83.112.225"
        self.port = 30215
        self.user = "SYSTEM"
        self.password = "Dilkyakare1234"
    
    def connect(self):
        """Establish HANA database connection"""
        try:
            self.connection = hdbcli.dbapi.connect(
                address=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            print("✅ Connected to SAP HANA database")
            return True
        except Exception as e:
            print(f"❌ HANA connection failed: {e}")
            return False
    
    def find_abap_programs(self, search_pattern=None):
        """Find ABAP programs using HANA database queries"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Query ABAP programs from repository
            if search_pattern:
                query = """
                    SELECT TOP 50
                        PROGNAME,
                        SUBC,
                        CDAT,
                        CNAM,
                        UDAT,
                        UNAM
                    FROM SAPSR3.REPOSRC 
                    WHERE UPPER(PROGNAME) LIKE UPPER(?)
                    ORDER BY UDAT DESC
                """
                cursor.execute(query, (f"%{search_pattern}%",))
            else:
                query = """
                    SELECT TOP 100
                        PROGNAME,
                        SUBC,
                        CDAT,
                        CNAM,
                        UDAT,
                        UNAM
                    FROM SAPSR3.REPOSRC 
                    WHERE PROGNAME LIKE 'SAPM%' 
                       OR PROGNAME LIKE 'RSUSR%'
                       OR PROGNAME LIKE 'RSPO%'
                    ORDER BY UDAT DESC
                """
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            programs = []
            for row in results:
                programs.append({
                    'name': row[0],
                    'type': row[1],
                    'created_date': row[2],
                    'created_by': row[3],
                    'updated_date': row[4],
                    'updated_by': row[5]
                })
            
            return programs
            
        except Exception as e:
            print(f"❌ Error finding ABAP programs: {e}")
            return []
    
    def get_program_source(self, program_name):
        """Get ABAP program source code"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            
            # Get program source from REPOSRC table
            query = """
                SELECT DATA
                FROM SAPSR3.REPOSRC 
                WHERE PROGNAME = ?
            """
            cursor.execute(query, (program_name,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting program source: {e}")
            return None
    
    def get_sales_order_analysis(self):
        """Get sales order analysis from VBAK table"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor()
            
            # Sales order summary
            query = """
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT KUNNR) as unique_customers,
                    AVG(CAST(NETWR AS DECIMAL(15,2))) as avg_net_value,
                    MAX(CAST(NETWR AS DECIMAL(15,2))) as max_net_value,
                    MIN(ERDAT) as earliest_date,
                    MAX(ERDAT) as latest_date
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL AND NETWR != ''
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'total_orders': result[0],
                    'unique_customers': result[1],
                    'avg_net_value': float(result[2]) if result[2] else 0,
                    'max_net_value': float(result[3]) if result[3] else 0,
                    'earliest_date': result[4],
                    'latest_date': result[5]
                }
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error getting sales analysis: {e}")
            return {}
    
    def search_tables(self, pattern):
        """Search for database tables"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Search in HANA system tables
            query = """
                SELECT 
                    SCHEMA_NAME,
                    TABLE_NAME,
                    RECORD_COUNT,
                    TABLE_TYPE
                FROM SYS.M_TABLES 
                WHERE UPPER(TABLE_NAME) LIKE UPPER(?)
                ORDER BY RECORD_COUNT DESC
                LIMIT 50
            """
            cursor.execute(query, (f"%{pattern}%",))
            results = cursor.fetchall()
            cursor.close()
            
            tables = []
            for row in results:
                tables.append({
                    'schema': row[0],
                    'name': row[1],
                    'records': row[2],
                    'type': row[3]
                })
            
            return tables
            
        except Exception as e:
            print(f"❌ Error searching tables: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ HANA connection closed")

def main():
    """Main function for Q CLI integration"""
    print("🔧 SAP HANA Integration for Q CLI")
    print("=" * 40)
    
    # Initialize integration
    sap = SAPHanaIntegration()
    
    if not sap.connect():
        sys.exit(1)
    
    try:
        # Command line argument handling
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "programs":
                pattern = sys.argv[2] if len(sys.argv) > 2 else None
                print(f"🔍 Searching for ABAP programs: {pattern or 'common programs'}")
                programs = sap.find_abap_programs(pattern)
                
                print(f"\n📋 Found {len(programs)} programs:")
                for prog in programs[:20]:  # Show first 20
                    print(f"  • {prog['name']} ({prog['type']}) - Updated: {prog['updated_date']} by {prog['updated_by']}")
                
                # Save to JSON for Q CLI integration
                with open('/tmp/sap_programs.json', 'w') as f:
                    json.dump(programs, f, indent=2, default=str)
                print(f"\n💾 Results saved to /tmp/sap_programs.json")
            
            elif command == "source":
                if len(sys.argv) < 3:
                    print("❌ Usage: python3 sap_hana_integration.py source PROGRAM_NAME")
                    sys.exit(1)
                
                program_name = sys.argv[2].upper()
                print(f"📄 Getting source for program: {program_name}")
                source = sap.get_program_source(program_name)
                
                if source:
                    print(f"\n📝 Source code for {program_name}:")
                    print("-" * 50)
                    print(source[:2000])  # Show first 2000 characters
                    if len(source) > 2000:
                        print(f"\n... (truncated, total length: {len(source)} characters)")
                    
                    # Save full source
                    with open(f'/tmp/{program_name}_source.txt', 'w') as f:
                        f.write(source)
                    print(f"\n💾 Full source saved to /tmp/{program_name}_source.txt")
                else:
                    print(f"❌ Program {program_name} not found")
            
            elif command == "sales":
                print("📊 Sales Order Analysis")
                analysis = sap.get_sales_order_analysis()
                
                if analysis:
                    print(f"  • Total Orders: {analysis['total_orders']:,}")
                    print(f"  • Unique Customers: {analysis['unique_customers']:,}")
                    print(f"  • Average Net Value: ${analysis['avg_net_value']:,.2f}")
                    print(f"  • Maximum Net Value: ${analysis['max_net_value']:,.2f}")
                    print(f"  • Date Range: {analysis['earliest_date']} to {analysis['latest_date']}")
                else:
                    print("❌ No sales data available")
            
            elif command == "tables":
                pattern = sys.argv[2] if len(sys.argv) > 2 else "VBAK"
                print(f"🔍 Searching for tables: {pattern}")
                tables = sap.search_tables(pattern)
                
                print(f"\n📋 Found {len(tables)} tables:")
                for table in tables[:15]:  # Show first 15
                    print(f"  • {table['schema']}.{table['name']} ({table['records']:,} records)")
            
            else:
                print("❌ Unknown command. Available: programs, source, sales, tables")
        
        else:
            # Default: show overview
            print("🏠 SAP System Overview")
            print("-" * 30)
            
            # Show some programs
            programs = sap.find_abap_programs()
            print(f"📋 ABAP Programs: {len(programs)} found")
            
            # Show sales analysis
            analysis = sap.get_sales_order_analysis()
            if analysis:
                print(f"📊 Sales Orders: {analysis['total_orders']:,} total")
            
            # Show available tables
            tables = sap.search_tables("VB")
            print(f"🗃️  VB* Tables: {len(tables)} found")
            
            print("\n💡 Usage:")
            print("  python3 sap_hana_integration.py programs [pattern]")
            print("  python3 sap_hana_integration.py source PROGRAM_NAME")
            print("  python3 sap_hana_integration.py sales")
            print("  python3 sap_hana_integration.py tables [pattern]")
    
    finally:
        sap.close()

if __name__ == "__main__":
    main()
