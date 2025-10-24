#!/usr/bin/env python3
"""
Complete sales analysis with fixed queries
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def complete_sales_analysis():
    """Complete analysis of sales data with fixed queries"""
    
    host = "98.83.112.225"
    port = 30215
    username = "system"
    password = "Dilkyakare1234"
    
    connection = None
    
    try:
        print("🔌 Connecting to SAP HANA...")
        connection = hana_db.connect(address=host, port=port, user=username, password=password)
        print("✅ Connection successful!")
        
        cursor = connection.cursor()
        
        print("\n💰 COMPLETE SALES ANALYSIS")
        print("=" * 60)
        
        # Get the highest value sales record with all details
        print("\n🏆 HIGHEST VALUE SALES RECORD:")
        print("=" * 50)
        
        cursor.execute("""
        SELECT 
            s.STORE_ID,
            s.WEEK_NUMBER,
            s.PRODUCT_ID,
            s.SALES_REVENUE
        FROM SYSTEM.SALES_DATA s
        ORDER BY s.SALES_REVENUE DESC
        LIMIT 1
        """)
        
        highest_sale = cursor.fetchone()
        if highest_sale:
            store_id, week, product_id, revenue = highest_sale
            
            # Get store details
            cursor.execute(f"SELECT STORE_NAME, LOCATION FROM SYSTEM.STORE_DATA WHERE STORE_ID = {store_id}")
            store_info = cursor.fetchone()
            store_name, location = store_info if store_info else ('N/A', 'N/A')
            
            # Get product details
            cursor.execute(f"SELECT PRODUCT_NAME, PRODUCT_COST FROM SYSTEM.PRODUCT_DATA WHERE PRODUCT_ID = {product_id}")
            product_info = cursor.fetchone()
            product_name, product_cost = product_info if product_info else ('N/A', 0)
            
            print(f"💵 HIGHEST SALES VALUE: ${revenue:,}")
            print(f"🏪 Store: {store_name} (ID: {store_id})")
            print(f"📍 Location: {location}")
            print(f"📅 Week: {week}")
            print(f"📦 Product: {product_name} (ID: {product_id})")
            print(f"💰 Product Cost: ${product_cost}")
            
            if product_cost and revenue:
                profit = revenue - product_cost
                margin = (profit / revenue) * 100 if revenue > 0 else 0
                print(f"📈 Profit: ${profit}")
                print(f"📊 Profit Margin: {margin:.1f}%")
        
        # Get all sales records summary
        print(f"\n📊 ALL SALES RECORDS SUMMARY:")
        print("-" * 50)
        
        cursor.execute("""
        SELECT 
            s.STORE_ID,
            s.WEEK_NUMBER,
            s.PRODUCT_ID,
            s.SALES_REVENUE
        FROM SYSTEM.SALES_DATA s
        ORDER BY s.SALES_REVENUE DESC
        """)
        
        all_sales = cursor.fetchall()
        total_revenue = 0
        
        print(f"{'RANK':<4} {'STORE_ID':<8} {'WEEK':<4} {'PRODUCT_ID':<10} {'REVENUE':<10}")
        print("-" * 40)
        
        for rank, (store_id, week, product_id, revenue) in enumerate(all_sales, 1):
            total_revenue += revenue
            print(f"{rank:<4} {store_id:<8} {week:<4} {product_id:<10} ${revenue:<9}")
        
        print("-" * 40)
        print(f"TOTAL REVENUE: ${total_revenue}")
        print(f"AVERAGE REVENUE: ${total_revenue/len(all_sales):.2f}")
        
        # Product performance analysis
        print(f"\n📦 PRODUCT PERFORMANCE:")
        print("-" * 40)
        
        cursor.execute("SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_COST FROM SYSTEM.PRODUCT_DATA")
        products = cursor.fetchall()
        
        for product_id, product_name, cost in products:
            cursor.execute(f"SELECT SUM(SALES_REVENUE), COUNT(*) FROM SYSTEM.SALES_DATA WHERE PRODUCT_ID = {product_id}")
            sales_info = cursor.fetchone()
            total_sales, sales_count = sales_info if sales_info and sales_info[0] else (0, 0)
            
            print(f"Product: {product_name}")
            print(f"  ID: {product_id}, Cost: ${cost}")
            print(f"  Total Sales: ${total_sales}, Orders: {sales_count}")
            if cost and total_sales:
                total_profit = total_sales - (cost * sales_count)
                print(f"  Total Profit: ${total_profit}")
            print()
        
        # Store performance analysis
        print(f"🏪 STORE PERFORMANCE:")
        print("-" * 40)
        
        cursor.execute("SELECT STORE_ID, STORE_NAME, LOCATION FROM SYSTEM.STORE_DATA")
        stores = cursor.fetchall()
        
        for store_id, store_name, location in stores:
            cursor.execute(f"SELECT SUM(SALES_REVENUE), COUNT(*) FROM SYSTEM.SALES_DATA WHERE STORE_ID = {store_id}")
            sales_info = cursor.fetchone()
            total_sales, sales_count = sales_info if sales_info and sales_info[0] else (0, 0)
            
            print(f"Store: {store_name}")
            print(f"  ID: {store_id}, Location: {location}")
            print(f"  Total Sales: ${total_sales}, Orders: {sales_count}")
            print()
        
        # Check for the large salesdata3 table
        print(f"🔍 CHECKING FOR LARGE SALES DATASET:")
        print("-" * 50)
        
        cursor.execute("""
        SELECT SCHEMA_NAME, TABLE_NAME, RECORD_COUNT
        FROM SYS.M_TABLES 
        WHERE TABLE_NAME LIKE '%sales%' OR TABLE_NAME LIKE '%SALES%'
        ORDER BY RECORD_COUNT DESC
        """)
        
        sales_tables = cursor.fetchall()
        if sales_tables:
            print("Found sales-related tables:")
            for schema, table, records in sales_tables:
                print(f"  {schema}.{table}: {records:,} records")
                
                # Try to access the large table if it exists
                if records and records > 1000:
                    try:
                        cursor.execute(f"""
                        SELECT COLUMN_NAME, DATA_TYPE_NAME 
                        FROM TABLE_COLUMNS 
                        WHERE SCHEMA_NAME = '{schema}' AND TABLE_NAME = '{table}'
                        ORDER BY POSITION
                        """)
                        
                        columns = cursor.fetchall()
                        value_columns = [col for col, dtype in columns if 'price' in col.lower() or 'amount' in col.lower() or 'revenue' in col.lower()]
                        
                        if value_columns:
                            print(f"    Value columns: {', '.join(value_columns)}")
                            
                            # Try to get highest value
                            for col in value_columns[:1]:  # Just check first value column
                                try:
                                    cursor.execute(f"SELECT MAX({col}) FROM {schema}.{table}")
                                    max_value = cursor.fetchone()[0]
                                    if max_value:
                                        print(f"    🏆 Highest {col}: ${max_value}")
                                except Exception as e:
                                    print(f"    ❌ Cannot access {col}: {str(e)[:30]}...")
                                    
                    except Exception as e:
                        print(f"    ❌ Cannot analyze structure: {str(e)[:40]}...")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return True

if __name__ == "__main__":
    print("SAP HANA - Complete Sales Analysis")
    print("=" * 70)
    complete_sales_analysis()
