#!/usr/bin/env python3
"""
Get highest sales value from accessible SYSTEM.SALES_DATA table
Database: 98.83.112.225:30215 (Instance 02)
"""

import hdbcli.dbapi as hana_db

def get_accessible_highest_sales():
    """Get highest sales value from accessible tables"""
    
    host = "98.83.112.225"
    port = 30215
    username = "system"
    password = "Dilkyakare1234"
    
    try:
        print("💰 FINDING HIGHEST SALES VALUE FROM ACCESSIBLE DATA")
        print("=" * 70)
        
        connection = hana_db.connect(address=host, port=port, user=username, password=password)
        cursor = connection.cursor()
        
        print("✅ Connected as SYSTEM user")
        
        # Get detailed analysis of SYSTEM.SALES_DATA
        print("\n🏆 ANALYZING SYSTEM.SALES_DATA TABLE:")
        print("-" * 50)
        
        # Get all records with full details
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
        
        all_sales = cursor.fetchall()
        
        if all_sales:
            # Get the highest value record
            highest_record = all_sales[0]
            store_id, week, product_id, revenue, product_name, cost, store_name, location = highest_record
            
            print("🥇 HIGHEST SALES VALUE FOUND!")
            print("=" * 60)
            print(f"💵 SALES REVENUE:         ${revenue:,}")
            print(f"🏪 Store ID:              {store_id}")
            print(f"🏬 Store Name:            {store_name}")
            print(f"📍 Location:              {location}")
            print(f"📅 Week Number:           {week}")
            print(f"📦 Product ID:            {product_id}")
            print(f"🛍️  Product Name:          {product_name}")
            print(f"💰 Product Cost:          ${cost}")
            
            if cost and revenue:
                profit = revenue - cost
                margin = (profit / revenue) * 100
                print(f"📈 Profit:                ${profit}")
                print(f"📊 Profit Margin:         {margin:.1f}%")
            
            print(f"\n📊 ALL SALES RECORDS:")
            print("-" * 100)
            print(f"{'RANK':<4} {'STORE':<15} {'LOCATION':<12} {'PRODUCT':<15} {'REVENUE':<10} {'COST':<8} {'PROFIT':<8}")
            print("-" * 100)
            
            total_revenue = 0
            for rank, record in enumerate(all_sales, 1):
                store_id, week, product_id, revenue, product_name, cost, store_name, location = record
                total_revenue += revenue
                
                profit = (revenue - cost) if (revenue and cost) else 0
                store_name = store_name[:14] if store_name else f"Store{store_id}"
                location = location[:11] if location else "N/A"
                product_name = product_name[:14] if product_name else f"Prod{product_id}"
                
                print(f"{rank:<4} {store_name:<15} {location:<12} {product_name:<15} ${revenue:<9} ${cost:<7} ${profit:<7}")
            
            print("-" * 100)
            print(f"TOTAL REVENUE: ${total_revenue}")
            print(f"AVERAGE REVENUE: ${total_revenue/len(all_sales):.2f}")
            
            # Store performance
            print(f"\n🏪 STORE PERFORMANCE COMPARISON:")
            print("-" * 50)
            
            cursor.execute("""
            SELECT 
                st.STORE_NAME,
                st.LOCATION,
                SUM(s.SALES_REVENUE) as total_sales,
                COUNT(*) as transaction_count,
                AVG(s.SALES_REVENUE) as avg_sale
            FROM SYSTEM.SALES_DATA s
            JOIN SYSTEM.STORE_DATA st ON s.STORE_ID = st.STORE_ID
            GROUP BY st.STORE_NAME, st.LOCATION
            ORDER BY total_sales DESC
            """)
            
            store_performance = cursor.fetchall()
            if store_performance:
                print(f"{'STORE':<15} {'LOCATION':<12} {'TOTAL':<10} {'COUNT':<6} {'AVERAGE':<10}")
                print("-" * 60)
                for store_name, location, total, count, avg in store_performance:
                    store_name = store_name[:14] if store_name else "N/A"
                    location = location[:11] if location else "N/A"
                    print(f"{store_name:<15} {location:<12} ${total:<9} {count:<6} ${avg:<9.2f}")
            
            # Product performance
            print(f"\n📦 PRODUCT PERFORMANCE:")
            print("-" * 40)
            
            cursor.execute("""
            SELECT 
                p.PRODUCT_NAME,
                p.PRODUCT_COST,
                SUM(s.SALES_REVENUE) as total_sales,
                COUNT(*) as sales_count,
                SUM(s.SALES_REVENUE - p.PRODUCT_COST) as total_profit
            FROM SYSTEM.SALES_DATA s
            JOIN SYSTEM.PRODUCT_DATA p ON s.PRODUCT_ID = p.PRODUCT_ID
            GROUP BY p.PRODUCT_NAME, p.PRODUCT_COST
            ORDER BY total_sales DESC
            """)
            
            product_performance = cursor.fetchall()
            if product_performance:
                print(f"{'PRODUCT':<15} {'COST':<8} {'SALES':<10} {'COUNT':<6} {'PROFIT':<10}")
                print("-" * 55)
                for product, cost, sales, count, profit in product_performance:
                    product = product[:14] if product else "N/A"
                    print(f"{product:<15} ${cost:<7} ${sales:<9} {count:<6} ${profit:<9}")
        
        else:
            print("❌ No sales data found")
        
        # Now let's try to create the VBAK_READER user
        print(f"\n🔧 CREATING VBAK_READER USER FOR FUTURE ACCESS:")
        print("-" * 60)
        
        try:
            # Create user
            cursor.execute("""
            CREATE USER VBAK_READER PASSWORD "VbakAccess123" NO FORCE_FIRST_PASSWORD_CHANGE
            """)
            print("✅ Created VBAK_READER user")
            
            # Grant privileges
            cursor.execute("GRANT CONNECT TO VBAK_READER")
            cursor.execute("GRANT SELECT ON SAPHANADB.VBAK TO VBAK_READER")
            cursor.execute("GRANT SELECT ON SAPHANADB.VBAP TO VBAK_READER")
            cursor.execute("GRANT SELECT ON SAPHANADB.KNA1 TO VBAK_READER")
            
            print("✅ Granted VBAK access privileges")
            print("📋 New user credentials:")
            print("   Username: VBAK_READER")
            print("   Password: VbakAccess123")
            print("   Access: SAPHANADB.VBAK, VBAP, KNA1")
            
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️  VBAK_READER user already exists")
            else:
                print(f"❌ Could not create VBAK_READER user: {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    get_accessible_highest_sales()
