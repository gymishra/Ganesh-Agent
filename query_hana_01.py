#!/usr/bin/env python3

from hdbcli import dbapi

def query_fastest_growing_tables():
    try:
        # Connect to HANA instance 01 on port 30115
        conn = dbapi.connect(
            address='98.83.112.225',
            port=30115,
            user='hdbuser',
            password='Dilkyakare1234'
        )
        
        cursor = conn.cursor()
        
        # Query fastest growing tables
        sql = """
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
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print("=== FASTEST GROWING HANA TABLES (Instance 01) ===")
        print(f"{'SCHEMA':<20} {'TABLE':<35} {'RECORDS':<12} {'SIZE_MB':<10} {'DELTA_RECORDS':<15}")
        print("-" * 95)
        
        for row in results:
            print(f"{row[0]:<20} {row[1]:<35} {row[2]:<12} {row[3]:<10} {row[4]:<15}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to instance 01: {e}")

if __name__ == "__main__":
    query_fastest_growing_tables()
