#!/usr/bin/env python3
"""
Create VBAK_READER user for full VBAK table access
Database: 98.83.112.225:30215 (Instance 02)
"""

import hdbcli.dbapi as hana_db

def create_vbak_reader_user():
    """Create VBAK_READER user with access to VBAK table"""
    
    host = "98.83.112.225"
    port = 30215
    username = "system"
    password = "Dilkyakare1234"
    
    try:
        print("🔧 CREATING VBAK_READER USER FOR FULL VBAK ACCESS")
        print("=" * 70)
        
        connection = hana_db.connect(address=host, port=port, user=username, password=password)
        cursor = connection.cursor()
        
        print("✅ Connected as SYSTEM user")
        
        # Create the VBAK_READER user
        print("\n👤 Creating VBAK_READER user...")
        
        try:
            cursor.execute("""
            CREATE USER VBAK_READER PASSWORD "VbakAccess123" NO FORCE_FIRST_PASSWORD_CHANGE
            """)
            print("✅ VBAK_READER user created successfully")
            
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️  VBAK_READER user already exists - continuing with grants...")
            else:
                print(f"❌ Error creating user: {e}")
                return False
        
        # Grant basic connection privilege
        print("\n🔐 Granting privileges...")
        
        try:
            cursor.execute("GRANT CONNECT TO VBAK_READER")
            print("✅ Granted CONNECT privilege")
        except Exception as e:
            print(f"⚠️  CONNECT grant: {e}")
        
        # Grant SELECT on VBAK table
        try:
            cursor.execute("GRANT SELECT ON SAPHANADB.VBAK TO VBAK_READER")
            print("✅ Granted SELECT on SAPHANADB.VBAK")
        except Exception as e:
            print(f"❌ VBAK grant failed: {e}")
        
        # Grant SELECT on VBAP (order items)
        try:
            cursor.execute("GRANT SELECT ON SAPHANADB.VBAP TO VBAK_READER")
            print("✅ Granted SELECT on SAPHANADB.VBAP")
        except Exception as e:
            print(f"❌ VBAP grant failed: {e}")
        
        # Grant SELECT on KNA1 (customer master)
        try:
            cursor.execute("GRANT SELECT ON SAPHANADB.KNA1 TO VBAK_READER")
            print("✅ Granted SELECT on SAPHANADB.KNA1")
        except Exception as e:
            print(f"❌ KNA1 grant failed: {e}")
        
        # Verify the grants
        print("\n🔍 Verifying granted privileges...")
        
        cursor.execute("""
        SELECT OBJECT_TYPE, SCHEMA_NAME, OBJECT_NAME, PRIVILEGE
        FROM SYS.GRANTED_PRIVILEGES 
        WHERE GRANTEE = 'VBAK_READER'
        ORDER BY OBJECT_NAME
        """)
        
        privileges = cursor.fetchall()
        if privileges:
            print(f"Found {len(privileges)} privileges for VBAK_READER:")
            for obj_type, schema, obj_name, privilege in privileges:
                print(f"   {privilege} on {schema}.{obj_name}")
        else:
            print("❌ No privileges found for VBAK_READER")
        
        # Test the new user connection
        print("\n🧪 Testing VBAK_READER connection...")
        
        try:
            test_connection = hana_db.connect(
                address=host,
                port=port,
                user="VBAK_READER",
                password="VbakAccess123"
            )
            
            test_cursor = test_connection.cursor()
            
            # Test VBAK access
            test_cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            vbak_count = test_cursor.fetchone()[0]
            
            print(f"✅ VBAK_READER can access VBAK table!")
            print(f"   VBAK records accessible: {vbak_count:,}")
            
            # Get the highest value sales order
            print(f"\n🏆 GETTING HIGHEST VALUE SALES ORDER FROM VBAK:")
            print("-" * 60)
            
            test_cursor.execute("""
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
            LIMIT 1
            """)
            
            highest_order = test_cursor.fetchone()
            
            if highest_order:
                vbeln, erdat, auart, netwr, waerk, kunnr, vkorg, ernam = highest_order
                
                print("🥇 HIGHEST VALUE SALES ORDER FROM VBAK:")
                print("=" * 70)
                print(f"💵 SALES ORDER VALUE:     {netwr:,.2f} {waerk}")
                print(f"📋 Sales Order Number:    {vbeln}")
                print(f"📅 Creation Date:         {erdat}")
                print(f"📝 Order Type:            {auart}")
                print(f"👤 Customer Number:       {kunnr}")
                print(f"🏢 Sales Organization:    {vkorg}")
                print(f"👨‍💼 Created By:            {ernam}")
                
                # Get top 5 for comparison
                print(f"\n📊 TOP 5 HIGHEST VALUE SALES ORDERS:")
                print("-" * 90)
                
                test_cursor.execute("""
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
                
                top_orders = test_cursor.fetchall()
                if top_orders:
                    print(f"{'RANK':<4} {'ORDER_NO':<12} {'DATE':<10} {'TYPE':<6} {'VALUE':<15} {'CURR':<4} {'CUSTOMER':<12}")
                    print("-" * 90)
                    
                    for rank, order in enumerate(top_orders, 1):
                        vbeln, erdat, auart, netwr, waerk, kunnr = order
                        print(f"{rank:<4} {vbeln:<12} {erdat:<10} {auart:<6} {netwr:>13,.2f} {waerk:<4} {kunnr:<12}")
                
                print(f"\n🎉 SUCCESS! VBAK_READER user can now access all VBAK data!")
                print(f"📋 Connection details:")
                print(f"   Username: VBAK_READER")
                print(f"   Password: VbakAccess123")
                print(f"   Database: {host}:{port}")
                
            else:
                print("❌ No sales orders found with valid values")
            
            test_cursor.close()
            test_connection.close()
            
        except Exception as e:
            print(f"❌ VBAK_READER connection test failed: {e}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_vbak_reader_user()
