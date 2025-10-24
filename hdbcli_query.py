#!/usr/bin/env python3

from hdbcli import dbapi
import sys

# HANA connection parameters
host = '98.83.112.225'
port = 30015
user = 's4huser'
password = 'Dilkyakare1234'

sql_query = """
SELECT 
    SCHEMA_NAME,
    TABLE_NAME,
    RECORD_COUNT,
    ROUND(TABLE_SIZE/1024/1024, 2) AS SIZE_MB,
    RAW_RECORD_COUNT_IN_DELTA
FROM M_TABLES 
WHERE TABLE_TYPE = 'COLUMN' 
    AND RECORD_COUNT > 1000
    AND RAW_RECORD_COUNT_IN_DELTA > 0
ORDER BY RAW_RECORD_COUNT_IN_DELTA DESC
LIMIT 15
"""

try:
    print(f"Connecting to HANA at {host}:{port} with user {user}...")
    conn = dbapi.connect(address=host, port=port, user=user, password=password)
    cursor = conn.cursor()
    
    print("Executing query for fastest growing tables...")
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    print("\n=== FASTEST GROWING HANA TABLES ===")
    print(f"{'SCHEMA':<20} {'TABLE':<35} {'RECORDS':<12} {'SIZE_MB':<10} {'DELTA':<10}")
    print("-" * 90)
    
    for row in results:
        print(f"{row[0]:<20} {row[1]:<35} {row[2]:<12} {row[3]:<10} {row[4]:<10}")
    
    cursor.close()
    conn.close()
    print(f"\nFound {len(results)} tables with active growth")
    
except Exception as e:
    print(f"Connection error: {e}")
    print("Make sure HANA is running and accessible on the specified port")
