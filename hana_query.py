#!/usr/bin/env python3

import socket
import sys

def test_hana_connection():
    """Test connection to HANA database"""
    host = "98.83.112.225"
    port = 30015
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ HANA database is accessible at {host}:{port}")
            return True
        else:
            print(f"✗ Cannot connect to HANA at {host}:{port}")
            return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

def main():
    print("Testing HANA database connection...")
    
    if test_hana_connection():
        print("\nTo query fastest growing tables, you need to run this on the HANA server:")
        print("\nSQL Query:")
        print("""
SELECT 
    SCHEMA_NAME,
    TABLE_NAME,
    RECORD_COUNT,
    ROUND(TABLE_SIZE/1024/1024, 2) AS SIZE_MB,
    RAW_RECORD_COUNT_IN_DELTA,
    CASE 
        WHEN LAST_COMPRESSED_RECORD_COUNT > 0 
        THEN ROUND((RAW_RECORD_COUNT_IN_DELTA * 100.0 / LAST_COMPRESSED_RECORD_COUNT), 2)
        ELSE 0 
    END AS GROWTH_PERCENTAGE
FROM M_TABLES 
WHERE TABLE_TYPE = 'COLUMN' 
    AND RECORD_COUNT > 1000
    AND RAW_RECORD_COUNT_IN_DELTA > 0
ORDER BY RAW_RECORD_COUNT_IN_DELTA DESC
LIMIT 15;
        """)
    else:
        print("Please check if:")
        print("1. HANA database is running")
        print("2. Port 30015 is open")
        print("3. Network connectivity is available")

if __name__ == "__main__":
    main()
