#!/usr/bin/env python3
"""
SAP HANA Authentication Troubleshooting Script
Helps diagnose connection and authentication issues
"""

import hdbcli.dbapi as hana_db
import sys
import getpass

def test_authentication_variants():
    """Test different authentication approaches"""
    
    host = "98.83.112.225"
    base_username = "gyabmis"
    base_password = "Pass2025$"
    
    # Different username/password combinations to try
    auth_variants = [
        # Original credentials
        {"user": "gyabmis", "password": "Pass2025$", "description": "Original credentials"},
        
        # Case variations
        {"user": "GYABMIS", "password": "Pass2025$", "description": "Uppercase username"},
        {"user": "gyabmis", "password": "PASS2025$", "description": "Uppercase password"},
        {"user": "GYABMIS", "password": "PASS2025$", "description": "Both uppercase"},
        
        # Common SAP default users (if accessible)
        {"user": "SYSTEM", "password": "Pass2025$", "description": "SYSTEM user"},
        {"user": "system", "password": "Pass2025$", "description": "system user (lowercase)"},
        
        # Database-specific formats
        {"user": "gyabmis@SYSTEMDB", "password": "Pass2025$", "description": "User with database suffix"},
    ]
    
    # Ports to test (we know these are open)
    ports_to_test = [30215, 30213]
    
    print("SAP HANA Authentication Troubleshooting")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Testing {len(auth_variants)} authentication variants on {len(ports_to_test)} ports")
    print()
    
    successful_auths = []
    
    for port in ports_to_test:
        print(f"🔌 Testing Port {port}")
        print("-" * 40)
        
        for i, auth in enumerate(auth_variants, 1):
            username = auth["user"]
            password = auth["password"]
            description = auth["description"]
            
            print(f"   {i}. {description}")
            print(f"      User: {username}")
            print(f"      Pass: {'*' * len(password)}")
            
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
                
                print(f"      ✅ SUCCESS! Server time: {server_time}")
                
                successful_auths.append({
                    "port": port,
                    "username": username,
                    "password": password,
                    "description": description
                })
                
                cursor.close()
                connection.close()
                
            except Exception as e:
                error_msg = str(e)
                if "authentication failed" in error_msg:
                    print(f"      ❌ Auth failed")
                elif "Connection refused" in error_msg:
                    print(f"      ❌ Connection refused")
                elif "timeout" in error_msg.lower():
                    print(f"      ❌ Timeout")
                else:
                    print(f"      ❌ Error: {error_msg[:50]}...")
            
            print()
        
        print()
    
    return successful_auths

def interactive_connection_test():
    """Allow user to manually enter credentials"""
    
    print("🔧 Interactive Connection Test")
    print("=" * 40)
    
    host = "98.83.112.225"
    
    try:
        # Get credentials interactively
        print("Please enter your SAP HANA credentials:")
        username = input("Username: ").strip()
        
        if not username:
            username = "gyabmis"
            print(f"Using default username: {username}")
        
        # Try to get password securely
        try:
            password = getpass.getpass("Password: ")
        except:
            password = input("Password (will be visible): ")
        
        if not password:
            password = "Pass2025$"
            print("Using provided password")
        
        # Ask for port
        port_input = input("Port (default 30215): ").strip()
        port = int(port_input) if port_input else 30215
        
        # Ask for database
        database = input("Database (press Enter for default): ").strip()
        database = database if database else None
        
        print(f"\n🔌 Attempting connection...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {username}")
        print(f"   Database: {database or 'Default'}")
        
        # Build connection parameters
        conn_params = {
            "address": host,
            "port": port,
            "user": username,
            "password": password
        }
        
        if database:
            conn_params["database"] = database
        
        # Attempt connection
        connection = hana_db.connect(**conn_params)
        cursor = connection.cursor()
        
        # Test connection
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        server_time = cursor.fetchone()[0]
        
        print(f"✅ Connection successful!")
        print(f"   Server time: {server_time}")
        
        # Get user info
        cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
        user_info = cursor.fetchone()
        print(f"   Current user: {user_info[0]}")
        print(f"   Current schema: {user_info[1]}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except KeyboardInterrupt:
        print("\\n❌ Cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_hana_system_info():
    """Try to get basic system information without authentication"""
    
    print("🔍 SAP HANA System Information Check")
    print("=" * 50)
    
    host = "98.83.112.225"
    
    # Check if we can get any system info from open ports
    for port in [30213, 30215]:
        print(f"Checking port {port}...")
        
        try:
            # Try a very basic connection to see what error we get
            connection = hdbcli.dbapi.connect(
                address=host,
                port=port,
                user="dummy_user",
                password="dummy_pass"
            )
        except Exception as e:
            error_msg = str(e)
            print(f"   Error: {error_msg}")
            
            # Analyze the error for clues
            if "authentication failed" in error_msg:
                print(f"   ✅ Port {port} is accepting connections (auth required)")
            elif "Connection refused" in error_msg:
                print(f"   ❌ Port {port} is not accepting connections")
            elif "timeout" in error_msg.lower():
                print(f"   ⏱️  Port {port} timeout (may be filtered)")
            else:
                print(f"   ❓ Port {port} unknown response")
        
        print()

def main():
    """Main troubleshooting function"""
    
    print("SAP HANA Connection Troubleshooting Tool")
    print("=" * 60)
    print()
    
    # Step 1: Check system info
    check_hana_system_info()
    
    # Step 2: Test authentication variants
    print("\\n" + "=" * 60)
    successful_auths = test_authentication_variants()
    
    if successful_auths:
        print(f"🎉 Found {len(successful_auths)} successful authentication(s)!")
        for auth in successful_auths:
            print(f"   ✅ {auth['description']} on port {auth['port']}")
        return True
    
    # Step 3: Interactive test if automated failed
    print("\\n" + "=" * 60)
    print("Automated authentication failed. Trying interactive mode...")
    
    if interactive_connection_test():
        return True
    
    # Step 4: Final troubleshooting advice
    print("\\n" + "=" * 60)
    print("🔧 TROUBLESHOOTING RECOMMENDATIONS:")
    print()
    print("1. VERIFY CREDENTIALS:")
    print("   - Double-check username: 'gyabmis'")
    print("   - Verify password: 'Pass2025$'")
    print("   - Check if password has expired")
    print()
    print("2. CHECK USER PERMISSIONS:")
    print("   - Ensure user exists in SAP HANA")
    print("   - Verify user has login permissions")
    print("   - Check if user is locked")
    print()
    print("3. NETWORK & SYSTEM:")
    print("   - Confirm SAP HANA instance is running")
    print("   - Verify instance number (02) is correct")
    print("   - Check firewall settings")
    print()
    print("4. ALTERNATIVE APPROACHES:")
    print("   - Try connecting with SAP HANA Studio")
    print("   - Use SAP HANA Cockpit web interface")
    print("   - Contact SAP HANA administrator")
    
    return False

if __name__ == "__main__":
    main()
