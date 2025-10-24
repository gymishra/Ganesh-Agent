#!/usr/bin/env python3
"""
SAP HANA Database Connection using HDBUSER
Database: 98.83.112.225:30215 (Instance 02)
User: HDBUSER
Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def connect_with_hdbuser():
    """Connect to SAP HANA using HDBUSER credentials and test access"""
    
    host = "98.83.112.225"
    port = 30215
    username = "HDBUSER"
    password = "Dilkyakare1234"
    
    connection = None
    
    try:
        print("🔌 Connecting to SAP HANA...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {username}")
        print(f"   Password: {'*' * len(password)}")
        
        # Establish connection
        connection = hana_db.connect(
            address=host,
            port=port,
            user=username,
            password=password
        )
        
        print("✅ Connection successful!")
        
        cursor = connection.cursor()
        
        # Get current timestamp and user info
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        current_time = cursor.fetchone()[0]
        print(f"   Server Time: {current_time}")
        
        cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
        user_info = cursor.fetchone()
        print(f"   Current User: {user_info[0]}")
        print(f"   Current Schema: {user_info[1]}")
        
        print("\n🔍 Testing HDBUSER access to VBAK table...")
        
        # Test access to VBAK table
        try:
            cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            vbak_count = cursor.fetchone()[0]
            print(f"✅ VBAK table access successful!")
            print(f"   Total VBAK records: {vbak_count:,}")
            
            # Now get the highest value sales order
            print(f"\n💰 Finding highest value sales order from VBAK...")
            
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
                ERNAM as created_by
            FROM SAPHANADB.VBAK
            WHERE NETWR IS NOT NULL AND NETWR > 0
            ORDER BY NETWR DESC
            LIMIT 1
            """)
            
            highest_order = cursor.fetchone()
            
            if highest_order:
                vbeln, erdat, auart, netwr, waerk, vkorg, vtweg, spart, kunnr, ernam = highest_order
                
                print("🏆 HIGHEST VALUE SALES ORDER:")
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
                
                # Get top 5 for comparison
                print(f"\n📊 TOP 5 HIGHEST VALUE SALES ORDERS:")
                cursor.execute("""
                SELECT 
                    VBELN,
                    ERDAT,
                    AUART,
                    NETWR,
                    WAERK,
                    KUNNR
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL AND NETWR > 0
                ORDER BY NETWR DESC
                LIMIT 5
                """)
                
                top_orders = cursor.fetchall()
                if top_orders:
                    print("-" * 80)
                    print(f"{'RANK':<4} {'ORDER_NO':<12} {'DATE':<10} {'TYPE':<6} {'VALUE':<15} {'CURR':<4} {'CUSTOMER':<12}")
                    print("-" * 80)
                    
                    for rank, order in enumerate(top_orders, 1):
                        vbeln, erdat, auart, netwr, waerk, kunnr = order
                        print(f"{rank:<4} {vbeln:<12} {erdat:<10} {auart:<6} {netwr:>13,.2f} {waerk:<4} {kunnr:<12}")
                
                # Get summary statistics
                print(f"\n📈 VBAK SALES STATISTICS:")
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(NETWR) as total_value,
                    AVG(NETWR) as average_value,
                    MIN(NETWR) as minimum_value,
                    MAX(NETWR) as maximum_value,
                    COUNT(DISTINCT WAERK) as currencies_used,
                    COUNT(DISTINCT AUART) as order_types,
                    COUNT(DISTINCT KUNNR) as unique_customers
                FROM SAPHANADB.VBAK
                WHERE NETWR IS NOT NULL AND NETWR > 0
                """)
                
                stats = cursor.fetchone()
                if stats:
                    total_orders, total_value, avg_value, min_value, max_value, currencies, order_types, customers = stats
                    print("-" * 50)
                    print(f"Total Orders:         {total_orders:,}")
                    print(f"Total Sales Value:    {total_value:,.2f}")
                    print(f"Average Order Value:  {avg_value:,.2f}")
                    print(f"Minimum Order Value:  {min_value:,.2f}")
                    print(f"Maximum Order Value:  {max_value:,.2f}")
                    print(f"Currencies Used:      {currencies}")
                    print(f"Order Types:          {order_types}")
                    print(f"Unique Customers:     {customers:,}")
                
            else:
                print("❌ No sales orders found with valid net values")
                
        except Exception as e:
            print(f"❌ Error accessing VBAK table: {e}")
            
            # Test what tables HDBUSER can access
            print(f"\n🔍 Checking HDBUSER table access permissions...")
            try:
                cursor.execute("""
                SELECT SCHEMA_NAME, TABLE_NAME, RECORD_COUNT
                FROM SYS.M_TABLES 
                WHERE SCHEMA_NAME IN ('SAPHANADB', 'SYSTEM')
                AND RECORD_COUNT > 0
                ORDER BY RECORD_COUNT DESC
                LIMIT 10
                """)
                
                accessible_tables = cursor.fetchall()
                if accessible_tables:
                    print("Top accessible tables:")
                    for schema, table, records in accessible_tables:
                        print(f"   {schema}.{table}: {records:,} records")
                        
            except Exception as e2:
                print(f"❌ Cannot check table permissions: {e2}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Troubleshooting suggestions for HDBUSER
        print(f"\n🔧 Troubleshooting suggestions for HDBUSER:")
        print(f"   1. Verify HDBUSER exists in SAP HANA")
        print(f"   2. Check if password 'Dilkyakare1234' is correct")
        print(f"   3. Confirm HDBUSER has necessary privileges")
        print(f"   4. Verify HDBUSER is not locked")
        print(f"   5. Check if HDBUSER has access to SAPHANADB schema")
        
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return True

if __name__ == "__main__":
    print("SAP HANA Database Connection - HDBUSER")
    print("=" * 60)
    connect_with_hdbuser()
