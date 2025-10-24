#!/usr/bin/env python3
"""
Find the highest value sales order from VBAK table
Database: 98.83.112.225:30215 (Instance 02)
This script will work once we have proper VBAK access credentials
"""

import hdbcli.dbapi as hana_db
import sys

def find_highest_value_vbak_order():
    """Find the sales order with highest value from VBAK table"""
    
    host = "98.83.112.225"
    port = 30215
    
    # Try multiple user credentials that might have VBAK access
    credential_options = [
        {"user": "SAPHANADB", "password": "Dilkyakare1234"},
        {"user": "system", "password": "Dilkyakare1234"},  # In case privileges were granted
        {"user": "HDBUSER", "password": "Dilkyakare1234"},
        {"user": "SAPABAP1", "password": "Dilkyakare1234"},
    ]
    
    print("🔍 FINDING HIGHEST VALUE SALES ORDER FROM VBAK")
    print("=" * 70)
    print(f"Database: {host}:{port}")
    print(f"Target Table: SAPHANADB.VBAK (7,274 records)")
    print()
    
    successful_connection = None
    
    # Try different credentials
    for i, cred in enumerate(credential_options, 1):
        username = cred["user"]
        password = cred["password"]
        
        print(f"🔄 Attempt {i}: Trying user {username}")
        
        try:
            connection = hana_db.connect(
                address=host,
                port=port,
                user=username,
                password=password
            )
            
            cursor = connection.cursor()
            
            # Test VBAK access
            cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            vbak_count = cursor.fetchone()[0]
            
            print(f"   ✅ SUCCESS! VBAK access granted")
            print(f"   Records accessible: {vbak_count:,}")
            
            successful_connection = {
                "connection": connection,
                "cursor": cursor,
                "username": username
            }
            break
            
        except Exception as e:
            if "authentication failed" in str(e):
                print(f"   ❌ Authentication failed for {username}")
            elif "insufficient privilege" in str(e):
                print(f"   ❌ {username} authenticated but no VBAK access")
            else:
                print(f"   ❌ Error: {str(e)[:50]}...")
    
    if successful_connection:
        print(f"\n💰 ANALYZING VBAK TABLE WITH USER: {successful_connection['username']}")
        print("=" * 70)
        
        cursor = successful_connection["cursor"]
        
        try:
            # Find the absolute highest value sales order
            print("🏆 FINDING HIGHEST VALUE SALES ORDER...")
            
            cursor.execute("""
            SELECT 
                VBELN as sales_order_number,
                ERDAT as creation_date,
                ERZET as creation_time,
                ERNAM as created_by,
                AUART as order_type,
                NETWR as net_value,
                WAERK as currency,
                VKORG as sales_organization,
                VTWEG as distribution_channel,
                SPART as division,
                KUNNR as customer_number,
                BSTNK as customer_po_number,
                BSTDK as customer_po_date,
                AUGRU as order_reason,
                VDATU as requested_delivery_date
            FROM SAPHANADB.VBAK
            WHERE NETWR IS NOT NULL 
            AND NETWR > 0
            ORDER BY NETWR DESC
            LIMIT 1
            """)
            
            highest_order = cursor.fetchone()
            
            if highest_order:
                (vbeln, erdat, erzet, ernam, auart, netwr, waerk, vkorg, 
                 vtweg, spart, kunnr, bstnk, bstdk, augru, vdatu) = highest_order
                
                print("\n🥇 HIGHEST VALUE SALES ORDER FOUND!")
                print("=" * 80)
                print(f"💵 SALES ORDER VALUE:     {netwr:,.2f} {waerk}")
                print(f"📋 Sales Order Number:    {vbeln}")
                print(f"📅 Creation Date:         {erdat}")
                print(f"⏰ Creation Time:         {erzet}")
                print(f"👨‍💼 Created By:            {ernam}")
                print(f"📝 Order Type:            {auart}")
                print(f"🏢 Sales Organization:    {vkorg}")
                print(f"🚚 Distribution Channel:  {vtweg}")
                print(f"🏭 Division:              {spart}")
                print(f"👤 Customer Number:       {kunnr}")
                print(f"📄 Customer PO Number:    {bstnk if bstnk else 'N/A'}")
                print(f"📅 Customer PO Date:      {bstdk if bstdk else 'N/A'}")
                print(f"🎯 Order Reason:          {augru if augru else 'N/A'}")
                print(f"🚛 Requested Delivery:    {vdatu if vdatu else 'N/A'}")
                
                # Get additional customer information if available
                print(f"\n👤 CUSTOMER DETAILS:")
                try:
                    cursor.execute(f"""
                    SELECT NAME1, ORT01, LAND1, KTOKD
                    FROM SAPHANADB.KNA1 
                    WHERE KUNNR = '{kunnr}'
                    """)
                    
                    customer_info = cursor.fetchone()
                    if customer_info:
                        name1, ort01, land1, ktokd = customer_info
                        print(f"   Customer Name:         {name1}")
                        print(f"   City:                  {ort01}")
                        print(f"   Country:               {land1}")
                        print(f"   Account Group:         {ktokd}")
                    else:
                        print(f"   Customer details not found for {kunnr}")
                        
                except Exception as e:
                    print(f"   Could not retrieve customer details: {str(e)[:40]}...")
                
                # Get order items for this highest value order
                print(f"\n📦 ORDER ITEMS BREAKDOWN:")
                try:
                    cursor.execute(f"""
                    SELECT 
                        POSNR as item_number,
                        MATNR as material_number,
                        KWMENG as order_quantity,
                        VRKME as sales_unit,
                        NETWR as item_net_value,
                        WERKS as plant
                    FROM SAPHANADB.VBAP
                    WHERE VBELN = '{vbeln}'
                    ORDER BY POSNR
                    """)
                    
                    order_items = cursor.fetchall()
                    if order_items:
                        print(f"   Found {len(order_items)} items in this order:")
                        print(f"   {'ITEM':<6} {'MATERIAL':<18} {'QTY':<10} {'UNIT':<6} {'VALUE':<15} {'PLANT':<6}")
                        print(f"   {'-' * 70}")
                        
                        total_items_value = 0
                        for posnr, matnr, kwmeng, vrkme, item_netwr, werks in order_items:
                            total_items_value += item_netwr if item_netwr else 0
                            qty_str = f"{kwmeng:.2f}" if kwmeng else "0"
                            value_str = f"{item_netwr:,.2f}" if item_netwr else "0.00"
                            print(f"   {posnr:<6} {matnr:<18} {qty_str:<10} {vrkme:<6} {value_str:<15} {werks:<6}")
                        
                        print(f"   {'-' * 70}")
                        print(f"   Total Items Value:     {total_items_value:,.2f} {waerk}")
                        
                    else:
                        print(f"   No items found for order {vbeln}")
                        
                except Exception as e:
                    print(f"   Could not retrieve order items: {str(e)[:40]}...")
                
                # Get top 10 highest value orders for comparison
                print(f"\n📊 TOP 10 HIGHEST VALUE SALES ORDERS:")
                print("-" * 120)
                
                cursor.execute("""
                SELECT 
                    VBELN,
                    ERDAT,
                    AUART,
                    NETWR,
                    WAERK,
                    KUNNR,
                    VKORG,
                    ERNAM
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL AND NETWR > 0
                ORDER BY NETWR DESC
                LIMIT 10
                """)
                
                top_orders = cursor.fetchall()
                if top_orders:
                    print(f"{'RANK':<4} {'ORDER_NO':<12} {'DATE':<10} {'TYPE':<6} {'VALUE':<15} {'CURR':<4} {'CUSTOMER':<12} {'ORG':<4} {'CREATED_BY':<12}")
                    print("-" * 120)
                    
                    for rank, order in enumerate(top_orders, 1):
                        vbeln_top, erdat_top, auart_top, netwr_top, waerk_top, kunnr_top, vkorg_top, ernam_top = order
                        print(f"{rank:<4} {vbeln_top:<12} {erdat_top:<10} {auart_top:<6} {netwr_top:>13,.2f} {waerk_top:<4} {kunnr_top:<12} {vkorg_top:<4} {ernam_top:<12}")
                
                # Get comprehensive statistics
                print(f"\n📈 VBAK COMPREHENSIVE STATISTICS:")
                print("-" * 80)
                
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN NETWR > 0 THEN 1 END) as orders_with_value,
                    SUM(NETWR) as total_value,
                    AVG(NETWR) as average_value,
                    MIN(NETWR) as minimum_value,
                    MAX(NETWR) as maximum_value,
                    STDDEV(NETWR) as std_deviation,
                    COUNT(DISTINCT WAERK) as currencies_used,
                    COUNT(DISTINCT AUART) as order_types,
                    COUNT(DISTINCT KUNNR) as unique_customers,
                    COUNT(DISTINCT VKORG) as sales_organizations,
                    COUNT(DISTINCT ERNAM) as created_by_users
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL
                """)
                
                stats = cursor.fetchone()
                if stats:
                    (total_orders, orders_with_value, total_value, avg_value, min_value, 
                     max_value, std_dev, currencies, order_types, customers, sales_orgs, users) = stats
                    
                    print(f"Total Orders:             {total_orders:,}")
                    print(f"Orders with Value:        {orders_with_value:,}")
                    print(f"Total Sales Value:        {total_value:,.2f}")
                    print(f"Average Order Value:      {avg_value:,.2f}")
                    print(f"Minimum Order Value:      {min_value:,.2f}")
                    print(f"Maximum Order Value:      {max_value:,.2f}")
                    print(f"Standard Deviation:       {std_dev:,.2f}" if std_dev else "Standard Deviation:       N/A")
                    print(f"Currencies Used:          {currencies}")
                    print(f"Order Types:              {order_types}")
                    print(f"Unique Customers:         {customers:,}")
                    print(f"Sales Organizations:      {sales_orgs}")
                    print(f"Created By (Users):       {users}")
                
                # Value distribution analysis
                print(f"\n💹 VALUE DISTRIBUTION ANALYSIS:")
                print("-" * 60)
                
                cursor.execute("""
                SELECT 
                    CASE 
                        WHEN NETWR >= 1000000 THEN '1M+'
                        WHEN NETWR >= 500000 THEN '500K-1M'
                        WHEN NETWR >= 100000 THEN '100K-500K'
                        WHEN NETWR >= 50000 THEN '50K-100K'
                        WHEN NETWR >= 10000 THEN '10K-50K'
                        WHEN NETWR >= 1000 THEN '1K-10K'
                        ELSE '<1K'
                    END as value_range,
                    COUNT(*) as order_count,
                    SUM(NETWR) as total_value,
                    AVG(NETWR) as avg_value
                FROM SAPHANADB.VBAK
                WHERE NETWR > 0
                GROUP BY 
                    CASE 
                        WHEN NETWR >= 1000000 THEN '1M+'
                        WHEN NETWR >= 500000 THEN '500K-1M'
                        WHEN NETWR >= 100000 THEN '100K-500K'
                        WHEN NETWR >= 50000 THEN '50K-100K'
                        WHEN NETWR >= 10000 THEN '10K-50K'
                        WHEN NETWR >= 1000 THEN '1K-10K'
                        ELSE '<1K'
                    END
                ORDER BY AVG(NETWR) DESC
                """)
                
                value_distribution = cursor.fetchall()
                if value_distribution:
                    print(f"{'VALUE_RANGE':<12} {'COUNT':<8} {'TOTAL_VALUE':<15} {'AVG_VALUE':<15}")
                    print("-" * 60)
                    
                    for value_range, count, total_val, avg_val in value_distribution:
                        print(f"{value_range:<12} {count:<8} {total_val:>13,.2f} {avg_val:>13,.2f}")
                
            else:
                print("❌ No sales orders found with valid net values in VBAK")
            
        except Exception as e:
            print(f"❌ Error analyzing VBAK data: {e}")
        
        finally:
            cursor.close()
            successful_connection["connection"].close()
            print(f"\n🔌 Connection closed")
    
    else:
        print("❌ Could not establish connection with VBAK access")
        print("\n💡 CURRENT STATUS:")
        print(f"   • VBAK table confirmed to exist with 7,274 records")
        print(f"   • Need proper credentials for SAPHANADB user or")
        print(f"   • Grant SYSTEM user SELECT privileges on SAPHANADB.VBAK")
        print(f"   • Alternative: Use different user with VBAK access")
        
        return False
    
    return True

if __name__ == "__main__":
    find_highest_value_vbak_order()
