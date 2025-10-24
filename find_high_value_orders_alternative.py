#!/usr/bin/env python3

"""
Alternative Approach to Find High-Value Sales Orders
Uses indirect methods when direct NETWR access is restricted
"""

import hdbcli.dbapi
from datetime import datetime

def find_high_value_indicators():
    """Find high-value sales order indicators using available data"""
    
    print("🔍 Alternative High-Value Sales Order Analysis")
    print("=" * 55)
    print("Since direct NETWR access is restricted, using indirect methods...")
    print()
    
    # Connect to SAP HANA
    conn = hdbcli.dbapi.connect(
        address='98.83.112.225',
        port=30215,
        user='SYSTEM',
        password='Dilkyakare1234'
    )
    
    cursor = conn.cursor()
    
    # Method 1: Find tables with accessible sales-related data
    print("📊 Method 1: Analyzing Accessible Sales Tables")
    print("-" * 45)
    
    try:
        # Look for sales-related tables we can actually query
        query = """
        SELECT 
            t.TABLE_NAME,
            t.RECORD_COUNT,
            t.TABLE_TYPE
        FROM SYS.M_TABLES t
        WHERE t.SCHEMA_NAME = 'SAPHANADB'
          AND (t.TABLE_NAME LIKE 'VB%'
            OR t.TABLE_NAME LIKE 'KONV%'  -- Condition records (pricing)
            OR t.TABLE_NAME LIKE 'VBKD%'  -- Sales document business data
            OR t.TABLE_NAME LIKE 'PRCD%'  -- Pricing procedure
            OR t.TABLE_NAME LIKE 'A%'     -- Condition tables
            OR t.TABLE_NAME LIKE 'KONH%'  -- Condition header
            OR t.TABLE_NAME LIKE 'KONP%') -- Condition item
          AND t.RECORD_COUNT > 0
        ORDER BY t.RECORD_COUNT DESC
        LIMIT 30
        """
        
        cursor.execute(query)
        tables = cursor.fetchall()
        
        accessible_tables = []
        
        for table_name, record_count, table_type in tables:
            # Test if we can actually query this table
            try:
                test_query = f"SELECT COUNT(*) FROM SAPHANADB.{table_name}"
                cursor.execute(test_query)
                actual_count = cursor.fetchone()[0]
                
                # Try to get a sample record
                sample_query = f"SELECT * FROM SAPHANADB.{table_name} LIMIT 1"
                cursor.execute(sample_query)
                sample = cursor.fetchone()
                
                if sample:
                    accessible_tables.append({
                        'table': table_name,
                        'records': actual_count,
                        'accessible': True
                    })
                    print(f"✅ {table_name}: {actual_count:,} records (accessible)")
                else:
                    print(f"🔒 {table_name}: {record_count:,} records (restricted)")
                    
            except Exception as e:
                print(f"❌ {table_name}: {record_count:,} records (no access)")
        
        print(f"\n📋 Found {len(accessible_tables)} accessible sales-related tables")
        
    except Exception as e:
        print(f"❌ Error analyzing tables: {e}")
    
    # Method 2: Analyze system metadata for value insights
    print(f"\n📊 Method 2: System Metadata Analysis")
    print("-" * 35)
    
    try:
        # Look for value-related columns across all tables
        value_columns_query = """
        SELECT 
            SCHEMA_NAME,
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE_NAME
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = 'SAPHANADB'
          AND (UPPER(COLUMN_NAME) LIKE '%NETWR%'
            OR UPPER(COLUMN_NAME) LIKE '%VALUE%'
            OR UPPER(COLUMN_NAME) LIKE '%AMOUNT%'
            OR UPPER(COLUMN_NAME) LIKE '%PRICE%'
            OR UPPER(COLUMN_NAME) LIKE '%KBETR%'  -- Condition rate
            OR UPPER(COLUMN_NAME) LIKE '%KWERT%') -- Condition value
        ORDER BY TABLE_NAME, COLUMN_NAME
        LIMIT 50
        """
        
        cursor.execute(value_columns_query)
        value_columns = cursor.fetchall()
        
        print("💰 Value-related columns found:")
        current_table = None
        for schema, table, column, data_type in value_columns:
            if table != current_table:
                print(f"\n📋 {table}:")
                current_table = table
            print(f"   • {column} ({data_type})")
        
    except Exception as e:
        print(f"❌ Error analyzing value columns: {e}")
    
    # Method 3: Provide recommendations based on SAP knowledge
    print(f"\n💡 Method 3: SAP Business Logic Recommendations")
    print("-" * 45)
    
    recommendations = [
        {
            'indicator': 'Document Flow Complexity',
            'description': 'Orders with many subsequent documents (deliveries, invoices) often have higher values',
            'table': 'VBFA',
            'accessible': False
        },
        {
            'indicator': 'Multiple Line Items',
            'description': 'Orders with many line items (VBAP records) typically have higher total values',
            'table': 'VBAP',
            'accessible': False
        },
        {
            'indicator': 'Condition Records',
            'description': 'Complex pricing conditions often indicate high-value transactions',
            'table': 'KONV',
            'accessible': 'Unknown'
        },
        {
            'indicator': 'Customer Classification',
            'description': 'Key account customers typically place higher value orders',
            'table': 'KNA1',
            'accessible': 'Unknown'
        }
    ]
    
    for rec in recommendations:
        status = "✅" if rec['accessible'] else "❌" if rec['accessible'] is False else "❓"
        print(f"{status} {rec['indicator']}")
        print(f"   {rec['description']}")
        print(f"   Data source: {rec['table']}")
        print()
    
    # Method 4: Provide specific guidance
    print(f"🎯 SPECIFIC GUIDANCE FOR HIGHEST VALUE ACCESS")
    print("-" * 45)
    
    print("To access the actual highest value sales order, you need:")
    print()
    print("1. 🔑 Database User with Privileges:")
    print("   • Request SAPHANADB schema user credentials")
    print("   • Or request SELECT privileges on VBAK table for SYSTEM user")
    print()
    print("2. 📊 Alternative Query Approach:")
    print("   • Use SAP GUI transaction VA05 (List Sales Orders)")
    print("   • Sort by net value (NETWR field)")
    print("   • Export results for analysis")
    print()
    print("3. 🔧 Technical Solution:")
    print("   • Ask SAP administrator to run this query:")
    print("   SELECT VBELN, KUNNR, NETWR, WAERK, ERDAT")
    print("   FROM VBAK")
    print("   WHERE NETWR IS NOT NULL")
    print("   ORDER BY CAST(NETWR AS DECIMAL(15,2)) DESC")
    print("   LIMIT 10;")
    print()
    print("4. 📋 Business User Approach:")
    print("   • Use SAP standard reports like VA05N")
    print("   • Apply selection criteria for high values")
    print("   • Export to Excel for further analysis")
    
    cursor.close()
    conn.close()
    
    return {
        'accessible_tables': len(accessible_tables) if 'accessible_tables' in locals() else 0,
        'analysis_complete': True,
        'recommendations_provided': True
    }

if __name__ == "__main__":
    results = find_high_value_indicators()
    
    print(f"\n🏁 ANALYSIS COMPLETE")
    print("=" * 20)
    print(f"✅ Alternative analysis methods explored")
    print(f"✅ Recommendations provided for accessing highest value orders")
    print(f"✅ Technical solutions identified")
    
    print(f"\n📞 NEXT STEPS:")
    print("1. Request SAPHANADB user access from SAP administrator")
    print("2. Use SAP GUI for direct business user access")
    print("3. Consider using accessible condition/pricing tables")
    print("4. Implement indirect analysis using document flow patterns")
