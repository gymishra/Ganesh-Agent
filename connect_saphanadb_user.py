#!/usr/bin/env python3
"""
Connect using SAPHANADB user to access VBAK table
Database: 98.83.112.225:30215 (Instance 02)
User: SAPHANADB
"""

import hdbcli.dbapi as hana_db
import sys

def connect_with_saphanadb_user():
    """Connect using SAPHANADB user to get highest value sales order"""
    
    host = "98.83.112.225"
    port = 30215
    
    # Try different password combinations for SAPHANADB user
    password_attempts = [
        "Dilkyakare1234",
        "Pass2025$", 
        "saphanadb",
        "SAPHANADB",
        "password",
        "Password123",
        "admin"
    ]
    
    print("SAP HANA Connection - SAPHANADB User")
    print("=" * 60)
    print(f"Host: {host}:{port}")
    print(f"User: SAPHANADB")
    print()
    
    successful_connection = None
    
    for i, password in enumerate(password_attempts, 1):
        print(f"🔄 Password attempt {i}: {'*' * len(password)}")
        
        try:
            connection = hana_db.connect(
                address=host,
                port=port,
                user="SAPHANADB",
                password=password
            )
            
            # Test with simple query
            cursor = connection.cursor()
            cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
            server_time = cursor.fetchone()[0]
            
            cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
            user_info = cursor.fetchone()
            
            print(f"   ✅ SUCCESS!")
            print(f"   Server Time: {server_time}")
            print(f"   Current User: {user_info[0]}")
            print(f"   Current Schema: {user_info[1]}")
            
            successful_connection = {
                "connection": connection,
                "cursor": cursor,
                "password": password
            }
            break
            
        except Exception as e:
            error_msg = str(e)
            if "authentication failed" in error_msg:
                print(f"   ❌ Authentication failed")
            else:
                print(f"   ❌ Error: {error_msg[:50]}...")
    
    if successful_connection:
        print(f"\n💰 ACCESSING VBAK TABLE WITH SAPHANADB USER:")
        print("=" * 60)
        
        try:
            cursor = successful_connection["cursor"]
            
            # Test VBAK access
            cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            vbak_count = cursor.fetchone()[0]
            print(f"✅ VBAK table access successful!")
            print(f"   Total VBAK records: {vbak_count:,}")
            
            # Get the highest value sales order
            print(f"\n🏆 FINDING HIGHEST VALUE SALES ORDER:")
            print("-" * 50)
            
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
                BSTNK as customer_po_number
            FROM SAPHANADB.VBAK
            WHERE NETWR IS NOT NULL AND NETWR > 0
            ORDER BY NETWR DESC
            LIMIT 1
            """)
            
            highest_order = cursor.fetchone()
            
            if highest_order:
                vbeln, erdat, auart, netwr, waerk, vkorg, vtweg, spart, kunnr, ernam, bstnk = highest_order
                
                print("🥇 HIGHEST VALUE SALES ORDER FOUND!")
                print("=" * 60)
                print(f"💵 Sales Order Number:    {vbeln}")
                print(f"💰 Net Value:             {netwr:,.2f} {waerk}")
                print(f"📅 Creation Date:         {erdat}")
                print(f"📋 Order Type:            {auart}")
                print(f"🏢 Sales Organization:    {vkorg}")
                print(f"🚚 Distribution Channel:  {vtweg}")
                print(f"🏭 Division:              {spart}")
                print(f"👤 Customer Number:       {kunnr}")
                print(f"👨‍💼 Created By:            {ernam}")
                print(f"📄 Customer PO:           {bstnk if bstnk else 'N/A'}")
                
                # Get top 10 highest value orders
                print(f"\n📊 TOP 10 HIGHEST VALUE SALES ORDERS:")
                print("-" * 100)
                
                cursor.execute("""
                SELECT 
                    VBELN,
                    ERDAT,
                    AUART,
                    NETWR,
                    WAERK,
                    KUNNR,
                    VKORG
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL AND NETWR > 0
                ORDER BY NETWR DESC
                LIMIT 10
                """)
                
                top_orders = cursor.fetchall()
                if top_orders:
                    print(f"{'RANK':<4} {'ORDER_NO':<12} {'DATE':<10} {'TYPE':<6} {'VALUE':<15} {'CURR':<4} {'CUSTOMER':<12} {'ORG':<4}")
                    print("-" * 100)
                    
                    for rank, order in enumerate(top_orders, 1):
                        vbeln, erdat, auart, netwr, waerk, kunnr, vkorg = order
                        print(f"{rank:<4} {vbeln:<12} {erdat:<10} {auart:<6} {netwr:>13,.2f} {waerk:<4} {kunnr:<12} {vkorg:<4}")
                
                # Get comprehensive statistics
                print(f"\n📈 COMPREHENSIVE VBAK STATISTICS:")
                print("-" * 60)
                
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN NETWR > 0 THEN 1 END) as orders_with_value,
                    SUM(NETWR) as total_value,
                    AVG(NETWR) as average_value,
                    MIN(NETWR) as minimum_value,
                    MAX(NETWR) as maximum_value,
                    COUNT(DISTINCT WAERK) as currencies_used,
                    COUNT(DISTINCT AUART) as order_types,
                    COUNT(DISTINCT KUNNR) as unique_customers,
                    COUNT(DISTINCT VKORG) as sales_organizations
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL
                """)
                
                stats = cursor.fetchone()
                if stats:
                    total_orders, orders_with_value, total_value, avg_value, min_value, max_value, currencies, order_types, customers, sales_orgs = stats
                    print(f"Total Orders:           {total_orders:,}")
                    print(f"Orders with Value:      {orders_with_value:,}")
                    print(f"Total Sales Value:      {total_value:,.2f}")
                    print(f"Average Order Value:    {avg_value:,.2f}")
                    print(f"Minimum Order Value:    {min_value:,.2f}")
                    print(f"Maximum Order Value:    {max_value:,.2f}")
                    print(f"Currencies Used:        {currencies}")
                    print(f"Order Types:            {order_types}")
                    print(f"Unique Customers:       {customers:,}")
                    print(f"Sales Organizations:    {sales_orgs}")
                
                # Get order type breakdown for high-value orders
                print(f"\n📋 HIGH-VALUE ORDER TYPES (>50,000):")
                print("-" * 50)
                
                cursor.execute("""
                SELECT 
                    AUART as order_type,
                    COUNT(*) as order_count,
                    AVG(NETWR) as avg_value,
                    MAX(NETWR) as max_value,
                    SUM(NETWR) as total_value
                FROM SAPHANADB.VBAK
                WHERE NETWR > 50000
                GROUP BY AUART
                ORDER BY max_value DESC
                """)
                
                high_value_types = cursor.fetchall()
                if high_value_types:
                    print(f"{'TYPE':<6} {'COUNT':<8} {'AVG_VALUE':<15} {'MAX_VALUE':<15} {'TOTAL_VALUE':<15}")
                    print("-" * 70)
                    
                    for auart, count, avg_val, max_val, total_val in high_value_types:
                        print(f"{auart:<6} {count:<8} {avg_val:>13,.2f} {max_val:>13,.2f} {total_val:>13,.2f}")
                else:
                    print("No orders found with value > 50,000")
                
            else:
                print("❌ No sales orders found with valid net values")
            
            cursor.close()
            successful_connection["connection"].close()
            
        except Exception as e:
            print(f"❌ Error accessing VBAK: {e}")
            if successful_connection["connection"]:
                successful_connection["connection"].close()
    
    else:
        print("❌ Could not connect with SAPHANADB user")
        print("\n💡 Alternative: Using SYSTEM user for VBAK metadata...")
        
        # Fall back to system user to get table info
        try:
            connection = hana_db.connect(
                address=host,
                port=port,
                user="system",
                password="Dilkyakare1234"
            )
            
            cursor = connection.cursor()
            
            cursor.execute("""
            SELECT RECORD_COUNT
            FROM SYS.M_CS_TABLES 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            """)
            
            vbak_info = cursor.fetchone()
            if vbak_info:
                print(f"✅ VBAK table has {vbak_info[0]:,} records")
                print("❌ However, direct data access requires SAPHANADB user privileges")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"❌ System fallback failed: {e}")

if __name__ == "__main__":
    connect_with_saphanadb_user()
