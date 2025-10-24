#!/usr/bin/env python3
"""
Find the sales order with highest sales value from VBAK table
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def find_highest_value_sales_order():
    """Find the sales order with the highest net value (NETWR) from VBAK table"""
    
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
        
        print("\n💰 Finding sales order with highest value...")
        
        # First, let's check if we can access the VBAK table directly
        try:
            # Query to find the highest value sales order
            cursor.execute("""
            SELECT 
                VBELN as sales_order_number,
                ERDAT as creation_date,
                AUART as order_type,
                NETWR as net_value,
                WAERK as currency,
                VKORG as sales_organization,
                VTWEG as distribution_channel,
                SPART as division,
                KUNNR as customer_number,
                ERNAM as created_by,
                BSTNK as customer_po_number,
                BSTDK as customer_po_date
            FROM SAPHANADB.VBAK
            WHERE NETWR IS NOT NULL
            ORDER BY NETWR DESC
            LIMIT 1
            """)
            
            highest_order = cursor.fetchone()
            
            if highest_order:
                vbeln, erdat, auart, netwr, waerk, vkorg, vtweg, spart, kunnr, ernam, bstnk, bstdk = highest_order
                
                print("🏆 HIGHEST VALUE SALES ORDER FOUND!")
                print("=" * 60)
                print(f"Sales Order Number:    {vbeln}")
                print(f"Net Value:             {netwr:,.2f} {waerk}")
                print(f"Creation Date:         {erdat}")
                print(f"Order Type:            {auart}")
                print(f"Sales Organization:    {vkorg}")
                print(f"Distribution Channel:  {vtweg}")
                print(f"Division:              {spart}")
                print(f"Customer Number:       {kunnr}")
                print(f"Created By:            {ernam}")
                print(f"Customer PO Number:    {bstnk if bstnk else 'N/A'}")
                print(f"Customer PO Date:      {bstdk if bstdk else 'N/A'}")
                
                # Get top 5 highest value orders for comparison
                print(f"\n📊 TOP 5 HIGHEST VALUE SALES ORDERS:")
                cursor.execute("""
                SELECT 
                    VBELN,
                    ERDAT,
                    AUART,
                    NETWR,
                    WAERK,
                    VKORG,
                    KUNNR
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL
                ORDER BY NETWR DESC
                LIMIT 5
                """)
                
                top_orders = cursor.fetchall()
                if top_orders:
                    print("-" * 90)
                    print(f"{'RANK':<4} {'ORDER_NO':<12} {'DATE':<10} {'TYPE':<6} {'VALUE':<15} {'CURR':<4} {'ORG':<4} {'CUSTOMER':<12}")
                    print("-" * 90)
                    
                    for rank, order in enumerate(top_orders, 1):
                        vbeln, erdat, auart, netwr, waerk, vkorg, kunnr = order
                        print(f"{rank:<4} {vbeln:<12} {erdat:<10} {auart:<6} {netwr:>13,.2f} {waerk:<4} {vkorg:<4} {kunnr:<12}")
                
                # Get some statistics about sales values
                print(f"\n📈 SALES VALUE STATISTICS:")
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(NETWR) as total_value,
                    AVG(NETWR) as average_value,
                    MIN(NETWR) as minimum_value,
                    MAX(NETWR) as maximum_value,
                    COUNT(DISTINCT WAERK) as currencies_used
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL AND NETWR > 0
                """)
                
                stats = cursor.fetchone()
                if stats:
                    total_orders, total_value, avg_value, min_value, max_value, currencies = stats
                    print("-" * 50)
                    print(f"Total Orders:         {total_orders:,}")
                    print(f"Total Sales Value:    {total_value:,.2f}")
                    print(f"Average Order Value:  {avg_value:,.2f}")
                    print(f"Minimum Order Value:  {min_value:,.2f}")
                    print(f"Maximum Order Value:  {max_value:,.2f}")
                    print(f"Currencies Used:      {currencies}")
                
                # Check order types distribution for high-value orders
                print(f"\n📋 ORDER TYPES FOR HIGH-VALUE ORDERS (>10,000):")
                cursor.execute("""
                SELECT 
                    AUART as order_type,
                    COUNT(*) as order_count,
                    AVG(NETWR) as avg_value,
                    MAX(NETWR) as max_value
                FROM SAPHANADB.VBAK
                WHERE NETWR > 10000
                GROUP BY AUART
                ORDER BY max_value DESC
                """)
                
                order_types = cursor.fetchall()
                if order_types:
                    print("-" * 60)
                    print(f"{'TYPE':<6} {'COUNT':<8} {'AVG_VALUE':<15} {'MAX_VALUE':<15}")
                    print("-" * 60)
                    
                    for auart, count, avg_val, max_val in order_types:
                        print(f"{auart:<6} {count:<8} {avg_val:>13,.2f} {max_val:>13,.2f}")
                
            else:
                print("❌ No sales orders found with valid net values")
                
        except Exception as e:
            print(f"❌ Error querying VBAK table: {e}")
            
            # If direct access fails, try to get information from system tables
            print(f"\n🔄 Trying alternative approach using system statistics...")
            try:
                cursor.execute("""
                SELECT 
                    SCHEMA_NAME,
                    TABLE_NAME,
                    RECORD_COUNT
                FROM SYS.M_CS_TABLES 
                WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
                """)
                
                table_info = cursor.fetchone()
                if table_info:
                    schema, table, records = table_info
                    print(f"✅ VBAK table has {records:,} records")
                    print("❌ However, direct data access requires additional privileges")
                else:
                    print("❌ Could not find VBAK table information")
                    
            except Exception as e2:
                print(f"❌ Alternative approach also failed: {e2}")
        
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
    print("SAP HANA - Highest Value Sales Order Analysis")
    print("=" * 70)
    find_highest_value_sales_order()
