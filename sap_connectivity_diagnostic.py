#!/usr/bin/env python3

"""
SAP Connectivity Diagnostic Tool
Comprehensive testing of SAP system connectivity options
"""

import socket
import requests
import urllib3
from urllib.parse import urlparse
import sys
import time

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_basic_connectivity():
    """Test basic network connectivity to SAP system"""
    print("🔍 Testing Basic Connectivity")
    print("=" * 40)
    
    sap_host = "98.83.112.225"
    sap_port = 30215
    
    try:
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((sap_host, sap_port))
        sock.close()
        
        if result == 0:
            print(f"✅ Basic TCP connection to {sap_host}:{sap_port} successful")
            return True
        else:
            print(f"❌ Cannot connect to {sap_host}:{sap_port}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_adt_endpoints():
    """Test common ADT (ABAP Development Tools) endpoints"""
    print("\n🔍 Testing ADT Endpoints")
    print("=" * 40)
    
    sap_host = "98.83.112.225"
    
    # Common ADT ports and paths
    test_configs = [
        {"port": 8000, "path": "/sap/bc/adt/discovery", "protocol": "http"},
        {"port": 8000, "path": "/sap/bc/adt/discovery", "protocol": "https"},
        {"port": 44300, "path": "/sap/bc/adt/discovery", "protocol": "http"},
        {"port": 44300, "path": "/sap/bc/adt/discovery", "protocol": "https"},
        {"port": 50000, "path": "/sap/bc/adt/discovery", "protocol": "http"},
        {"port": 50000, "path": "/sap/bc/adt/discovery", "protocol": "https"},
    ]
    
    successful_endpoints = []
    
    for config in test_configs:
        url = f"{config['protocol']}://{sap_host}:{config['port']}{config['path']}"
        print(f"📡 Testing: {url}")
        
        try:
            response = requests.get(
                url, 
                timeout=10, 
                verify=False,
                auth=('SYSTEM', 'Dilkyakare1234')
            )
            
            if response.status_code == 200:
                print(f"✅ ADT endpoint accessible: {url}")
                successful_endpoints.append(url)
            elif response.status_code == 401:
                print(f"🔐 ADT endpoint found but authentication failed: {url}")
                successful_endpoints.append(url)
            else:
                print(f"⚠️  ADT endpoint responded with status {response.status_code}: {url}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"⏱️  Timeout connecting to: {url}")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error to {url}: {str(e)[:100]}...")
        except Exception as e:
            print(f"❌ Error testing {url}: {str(e)[:100]}...")
    
    return successful_endpoints

def test_dns_resolution():
    """Test DNS resolution for common SAP hostnames"""
    print("\n🔍 Testing DNS Resolution")
    print("=" * 40)
    
    # Test if the IP resolves to any hostname
    sap_ip = "98.83.112.225"
    
    try:
        hostname = socket.gethostbyaddr(sap_ip)
        print(f"✅ Reverse DNS lookup successful: {sap_ip} -> {hostname[0]}")
        return hostname[0]
    except socket.herror:
        print(f"⚠️  No reverse DNS entry for {sap_ip}")
        return None
    except Exception as e:
        print(f"❌ DNS lookup error: {e}")
        return None

def test_sap_gui_connectivity():
    """Test SAP GUI style connectivity"""
    print("\n🔍 Testing SAP GUI Connectivity")
    print("=" * 40)
    
    sap_host = "98.83.112.225"
    
    # Common SAP GUI ports
    gui_ports = [3200, 3201, 3202, 3300, 3301, 3302]
    
    accessible_ports = []
    
    for port in gui_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((sap_host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ SAP GUI port {port} is accessible")
                accessible_ports.append(port)
            else:
                print(f"❌ SAP GUI port {port} is not accessible")
                
        except Exception as e:
            print(f"❌ Error testing port {port}: {e}")
    
    return accessible_ports

def generate_recommendations(basic_conn, adt_endpoints, dns_hostname, gui_ports):
    """Generate recommendations based on test results"""
    print("\n🎯 RECOMMENDATIONS")
    print("=" * 40)
    
    if not basic_conn:
        print("❌ CRITICAL: Basic connectivity failed")
        print("   • Check network connectivity")
        print("   • Verify SAP system is running")
        print("   • Check firewall settings")
        return
    
    if not adt_endpoints:
        print("⚠️  ADT endpoints not accessible")
        print("   • ADT services may not be enabled on SAP system")
        print("   • Try enabling ADT in SAP system (SICF transaction)")
        print("   • Check if different ports are used for ADT")
        
        if gui_ports:
            print("   • SAP GUI ports are accessible - system is running")
            print("   • Focus on ADT service configuration")
    
    if dns_hostname:
        print(f"✅ Use hostname in MCP configuration: {dns_hostname}")
    else:
        print("⚠️  Continue using IP address in configuration")
    
    print("\n💡 ALTERNATIVE APPROACHES:")
    print("   1. Use direct HANA database connection (already working)")
    print("   2. Configure SAP system for ADT access")
    print("   3. Use SAP RFC connections if available")
    print("   4. Consider SAP Cloud Connector if this is on-premise")

def main():
    """Main diagnostic function"""
    print("🔧 SAP Connectivity Diagnostic Tool")
    print("=" * 50)
    print("Testing connectivity to SAP system at 98.83.112.225")
    print()
    
    # Run all tests
    basic_conn = test_basic_connectivity()
    adt_endpoints = test_adt_endpoints()
    dns_hostname = test_dns_resolution()
    gui_ports = test_sap_gui_connectivity()
    
    # Generate recommendations
    generate_recommendations(basic_conn, adt_endpoints, dns_hostname, gui_ports)
    
    print("\n📋 SUMMARY")
    print("=" * 20)
    print(f"Basic connectivity: {'✅' if basic_conn else '❌'}")
    print(f"ADT endpoints found: {len(adt_endpoints)}")
    print(f"DNS hostname: {dns_hostname or 'None'}")
    print(f"SAP GUI ports accessible: {len(gui_ports)}")

if __name__ == "__main__":
    main()
