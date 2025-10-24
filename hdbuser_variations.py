#!/usr/bin/env python3
"""
Try different HDBUSER credential variations
Database: 98.83.112.225:30215 (Instance 02)
"""

import hdbcli.dbapi as hana_db
import sys

def try_hdbuser_variations():
    """Try different HDBUSER credential and connection variations"""
    
    host = "98.83.112.225"
    port = 30215
    
    # Different username/password combinations to try
    credential_variations = [
        {"user": "HDBUSER", "password": "Dilkyakare1234", "description": "HDBUSER with original password"},
        {"user": "hdbuser", "password": "Dilkyakare1234", "description": "lowercase hdbuser"},
        {"user": "HDBUSER", "password": "dilkyakare1234", "description": "HDBUSER with lowercase password"},
        {"user": "hdbuser", "password": "dilkyakare1234", "description": "Both lowercase"},
        {"user": "HDBUSER", "password": "Pass2025$", "description": "HDBUSER with system password"},
        {"user": "HDB", "password": "Dilkyakare1234", "description": "HDB user"},
        {"user": "SAPABAP1", "password": "Dilkyakare1234", "description": "SAPABAP1 user"},
    ]
    
    print("SAP HANA HDBUSER Connection Variations")
    print("=" * 60)
    print(f"Host: {host}:{port}")
    print()
    
    successful_connections = []
    
    for i, cred in enumerate(credential_variations, 1):
        username = cred["user"]
        password = cred["password"]
        description = cred["description"]
        
        print(f"🔄 Attempt {i}: {description}")
        print(f"   User: {username}")
        print(f"   Pass: {'*' * len(password)}")
        
        try:
            connection = hana_db.connect(
                address=host,
                port=port,
                user=username,
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
            
            successful_connections.append({
                "username": username,
                "password": password,
                "description": description,
                "connection": connection
            })
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            error_msg = str(e)
            if "authentication failed" in error_msg:
                print(f"   ❌ Authentication failed")
            elif "Connection refused" in error_msg:
                print(f"   ❌ Connection refused")
            elif "timeout" in error_msg.lower():
                print(f"   ❌ Timeout")
            else:
                print(f"   ❌ Error: {error_msg[:50]}...")
        
        print()
    
    if successful_connections:
        print(f"🎉 Found {len(successful_connections)} successful connection(s)!")
        
        # Use the first successful connection to test VBAK access
        best_connection = successful_connections[0]
        print(f"\n📊 Testing VBAK access with: {best_connection['description']}")
        
        try:
            connection = hana_db.connect(
                address=host,
                port=port,
                user=best_connection['username'],
                password=best_connection['password']
            )
            
            cursor = connection.cursor()
            
            # Test VBAK access
            cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            vbak_count = cursor.fetchone()[0]
            print(f"✅ VBAK access successful! Records: {vbak_count:,}")
            
            # Get highest value sales order
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
            LIMIT 1
            """)
            
            highest_order = cursor.fetchone()
            if highest_order:
                vbeln, erdat, auart, netwr, waerk, kunnr = highest_order
                print(f"\n🏆 HIGHEST VALUE SALES ORDER:")
                print(f"   Order Number: {vbeln}")
                print(f"   Net Value: {netwr:,.2f} {waerk}")
                print(f"   Date: {erdat}")
                print(f"   Customer: {kunnr}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"❌ VBAK access failed: {e}")
    
    else:
        print("❌ No successful connections found")
        print("\n🔧 Additional troubleshooting:")
        print("   1. HDBUSER might not exist in this SAP HANA system")
        print("   2. Password might be different")
        print("   3. User might be locked or expired")
        print("   4. Different authentication method might be required")
        
        # Check what users exist (if we can)
        print("\n🔍 Trying to check existing users with SYSTEM account...")
        try:
            connection = hana_db.connect(
                address=host,
                port=port,
                user="system",
                password="Dilkyakare1234"
            )
            
            cursor = connection.cursor()
            
            # Try to get user information
            cursor.execute("""
            SELECT USER_NAME, USER_DEACTIVATED, LAST_SUCCESSFUL_CONNECT
            FROM SYS.USERS 
            WHERE USER_NAME LIKE '%HDB%' OR USER_NAME LIKE '%SAP%'
            ORDER BY USER_NAME
            """)
            
            users = cursor.fetchall()
            if users:
                print("Found users with HDB or SAP in name:")
                for user_name, deactivated, last_connect in users:
                    status = "ACTIVE" if deactivated == 'FALSE' else "DEACTIVATED"
                    print(f"   {user_name}: {status}, Last connect: {last_connect}")
            else:
                print("No HDB/SAP users found")
                
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"   Cannot check users: {e}")

if __name__ == "__main__":
    try_hdbuser_variations()
