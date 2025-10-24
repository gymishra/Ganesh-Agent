#!/usr/bin/env python3

from hdbcli import dbapi

def query_fastest_growing_tables():
    try:
        # Connect to HANA on port 30013 (system database)
        conn = dbapi.connect(
            address='98.83.112.225',
            port=30013,
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
        LIMIT 15
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print("=== FASTEST GROWING HANA TABLES (Port 30013) ===")
        print(f"{'SCHEMA':<20} {'TABLE':<30} {'RECORDS':<10} {'SIZE_MB':<10} {'DELTA':<10} {'GROWTH%':<8}")
        print("-" * 100)
        
        for row in results:
            print(f"{row[0]:<20} {row[1]:<30} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<8}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error on port 30013: {e}")

if __name__ == "__main__":
    query_fastest_growing_tables()
