#!/usr/bin/env python3

"""
SAP HANA Integration for Q CLI - Fixed Version
Working solution using direct HANA database access with correct schemas
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
    
    def get_available_schemas(self):
        """Get list of available schemas"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT SCHEMA_NAME, COUNT(*) as TABLE_COUNT
                FROM SYS.TABLES 
                GROUP BY SCHEMA_NAME
                ORDER BY TABLE_COUNT DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            schemas = []
            for row in results:
                schemas.append({
                    'name': row[0],
                    'table_count': row[1]
                })
            
            return schemas
            
        except Exception as e:
            print(f"❌ Error getting schemas: {e}")
            return []
    
    def find_sap_tables(self, pattern=None):
        """Find SAP-related tables"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            if pattern:
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
            else:
                # Look for common SAP tables
                query = """
                    SELECT 
                        SCHEMA_NAME,
                        TABLE_NAME,
                        RECORD_COUNT,
                        TABLE_TYPE
                    FROM SYS.M_TABLES 
                    WHERE TABLE_NAME IN ('VBAK', 'VBAP', 'KNA1', 'MARA', 'T001')
                       OR TABLE_NAME LIKE 'VB%'
                       OR TABLE_NAME LIKE 'T0%'
                    ORDER BY RECORD_COUNT DESC
                    LIMIT 100
                """
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            tables = []
            for row in results:
                tables.append({
                    'schema': row[0],
                    'name': row[1],
                    'records': row[2] if row[2] else 0,
                    'type': row[3]
                })
            
            return tables
            
        except Exception as e:
            print(f"❌ Error finding SAP tables: {e}")
            return []
    
    def get_table_structure(self, schema, table_name):
        """Get table structure"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            query = """
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE_NAME,
                    LENGTH,
                    IS_NULLABLE
                FROM SYS.TABLE_COLUMNS 
                WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
                ORDER BY POSITION
            """
            cursor.execute(query, (schema, table_name))
            results = cursor.fetchall()
            cursor.close()
            
            columns = []
            for row in results:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'length': row[2],
                    'nullable': row[3] == 'TRUE'
                })
            
            return columns
            
        except Exception as e:
            print(f"❌ Error getting table structure: {e}")
            return []
    
    def query_vbak_data(self):
        """Query VBAK sales order data using correct schema"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor()
            
            # First, find the correct schema for VBAK
            schema_query = """
                SELECT SCHEMA_NAME 
                FROM SYS.M_TABLES 
                WHERE TABLE_NAME = 'VBAK'
                LIMIT 1
            """
            cursor.execute(schema_query)
            schema_result = cursor.fetchone()
            
            if not schema_result:
                print("❌ VBAK table not found")
                return {}
            
            schema_name = schema_result[0]
            print(f"📊 Found VBAK in schema: {schema_name}")
            
            # Query VBAK data
            query = f"""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT KUNNR) as unique_customers,
                    MIN(ERDAT) as earliest_date,
                    MAX(ERDAT) as latest_date
                FROM {schema_name}.VBAK
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'schema': schema_name,
                    'total_orders': result[0],
                    'unique_customers': result[1],
                    'earliest_date': result[2],
                    'latest_date': result[3]
                }
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error querying VBAK: {e}")
            return {}
    
    def sample_table_data(self, schema, table_name, limit=5):
        """Get sample data from a table"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            query = f"SELECT * FROM {schema}.{table_name} LIMIT {limit}"
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            
            data = []
            for row in results:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = str(value) if value is not None else None
                data.append(row_dict)
            
            return data
            
        except Exception as e:
            print(f"❌ Error sampling table data: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ HANA connection closed")

def main():
    """Main function for Q CLI integration"""
    print("🔧 SAP HANA Integration for Q CLI (Fixed)")
    print("=" * 45)
    
    # Initialize integration
    sap = SAPHanaIntegration()
    
    if not sap.connect():
        sys.exit(1)
    
    try:
        # Command line argument handling
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "schemas":
                print("🗂️  Available Schemas:")
                schemas = sap.get_available_schemas()
                
                for schema in schemas[:20]:  # Show first 20
                    print(f"  • {schema['name']} ({schema['table_count']} tables)")
                
                # Save to JSON
                with open('/tmp/sap_schemas.json', 'w') as f:
                    json.dump(schemas, f, indent=2)
                print(f"\n💾 Results saved to /tmp/sap_schemas.json")
            
            elif command == "tables":
                pattern = sys.argv[2] if len(sys.argv) > 2 else None
                print(f"🔍 Searching for tables: {pattern or 'SAP tables'}")
                tables = sap.find_sap_tables(pattern)
                
                print(f"\n📋 Found {len(tables)} tables:")
                for table in tables[:25]:  # Show first 25
                    print(f"  • {table['schema']}.{table['name']} ({table['records']:,} records)")
                
                # Save to JSON
                with open('/tmp/sap_tables.json', 'w') as f:
                    json.dump(tables, f, indent=2)
                print(f"\n💾 Results saved to /tmp/sap_tables.json")
            
            elif command == "structure":
                if len(sys.argv) < 4:
                    print("❌ Usage: python3 sap_hana_integration_fixed.py structure SCHEMA TABLE")
                    sys.exit(1)
                
                schema = sys.argv[2]
                table_name = sys.argv[3]
                print(f"🏗️  Table structure for {schema}.{table_name}:")
                
                columns = sap.get_table_structure(schema, table_name)
                
                if columns:
                    print(f"\n📋 {len(columns)} columns:")
                    for col in columns:
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        print(f"  • {col['name']} {col['type']}({col['length']}) {nullable}")
                else:
                    print("❌ Table not found or no access")
            
            elif command == "sample":
                if len(sys.argv) < 4:
                    print("❌ Usage: python3 sap_hana_integration_fixed.py sample SCHEMA TABLE [LIMIT]")
                    sys.exit(1)
                
                schema = sys.argv[2]
                table_name = sys.argv[3]
                limit = int(sys.argv[4]) if len(sys.argv) > 4 else 5
                
                print(f"📄 Sample data from {schema}.{table_name} (limit {limit}):")
                
                data = sap.sample_table_data(schema, table_name, limit)
                
                if data:
                    # Show first few columns of first row as example
                    first_row = data[0]
                    columns = list(first_row.keys())[:10]  # First 10 columns
                    
                    print(f"\n📊 Columns: {', '.join(columns)}")
                    for i, row in enumerate(data):
                        row_data = [str(row.get(col, ''))[:20] for col in columns]
                        print(f"  Row {i+1}: {' | '.join(row_data)}")
                    
                    # Save full data
                    with open(f'/tmp/{schema}_{table_name}_sample.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"\n💾 Full sample saved to /tmp/{schema}_{table_name}_sample.json")
                else:
                    print("❌ No data found or no access")
            
            elif command == "vbak":
                print("📊 VBAK Sales Order Analysis")
                analysis = sap.query_vbak_data()
                
                if analysis:
                    print(f"  • Schema: {analysis['schema']}")
                    print(f"  • Total Orders: {analysis['total_orders']:,}")
                    print(f"  • Unique Customers: {analysis['unique_customers']:,}")
                    print(f"  • Date Range: {analysis['earliest_date']} to {analysis['latest_date']}")
                    
                    # Get sample data
                    sample = sap.sample_table_data(analysis['schema'], 'VBAK', 3)
                    if sample:
                        print(f"\n📄 Sample VBAK records:")
                        for i, record in enumerate(sample):
                            print(f"  Order {i+1}: {record.get('VBELN', 'N/A')} - Customer: {record.get('KUNNR', 'N/A')}")
                else:
                    print("❌ No VBAK data available")
            
            else:
                print("❌ Unknown command. Available: schemas, tables, structure, sample, vbak")
        
        else:
            # Default: show overview
            print("🏠 SAP System Overview")
            print("-" * 30)
            
            # Show schemas
            schemas = sap.get_available_schemas()
            print(f"🗂️  Schemas: {len(schemas)} found")
            for schema in schemas[:5]:
                print(f"  • {schema['name']} ({schema['table_count']} tables)")
            
            # Show SAP tables
            tables = sap.find_sap_tables()
            print(f"\n📋 SAP Tables: {len(tables)} found")
            for table in tables[:5]:
                print(f"  • {table['schema']}.{table['name']} ({table['records']:,} records)")
            
            # Show VBAK analysis
            analysis = sap.query_vbak_data()
            if analysis:
                print(f"\n📊 VBAK Analysis: {analysis['total_orders']:,} orders in {analysis['schema']}")
            
            print("\n💡 Usage:")
            print("  python3 sap_hana_integration_fixed.py schemas")
            print("  python3 sap_hana_integration_fixed.py tables [pattern]")
            print("  python3 sap_hana_integration_fixed.py structure SCHEMA TABLE")
            print("  python3 sap_hana_integration_fixed.py sample SCHEMA TABLE [LIMIT]")
            print("  python3 sap_hana_integration_fixed.py vbak")
    
    finally:
        sap.close()

if __name__ == "__main__":
    main()
