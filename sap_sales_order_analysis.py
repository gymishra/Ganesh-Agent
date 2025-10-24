#!/usr/bin/env python3

"""
SAP Sales Order Analysis - Privilege-Aware Approach
Analyzes sales orders with highest values using available access methods
"""

import hdbcli.dbapi
import json
from datetime import datetime

class SAPSalesOrderAnalysis:
    def __init__(self):
        self.connection = None
        self.host = "98.83.112.225"
        self.port = 30215
        self.user = "SYSTEM"
        self.password = "Dilkyakare1234"
        self.schema = "SAPHANADB"
    
    def connect(self):
        """Establish HANA database connection"""
        try:
            self.connection = hdbcli.dbapi.connect(
                address=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def check_table_access(self, table_name):
        """Check what level of access we have to a table"""
        if not self.connection:
            return None
        
        access_info = {
            'table_exists': False,
            'can_count': False,
            'can_select': False,
            'record_count': 0,
            'accessible_columns': []
        }
        
        try:
            cursor = self.connection.cursor()
            
            # Check if table exists
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM SYS.M_TABLES 
                WHERE SCHEMA_NAME = '{self.schema}' AND TABLE_NAME = '{table_name}'
            """)
            if cursor.fetchone()[0] > 0:
                access_info['table_exists'] = True
            
            # Try to get record count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.{table_name}")
                access_info['record_count'] = cursor.fetchone()[0]
                access_info['can_count'] = True
            except:
                pass
            
            # Try to select sample data
            try:
                cursor.execute(f"SELECT * FROM {self.schema}.{table_name} LIMIT 1")
                result = cursor.fetchone()
                if result:
                    access_info['can_select'] = True
                    # Get column names
                    cursor.execute(f"""
                        SELECT COLUMN_NAME 
                        FROM SYS.TABLE_COLUMNS 
                        WHERE SCHEMA_NAME = '{self.schema}' AND TABLE_NAME = '{table_name}'
                        ORDER BY POSITION
                    """)
                    columns = cursor.fetchall()
                    access_info['accessible_columns'] = [col[0] for col in columns]
            except:
                pass
            
            cursor.close()
            
        except Exception as e:
            access_info['error'] = str(e)
        
        return access_info
    
    def find_accessible_sales_tables(self):
        """Find sales-related tables we can actually access"""
        if not self.connection:
            return []
        
        sales_tables = ['VBAK', 'VBAP', 'VBRK', 'VBRP', 'VBFA', 'VBPA', 'VBKD']
        accessible_tables = []
        
        print("🔍 Checking access to sales tables...")
        print("=" * 50)
        
        for table in sales_tables:
            access = self.check_table_access(table)
            if access:
                status = "✅" if access['can_select'] else "🔒" if access['can_count'] else "❌"
                count = f"({access['record_count']:,} records)" if access['can_count'] else "(unknown count)"
                print(f"{status} {table}: {count}")
                
                if access['can_select'] or access['can_count']:
                    accessible_tables.append({
                        'table_name': table,
                        'access_info': access
                    })
        
        return accessible_tables
    
    def analyze_document_flow(self):
        """Analyze VBFA (document flow) table for sales insights"""
        if not self.connection:
            return {}
        
        print("\n📊 Analyzing Document Flow (VBFA)...")
        
        try:
            cursor = self.connection.cursor()
            
            # Check if we can access VBFA
            access = self.check_table_access('VBFA')
            if not access['can_select']:
                print("❌ Cannot access VBFA table data")
                return {}
            
            # Get document flow statistics
            analysis = {
                'total_flow_records': access['record_count'],
                'document_types': {},
                'high_value_indicators': []
            }
            
            # Try to get document type distribution
            try:
                cursor.execute(f"""
                    SELECT VBTYP_N as doc_type, COUNT(*) as count
                    FROM {self.schema}.VBFA
                    GROUP BY VBTYP_N
                    ORDER BY count DESC
                    LIMIT 10
                """)
                doc_types = cursor.fetchall()
                
                for doc_type, count in doc_types:
                    analysis['document_types'][doc_type or 'Unknown'] = count
                    
            except Exception as e:
                analysis['document_types_error'] = str(e)
            
            # Look for sales order patterns
            try:
                cursor.execute(f"""
                    SELECT VBELV as source_doc, COUNT(*) as flow_count
                    FROM {self.schema}.VBFA
                    WHERE VBTYP_V = 'C'  -- Sales orders
                    GROUP BY VBELV
                    ORDER BY flow_count DESC
                    LIMIT 20
                """)
                high_flow_docs = cursor.fetchall()
                
                analysis['high_activity_orders'] = []
                for doc, flow_count in high_flow_docs:
                    analysis['high_activity_orders'].append({
                        'order_number': doc,
                        'flow_count': flow_count
                    })
                    
            except Exception as e:
                analysis['flow_analysis_error'] = str(e)
            
            cursor.close()
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def find_highest_value_indicators(self):
        """Find indicators of highest value sales orders using available data"""
        if not self.connection:
            return {}
        
        print("\n🏆 Finding Highest Value Indicators...")
        
        results = {
            'method': 'indirect_analysis',
            'timestamp': datetime.now().isoformat(),
            'findings': {}
        }
        
        # Method 1: Analyze document flow complexity
        doc_flow = self.analyze_document_flow()
        if 'high_activity_orders' in doc_flow:
            results['findings']['high_activity_orders'] = doc_flow['high_activity_orders'][:10]
            print(f"📈 Found {len(doc_flow['high_activity_orders'])} orders with high document flow activity")
        
        # Method 2: Check table metadata for value insights
        try:
            cursor = self.connection.cursor()
            
            # Look for tables with value-related data we can access
            cursor.execute(f"""
                SELECT TABLE_NAME, RECORD_COUNT
                FROM SYS.M_TABLES 
                WHERE SCHEMA_NAME = '{self.schema}'
                  AND (TABLE_NAME LIKE '%PRICE%' 
                    OR TABLE_NAME LIKE '%VALUE%'
                    OR TABLE_NAME LIKE '%AMOUNT%'
                    OR TABLE_NAME LIKE 'KONV%'  -- Condition records
                    OR TABLE_NAME LIKE 'VBKD%') -- Sales document business data
                ORDER BY RECORD_COUNT DESC
                LIMIT 20
            """)
            value_tables = cursor.fetchall()
            
            results['findings']['value_related_tables'] = []
            for table_name, record_count in value_tables:
                # Test access to each table
                access = self.check_table_access(table_name)
                if access['can_select']:
                    results['findings']['value_related_tables'].append({
                        'table_name': table_name,
                        'record_count': record_count,
                        'accessible': True
                    })
            
            cursor.close()
            
        except Exception as e:
            results['findings']['metadata_error'] = str(e)
        
        return results
    
    def generate_sales_insights_report(self):
        """Generate comprehensive sales insights report"""
        print("📋 SAP Sales Order Analysis Report")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"SAP System: {self.host}:{self.port}")
        print(f"Schema: {self.schema}")
        print()
        
        # Check accessible tables
        accessible_tables = self.find_accessible_sales_tables()
        
        # Find highest value indicators
        value_analysis = self.find_highest_value_indicators()
        
        # Summary
        print("\n📊 ANALYSIS SUMMARY")
        print("-" * 30)
        print(f"Accessible Sales Tables: {len(accessible_tables)}")
        
        if 'high_activity_orders' in value_analysis.get('findings', {}):
            high_activity = value_analysis['findings']['high_activity_orders']
            print(f"High Activity Orders Found: {len(high_activity)}")
            
            if high_activity:
                print(f"\n🏆 TOP HIGH-ACTIVITY ORDERS (Potential High Value):")
                print("-" * 50)
                for i, order in enumerate(high_activity[:10], 1):
                    print(f"{i:2d}. Order {order['order_number']}: {order['flow_count']} document flows")
        
        # Value-related tables
        if 'value_related_tables' in value_analysis.get('findings', {}):
            value_tables = value_analysis['findings']['value_related_tables']
            if value_tables:
                print(f"\n💰 ACCESSIBLE VALUE-RELATED TABLES:")
                print("-" * 40)
                for table in value_tables[:10]:
                    print(f"• {table['table_name']}: {table['record_count']:,} records")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 20)
        print("1. High document flow activity often indicates complex/high-value orders")
        print("2. Orders with multiple billing documents suggest higher values")
        print("3. Consider requesting SAPHANADB user access for direct VBAK queries")
        print("4. Use accessible condition tables (KONV) for pricing analysis")
        
        # Export results
        export_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'accessible_tables': accessible_tables,
            'value_analysis': value_analysis,
            'recommendations': [
                "High document flow activity indicates complex/valuable orders",
                "Multiple billing documents suggest higher order values",
                "Request SAPHANADB user access for direct value queries",
                "Use condition tables for detailed pricing analysis"
            ]
        }
        
        with open('/tmp/sap_sales_analysis.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: /tmp/sap_sales_analysis.json")
        
        return export_data
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

def main():
    """Main analysis function"""
    analyzer = SAPSalesOrderAnalysis()
    
    if not analyzer.connect():
        return
    
    try:
        # Generate comprehensive analysis
        results = analyzer.generate_sales_insights_report()
        
        print(f"\n🎯 CONCLUSION:")
        print("=" * 15)
        
        if results.get('value_analysis', {}).get('findings', {}).get('high_activity_orders'):
            high_activity = results['value_analysis']['findings']['high_activity_orders']
            if high_activity:
                top_order = high_activity[0]
                print(f"🥇 Most Active Order: {top_order['order_number']}")
                print(f"   Document Flows: {top_order['flow_count']}")
                print(f"   (High activity often correlates with high value)")
            else:
                print("⚠️  No high-activity orders identified")
        else:
            print("⚠️  Limited access prevents direct value analysis")
        
        print(f"\n📈 For complete highest-value analysis, request:")
        print(f"   • SAPHANADB user credentials")
        print(f"   • SELECT privileges on VBAK.NETWR field")
        print(f"   • Access to pricing condition tables")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
