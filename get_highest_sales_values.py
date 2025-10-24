#!/usr/bin/env python3
"""
Get detailed highest sales values from accessible tables
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def get_highest_sales_values():
    """Get detailed analysis of highest sales values from accessible tables"""
    
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
        
        # Get current timestamp
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        current_time = cursor.fetchone()[0]
        print(f"   Server Time: {current_time}")
        
        print("\n💰 DETAILED SALES VALUE ANALYSIS")
        print("=" * 60)
        
        # Analyze SALES_DATA table in detail
        print("\n🏆 SALES_DATA Table Analysis:")
        print("-" * 40)
        
        # Get all records with detailed information
        cursor.execute("""
        SELECT 
            s.STORE_ID,
            s.WEEK_NUMBER,
            s.PRODUCT_ID,
            s.SALES_REVENUE,
            p.PRODUCT_NAME,
            p.PRODUCT_COST,
            st.STORE_NAME,
            st.LOCATION
        FROM SYSTEM.SALES_DATA s
        LEFT JOIN SYSTEM.PRODUCT_DATA p ON s.PRODUCT_ID = p.PRODUCT_ID
        LEFT JOIN SYSTEM.STORE_DATA st ON s.STORE_ID = st.STORE_ID
        ORDER BY s.SALES_REVENUE DESC
        """)
        
        sales_records = cursor.fetchall()
        
        if sales_records:
            print(f"📊 ALL SALES RECORDS (Ordered by Revenue):")
            print("-" * 100)
            print(f"{'STORE_ID':<8} {'WEEK':<4} {'PRODUCT_ID':<10} {'REVENUE':<10} {'PRODUCT_NAME':<20} {'COST':<8} {'STORE_NAME':<15} {'LOCATION':<15}")
            print("-" * 100)
            
            total_revenue = 0
            for record in sales_records:
                store_id, week, product_id, revenue, product_name, cost, store_name, location = record
                total_revenue += revenue if revenue else 0
                
                product_name = product_name[:19] if product_name else 'N/A'
                store_name = store_name[:14] if store_name else 'N/A'
                location = location[:14] if location else 'N/A'
                
                print(f"{store_id:<8} {week:<4} {product_id:<10} {revenue:<10} {product_name:<20} {cost:<8} {store_name:<15} {location:<15}")
            
            print("-" * 100)
            print(f"TOTAL REVENUE: {total_revenue}")
            
            # Find the highest value record
            highest_record = sales_records[0]  # Already ordered by revenue DESC
            store_id, week, product_id, revenue, product_name, cost, store_name, location = highest_record
            
            print(f"\n🥇 HIGHEST VALUE SALES RECORD:")
            print("=" * 50)
            print(f"Sales Revenue:    ${revenue:,}")
            print(f"Store ID:         {store_id}")
            print(f"Store Name:       {store_name if store_name else 'N/A'}")
            print(f"Location:         {location if location else 'N/A'}")
            print(f"Week Number:      {week}")
            print(f"Product ID:       {product_id}")
            print(f"Product Name:     {product_name if product_name else 'N/A'}")
            print(f"Product Cost:     ${cost if cost else 'N/A'}")
            if cost and revenue:
                profit = revenue - cost
                margin = (profit / revenue) * 100
                print(f"Profit:           ${profit}")
                print(f"Profit Margin:    {margin:.1f}%")
        
        # Get product analysis
        print(f"\n📦 PRODUCT ANALYSIS:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT 
            p.PRODUCT_ID,
            p.PRODUCT_NAME,
            p.PRODUCT_COST,
            COALESCE(SUM(s.SALES_REVENUE), 0) as total_sales,
            COUNT(s.PRODUCT_ID) as sales_count
        FROM SYSTEM.PRODUCT_DATA p
        LEFT JOIN SYSTEM.SALES_DATA s ON p.PRODUCT_ID = s.PRODUCT_ID
        GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME, p.PRODUCT_COST
        ORDER BY total_sales DESC
        """)
        
        product_analysis = cursor.fetchall()
        
        if product_analysis:
            print(f"{'PRODUCT_ID':<10} {'PRODUCT_NAME':<25} {'COST':<8} {'TOTAL_SALES':<12} {'SALES_COUNT':<12}")
            print("-" * 75)
            
            for product_id, product_name, cost, total_sales, sales_count in product_analysis:
                product_name = product_name[:24] if product_name else 'N/A'
                print(f"{product_id:<10} {product_name:<25} ${cost:<7} ${total_sales:<11} {sales_count:<12}")
        
        # Get store analysis
        print(f"\n🏪 STORE ANALYSIS:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT 
            st.STORE_ID,
            st.STORE_NAME,
            st.LOCATION,
            COALESCE(SUM(s.SALES_REVENUE), 0) as total_sales,
            COUNT(s.STORE_ID) as sales_count
        FROM SYSTEM.STORE_DATA st
        LEFT JOIN SYSTEM.SALES_DATA s ON st.STORE_ID = s.STORE_ID
        GROUP BY st.STORE_ID, st.STORE_NAME, st.LOCATION
        ORDER BY total_sales DESC
        """)
        
        store_analysis = cursor.fetchall()
        
        if store_analysis:
            print(f"{'STORE_ID':<8} {'STORE_NAME':<20} {'LOCATION':<15} {'TOTAL_SALES':<12} {'SALES_COUNT':<12}")
            print("-" * 75)
            
            for store_id, store_name, location, total_sales, sales_count in store_analysis:
                store_name = store_name[:19] if store_name else 'N/A'
                location = location[:14] if location else 'N/A'
                print(f"{store_id:<8} {store_name:<20} {location:<15} ${total_sales:<11} {sales_count:<12}")
        
        # Try to access the salesdata3 table with different approaches
        print(f"\n🔍 Attempting to access salesdata3 table:")
        print("-" * 50)
        
        # First, let's see what schemas contain salesdata3
        cursor.execute("""
        SELECT SCHEMA_NAME, TABLE_NAME, RECORD_COUNT
        FROM SYS.M_TABLES 
        WHERE TABLE_NAME = 'salesdata3'
        """)
        
        salesdata3_info = cursor.fetchall()
        if salesdata3_info:
            for schema, table, records in salesdata3_info:
                print(f"Found {table} in schema {schema} with {records:,} records")
                
                # Try to access it
                try:
                    cursor.execute(f"SELECT TOP 5 * FROM {schema}.{table} ORDER BY checkout_price DESC")
                    sample_records = cursor.fetchall()
                    
                    if sample_records:
                        print(f"\n🏆 TOP 5 HIGHEST checkout_price from {schema}.{table}:")
                        print("-" * 80)
                        
                        for i, record in enumerate(sample_records, 1):
                            print(f"Rank {i}: {record}")
                            
                        # Get the highest value
                        highest_checkout = sample_records[0]
                        print(f"\n💰 HIGHEST CHECKOUT PRICE: ${highest_checkout[4]}")  # checkout_price is 5th column (index 4)
                        
                except Exception as e:
                    print(f"❌ Cannot access {schema}.{table}: {str(e)[:60]}...")
        else:
            print("❌ salesdata3 table not found in any accessible schema")
        
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
    print("SAP HANA - Highest Sales Values Analysis")
    print("=" * 70)
    get_highest_sales_values()
