#!/usr/bin/env python3

"""
Q CLI SAP Integration - Complete Working Solution
Integrates SAP HANA database with Q CLI for GenAI curriculum enhancement
"""

import hdbcli.dbapi
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

class QCLISAPIntegration:
    """Complete SAP integration for Q CLI with HANA database access"""
    
    def __init__(self):
        self.connection = None
        self.host = "98.83.112.225"
        self.port = 30215
        self.user = "SYSTEM"
        self.password = "Dilkyakare1234"
        self.schema = "SAPHANADB"
    
    def connect(self) -> bool:
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
            print(f"❌ HANA connection failed: {e}")
            return False
    
    def get_sap_business_data_overview(self) -> Dict[str, Any]:
        """Get comprehensive SAP business data overview"""
        if not self.connection:
            return {}
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'connection_info': {
                'host': self.host,
                'port': self.port,
                'schema': self.schema
            },
            'business_areas': {}
        }
        
        # Sales & Distribution data
        try:
            cursor = self.connection.cursor()
            
            # Sales Orders (VBAK)
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.VBAK")
            vbak_count = cursor.fetchone()[0]
            
            # Sales Order Items (VBAP)
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.VBAP")
            vbap_count = cursor.fetchone()[0]
            
            # Billing Documents (VBRK)
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.VBRK")
            vbrk_count = cursor.fetchone()[0]
            
            # Document Flow (VBFA)
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.VBFA")
            vbfa_count = cursor.fetchone()[0]
            
            overview['business_areas']['sales_distribution'] = {
                'sales_orders': vbak_count,
                'order_items': vbap_count,
                'billing_documents': vbrk_count,
                'document_flow_records': vbfa_count
            }
            
            cursor.close()
            
        except Exception as e:
            overview['business_areas']['sales_distribution'] = {'error': str(e)}
        
        return overview
    
    def get_sales_analytics(self) -> Dict[str, Any]:
        """Get detailed sales analytics for GenAI scenarios"""
        if not self.connection:
            return {}
        
        analytics = {
            'summary': {},
            'top_customers': [],
            'order_trends': [],
            'sample_orders': []
        }
        
        try:
            cursor = self.connection.cursor()
            
            # Basic sales summary
            query = f"""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT KUNNR) as unique_customers,
                    MIN(ERDAT) as earliest_order,
                    MAX(ERDAT) as latest_order
                FROM {self.schema}.VBAK
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                analytics['summary'] = {
                    'total_orders': result[0],
                    'unique_customers': result[1],
                    'date_range': f"{result[2]} to {result[3]}"
                }
            
            # Top customers by order count
            query = f"""
                SELECT 
                    KUNNR as customer_id,
                    COUNT(*) as order_count
                FROM {self.schema}.VBAK
                WHERE KUNNR IS NOT NULL AND KUNNR != ''
                GROUP BY KUNNR
                ORDER BY order_count DESC
                LIMIT 10
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            for row in results:
                analytics['top_customers'].append({
                    'customer_id': row[0],
                    'order_count': row[1]
                })
            
            # Sample orders for GenAI examples
            query = f"""
                SELECT 
                    VBELN as order_number,
                    KUNNR as customer_id,
                    ERDAT as order_date,
                    VKORG as sales_org,
                    VTWEG as distribution_channel
                FROM {self.schema}.VBAK
                LIMIT 20
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            for row in results:
                analytics['sample_orders'].append({
                    'order_number': row[0],
                    'customer_id': row[1],
                    'order_date': str(row[2]),
                    'sales_org': row[3],
                    'distribution_channel': row[4]
                })
            
            cursor.close()
            
        except Exception as e:
            analytics['error'] = str(e)
        
        return analytics
    
    def get_table_catalog(self) -> List[Dict[str, Any]]:
        """Get catalog of available SAP tables for GenAI curriculum"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Get SAP business tables with descriptions
            query = f"""
                SELECT 
                    TABLE_NAME,
                    RECORD_COUNT,
                    TABLE_TYPE
                FROM SYS.M_TABLES 
                WHERE SCHEMA_NAME = '{self.schema}'
                  AND (TABLE_NAME LIKE 'VB%'    -- Sales & Distribution
                    OR TABLE_NAME LIKE 'KN%'    -- Customer Master
                    OR TABLE_NAME LIKE 'MAR%'   -- Material Master
                    OR TABLE_NAME LIKE 'T0%'    -- Configuration Tables
                    OR TABLE_NAME LIKE 'MARA'   -- Material Master
                    OR TABLE_NAME LIKE 'KNA1')  -- Customer Master
                ORDER BY RECORD_COUNT DESC
                LIMIT 100
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            catalog = []
            for row in results:
                # Add business context for common tables
                business_area = self._get_business_area(row[0])
                description = self._get_table_description(row[0])
                
                catalog.append({
                    'table_name': row[0],
                    'record_count': row[1] if row[1] else 0,
                    'table_type': row[2],
                    'business_area': business_area,
                    'description': description,
                    'genai_use_cases': self._get_genai_use_cases(row[0])
                })
            
            return catalog
            
        except Exception as e:
            print(f"❌ Error getting table catalog: {e}")
            return []
    
    def _get_business_area(self, table_name: str) -> str:
        """Map table name to business area"""
        if table_name.startswith('VB'):
            return 'Sales & Distribution'
        elif table_name.startswith('KN'):
            return 'Customer Management'
        elif table_name.startswith('MAR') or table_name == 'MARA':
            return 'Material Management'
        elif table_name.startswith('T0'):
            return 'Configuration'
        else:
            return 'General'
    
    def _get_table_description(self, table_name: str) -> str:
        """Get business description for common SAP tables"""
        descriptions = {
            'VBAK': 'Sales Document Header',
            'VBAP': 'Sales Document Item',
            'VBRK': 'Billing Document Header',
            'VBRP': 'Billing Document Item',
            'VBFA': 'Sales Document Flow',
            'VBPA': 'Sales Document Partner',
            'KNA1': 'Customer Master General Data',
            'MARA': 'Material Master General Data',
            'T001': 'Company Codes'
        }
        return descriptions.get(table_name, 'SAP Business Table')
    
    def _get_genai_use_cases(self, table_name: str) -> List[str]:
        """Get GenAI use cases for each table"""
        use_cases = {
            'VBAK': [
                'Sales order analysis and forecasting',
                'Customer behavior pattern recognition',
                'Order processing automation',
                'Sales performance analytics'
            ],
            'VBAP': [
                'Product demand analysis',
                'Cross-selling recommendations',
                'Inventory optimization',
                'Pricing strategy analysis'
            ],
            'VBRK': [
                'Revenue recognition automation',
                'Billing anomaly detection',
                'Payment prediction models',
                'Financial reporting automation'
            ],
            'VBFA': [
                'Process flow optimization',
                'Document lifecycle analysis',
                'Workflow automation',
                'Business process mining'
            ]
        }
        return use_cases.get(table_name, ['Data analysis and reporting'])
    
    def generate_genai_curriculum_examples(self) -> Dict[str, Any]:
        """Generate examples for SAP GenAI curriculum"""
        if not self.connection:
            return {}
        
        curriculum = {
            'overview': {
                'title': 'SAP GenAI Integration Curriculum',
                'description': 'Real SAP HANA data integration with AWS Bedrock models',
                'data_source': f'{self.host}:{self.port}/{self.schema}',
                'generated_at': datetime.now().isoformat()
            },
            'modules': []
        }
        
        # Module 1: Sales Data Analysis
        sales_data = self.get_sales_analytics()
        if sales_data and 'summary' in sales_data:
            curriculum['modules'].append({
                'module_id': 'M001',
                'title': 'Sales Order Analysis with GenAI',
                'description': 'Analyze real SAP sales data using AWS Bedrock models',
                'data_points': sales_data['summary'],
                'sample_data': sales_data['sample_orders'][:5],
                'genai_prompts': [
                    f"Analyze the sales pattern from {sales_data['summary'].get('total_orders', 0)} orders",
                    f"Identify trends among {sales_data['summary'].get('unique_customers', 0)} customers",
                    "Generate insights for sales optimization"
                ],
                'aws_bedrock_models': [
                    'anthropic.claude-3-sonnet-20240229-v1:0',
                    'amazon.titan-text-express-v1',
                    'ai21.j2-ultra-v1'
                ]
            })
        
        # Module 2: Table Exploration
        table_catalog = self.get_table_catalog()
        if table_catalog:
            curriculum['modules'].append({
                'module_id': 'M002',
                'title': 'SAP Table Structure Analysis',
                'description': 'Explore SAP business tables using GenAI',
                'available_tables': len(table_catalog),
                'top_tables': [
                    {
                        'name': table['table_name'],
                        'records': table['record_count'],
                        'business_area': table['business_area']
                    }
                    for table in table_catalog[:10]
                ],
                'genai_use_cases': [
                    'Automated table documentation',
                    'Data relationship discovery',
                    'Business process mapping'
                ]
            })
        
        return curriculum
    
    def export_for_q_cli(self, output_dir: str = '/tmp') -> Dict[str, str]:
        """Export all data for Q CLI integration"""
        if not self.connection:
            return {}
        
        exports = {}
        
        try:
            # Export business overview
            overview = self.get_sap_business_data_overview()
            overview_file = os.path.join(output_dir, 'sap_business_overview.json')
            with open(overview_file, 'w') as f:
                json.dump(overview, f, indent=2)
            exports['business_overview'] = overview_file
            
            # Export sales analytics
            sales = self.get_sales_analytics()
            sales_file = os.path.join(output_dir, 'sap_sales_analytics.json')
            with open(sales_file, 'w') as f:
                json.dump(sales, f, indent=2)
            exports['sales_analytics'] = sales_file
            
            # Export table catalog
            catalog = self.get_table_catalog()
            catalog_file = os.path.join(output_dir, 'sap_table_catalog.json')
            with open(catalog_file, 'w') as f:
                json.dump(catalog, f, indent=2)
            exports['table_catalog'] = catalog_file
            
            # Export GenAI curriculum
            curriculum = self.generate_genai_curriculum_examples()
            curriculum_file = os.path.join(output_dir, 'sap_genai_curriculum.json')
            with open(curriculum_file, 'w') as f:
                json.dump(curriculum, f, indent=2)
            exports['genai_curriculum'] = curriculum_file
            
            # Create Q CLI configuration
            q_config = {
                'sap_integration': {
                    'host': self.host,
                    'port': self.port,
                    'schema': self.schema,
                    'available_data': list(exports.keys()),
                    'mcp_server_path': '/home/gyanmis/mcp-abap-abap-adt-api/dist/index.js',
                    'hana_integration': '/home/gyanmis/q_cli_sap_integration.py'
                }
            }
            
            config_file = os.path.join(output_dir, 'q_cli_sap_config.json')
            with open(config_file, 'w') as f:
                json.dump(q_config, f, indent=2)
            exports['q_cli_config'] = config_file
            
        except Exception as e:
            exports['error'] = str(e)
        
        return exports
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

def main():
    """Main function for Q CLI SAP integration"""
    print("🚀 Q CLI SAP Integration - Complete Solution")
    print("=" * 50)
    
    # Initialize integration
    sap = QCLISAPIntegration()
    
    if not sap.connect():
        print("❌ Failed to connect to SAP HANA")
        sys.exit(1)
    
    print("✅ Connected to SAP HANA database")
    
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "overview":
                print("\n📊 SAP Business Data Overview")
                overview = sap.get_sap_business_data_overview()
                
                if 'business_areas' in overview:
                    for area, data in overview['business_areas'].items():
                        print(f"\n🏢 {area.replace('_', ' ').title()}:")
                        if isinstance(data, dict) and 'error' not in data:
                            for key, value in data.items():
                                print(f"  • {key.replace('_', ' ').title()}: {value:,}")
                        elif 'error' in data:
                            print(f"  ⚠️  {data['error']}")
            
            elif command == "sales":
                print("\n📈 Sales Analytics")
                analytics = sap.get_sales_analytics()
                
                if 'summary' in analytics:
                    print("📋 Summary:")
                    for key, value in analytics['summary'].items():
                        print(f"  • {key.replace('_', ' ').title()}: {value}")
                
                if 'top_customers' in analytics and analytics['top_customers']:
                    print(f"\n🏆 Top Customers:")
                    for customer in analytics['top_customers'][:5]:
                        print(f"  • Customer {customer['customer_id']}: {customer['order_count']} orders")
            
            elif command == "catalog":
                print("\n📚 SAP Table Catalog")
                catalog = sap.get_table_catalog()
                
                print(f"Found {len(catalog)} business tables:")
                for table in catalog[:15]:
                    print(f"  • {table['table_name']} ({table['record_count']:,} records) - {table['business_area']}")
                    print(f"    {table['description']}")
            
            elif command == "curriculum":
                print("\n🎓 GenAI Curriculum Generation")
                curriculum = sap.generate_genai_curriculum_examples()
                
                print(f"📖 {curriculum['overview']['title']}")
                print(f"📝 {curriculum['overview']['description']}")
                print(f"🔗 Data Source: {curriculum['overview']['data_source']}")
                
                if 'modules' in curriculum:
                    print(f"\n📚 Available Modules: {len(curriculum['modules'])}")
                    for module in curriculum['modules']:
                        print(f"  • {module['module_id']}: {module['title']}")
                        print(f"    {module['description']}")
            
            elif command == "export":
                print("\n💾 Exporting Data for Q CLI")
                exports = sap.export_for_q_cli()
                
                print("📁 Generated Files:")
                for key, filepath in exports.items():
                    if key != 'error':
                        print(f"  • {key.replace('_', ' ').title()}: {filepath}")
                
                if 'error' not in exports:
                    print("\n✅ All data exported successfully!")
                    print("🚀 Ready for Q CLI integration!")
                else:
                    print(f"\n❌ Export error: {exports['error']}")
            
            else:
                print("❌ Unknown command. Available: overview, sales, catalog, curriculum, export")
        
        else:
            # Default: comprehensive overview
            print("\n🏠 SAP System Integration Status")
            print("-" * 40)
            
            # Business overview
            overview = sap.get_sap_business_data_overview()
            if 'business_areas' in overview and 'sales_distribution' in overview['business_areas']:
                sd_data = overview['business_areas']['sales_distribution']
                if 'error' not in sd_data:
                    print(f"📊 Sales Orders: {sd_data.get('sales_orders', 0):,}")
                    print(f"📋 Order Items: {sd_data.get('order_items', 0):,}")
                    print(f"💰 Billing Documents: {sd_data.get('billing_documents', 0):,}")
            
            # Table catalog
            catalog = sap.get_table_catalog()
            print(f"📚 Business Tables: {len(catalog)} available")
            
            # Export status
            exports = sap.export_for_q_cli()
            print(f"💾 Export Files: {len([k for k in exports.keys() if k != 'error'])} generated")
            
            print("\n💡 Commands:")
            print("  python3 q_cli_sap_integration.py overview")
            print("  python3 q_cli_sap_integration.py sales")
            print("  python3 q_cli_sap_integration.py catalog")
            print("  python3 q_cli_sap_integration.py curriculum")
            print("  python3 q_cli_sap_integration.py export")
            
            print("\n🎯 Next Steps:")
            print("  1. Run 'export' command to generate Q CLI integration files")
            print("  2. Configure Q CLI with generated config file")
            print("  3. Use exported data for GenAI curriculum development")
    
    finally:
        sap.close()

if __name__ == "__main__":
    main()
